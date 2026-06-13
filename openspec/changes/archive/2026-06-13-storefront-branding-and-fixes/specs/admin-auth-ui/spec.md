## ADDED Requirements

### Requirement: Redirección de sesión no administradora al panel

El guard del panel SHALL redirigir a la página de login (con `next` a la ruta admin) cuando
una sesión autenticada NO sea de administrador (p. ej. un cliente), permitiendo iniciar sesión
como admin. NO SHALL dejar al usuario en una página admin sin estilos ni datos.

#### Scenario: Cliente intenta entrar al panel

- **WHEN** un usuario con rol `client` abre `/admin/dashboard.html`
- **THEN** se le redirige a `/login.html?next=/admin/dashboard.html`
- **AND** tras iniciar sesión como admin regresa al panel
