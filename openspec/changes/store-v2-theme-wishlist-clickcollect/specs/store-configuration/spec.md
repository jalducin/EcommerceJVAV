## MODIFIED Requirements

### Requirement: Tema visual configurable con azul metálico por defecto

Los tokens de tema (colores, fuentes) SHALL provenir de la configuración de tienda y aplicarse vía CSS
Custom Properties. El tema por defecto SHALL ser una paleta **azul metálico** suave y profesional (azul
de marca, azul acero, azul acento, superficie clara y texto de alto contraste), con contraste suficiente
para accesibilidad básica. La tienda SHALL seguir siendo configurable: sobrescribir `theme` en la
configuración cambia la paleta sin recompilar ni editar lógica. NO SHALL introducirse frameworks CSS, y
los nombres de los tokens SHALL mantenerse estables (se redefine su valor, no su nombre).

#### Scenario: Tema azul metálico por defecto

- **WHEN** no se sobrescribe la configuración de tema
- **THEN** la tienda usa la paleta azul metálico por defecto definida en `css/variables.css`
- **AND** los colores se aplican vía CSS Custom Properties, sin frameworks ni colores hardcodeados

#### Scenario: Tema sobrescrito por configuración

- **WHEN** la configuración define una paleta distinta a la azul metálico por defecto
- **THEN** el frontend aplica esos tokens mediante CSS Custom Properties sin recompilar
- **AND** una tienda que ya sobrescribe el tema conserva su propia paleta

### Requirement: Ubicaciones de recogida en la configuración de tienda

La configuración de tienda SHALL poder declarar una lista de **ubicaciones de recogida**
(`pickup_locations`), cada una con al menos un identificador (`id`), un nombre (`name`) y una dirección
(`address`), y opcionalmente horarios (`hours`). Estas ubicaciones SHALL exponerse en `GET /api/config`
para que el checkout ofrezca la opción de recoger en tienda. Una tienda sin ubicaciones declaradas SHALL
devolver una lista vacía (no un error) y, en ese caso, la opción de recoger en tienda no SHALL ofrecerse.

#### Scenario: La API expone las ubicaciones de recogida

- **WHEN** el frontend solicita `GET /api/config` en una tienda con ubicaciones de recogida configuradas
- **THEN** la respuesta incluye `pickup_locations` con el `id`, `name` y `address` de cada ubicación
- **AND** el checkout usa esa lista para ofrecer la opción de recoger en tienda

#### Scenario: Tienda sin ubicaciones de recogida

- **WHEN** la configuración no declara ninguna ubicación de recogida
- **THEN** `GET /api/config` devuelve `pickup_locations` como lista vacía, no un error
- **AND** el checkout no ofrece la opción de recoger en tienda
