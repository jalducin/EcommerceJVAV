# admin-auth-ui Specification

## Purpose
TBD - created by archiving change panel-admin. Update Purpose after archive.
## Requirements
### Requirement: Login de administrador en la UI

La UI de administración SHALL ofrecer un formulario de login que autentique contra `POST /api/auth/login`, almacene los tokens JWT (access y refresh) en localStorage y refresque el access token de forma automática al expirar.

#### Scenario: Login exitoso de un admin

- **WHEN** un usuario con rol admin envía credenciales válidas en el formulario de login
- **THEN** la UI guarda el access token y el refresh token en localStorage
- **AND** redirige al dashboard de administración

#### Scenario: Credenciales inválidas

- **WHEN** se envían credenciales incorrectas
- **THEN** la UI muestra un mensaje de error accesible sin exponer detalles del backend
- **AND** no almacena ningún token

### Requirement: Guard de las vistas de administración

Las vistas de administración SHALL exigir un usuario con rol `admin` y, si el usuario no es admin o no está autenticado, redirigir al login o mostrar un estado 403, sin renderizar datos protegidos. El guard de UI es defensa en profundidad: la autoridad real es `require_admin` en el backend.

#### Scenario: Usuario sin sesión accede a una vista admin

- **WHEN** un usuario sin token válido abre una vista de administración
- **THEN** la UI lo redirige al formulario de login
- **AND** no realiza llamadas a endpoints admin con un token ausente

#### Scenario: Usuario autenticado pero sin rol admin

- **WHEN** un usuario autenticado sin rol admin intenta abrir una vista admin
- **THEN** un endpoint admin responde 403 y la UI muestra un estado de "acceso denegado"
- **AND** no renderiza datos de administración

#### Scenario: Token expirado se refresca de forma transparente

- **WHEN** el access token expira durante el uso del panel y existe un refresh token válido
- **THEN** la UI obtiene un nuevo access token vía `POST /api/auth/refresh`
- **AND** reintenta la llamada original sin expulsar al usuario

### Requirement: Redirección de sesión no administradora al panel

El guard del panel SHALL redirigir a la página de login (con `next` a la ruta admin) cuando
una sesión autenticada NO sea de administrador (p. ej. un cliente), permitiendo iniciar sesión
como admin. NO SHALL dejar al usuario en una página admin sin estilos ni datos.

#### Scenario: Cliente intenta entrar al panel

- **WHEN** un usuario con rol `client` abre `/admin/dashboard.html`
- **THEN** se le redirige a `/login.html?next=/admin/dashboard.html`
- **AND** tras iniciar sesión como admin regresa al panel

