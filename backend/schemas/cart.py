from pydantic import BaseModel, ConfigDict, field_validator


class CartItemCreate(BaseModel):
    product_id: int
    quantity: int = 1

    @field_validator("quantity")
    @classmethod
    def qty_positive(cls, v: int) -> int:
        if v < 1:
            raise ValueError("La cantidad debe ser al menos 1")
        return v


class CartItemUpdate(BaseModel):
    quantity: int

    @field_validator("quantity")
    @classmethod
    def qty_positive(cls, v: int) -> int:
        if v < 1:
            raise ValueError("La cantidad debe ser al menos 1")
        return v


class CartProductInfo(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    price: float
    stock: int
    images: list[str] | None


class CartItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    product_id: int
    quantity: int
    product: CartProductInfo


class CartResponse(BaseModel):
    items: list[CartItemResponse]
    subtotal: float
    total: float
    item_count: int


class CartSyncItem(BaseModel):
    product_id: int
    quantity: int


class CartSyncRequest(BaseModel):
    items: list[CartSyncItem]
