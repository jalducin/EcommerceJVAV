from pathlib import Path

from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from pydantic import EmailStr

from ..config import settings
from ..schemas.order import OrderDetail

# Configuración de email desde settings
conf = ConnectionConfig(
    MAIL_USERNAME=settings.SMTP_USER,
    MAIL_PASSWORD=settings.SMTP_PASSWORD,
    MAIL_FROM=settings.EMAILS_FROM,
    MAIL_PORT=settings.SMTP_PORT or 587,
    MAIL_SERVER=settings.SMTP_HOST,
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
    TEMPLATE_FOLDER=Path(__file__).parent.parent / "templates",
)

fm = FastMail(conf)


async def send_order_confirmation_email(email_to: EmailStr, order: OrderDetail):
    """Envía un email de confirmación de pedido."""
    if not all([settings.SMTP_HOST, settings.SMTP_USER, settings.SMTP_PASSWORD, settings.EMAILS_FROM]):
        print("WARN: Faltan variables de entorno de SMTP. No se enviará el email de confirmación.")
        return

    template_body = {
        "order_id": order.id,
        "total": f"{order.total:.2f}",
        "created_at": order.created_at.strftime("%d/%m/%Y %H:%M"),
        "items": order.items,
        "shipping_address": order.shipping_address,
        "frontend_url": settings.FRONTEND_URL,
    }

    message = MessageSchema(
        subject=f"MetalShop - Confirmación de tu pedido #{order.id}",
        recipients=[email_to],
        template_body=template_body,
        subtype=MessageType.html,
    )

    try:
        await fm.send_message(message, template_name="order_confirmation.html")
        print(f"Email de confirmación enviado a {email_to} para el pedido #{order.id}")
    except Exception as e:
        print(f"ERROR: No se pudo enviar el email de confirmación a {email_to}. Error: {e}")