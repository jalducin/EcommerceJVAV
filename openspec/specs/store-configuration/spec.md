# store-configuration Specification

## Purpose
TBD - created by archiving change migrate-to-serverless-aws. Update Purpose after archive.
## Requirements
### Requirement: Configuración de tienda business-agnostic

La tienda SHALL ser configurable para cualquier tipo de negocio sin cambios de código. Una
**configuración de tienda** SHALL definir, como mínimo: nombre/marca, logo, lista de categorías, moneda,
locale/idioma, reglas de impuesto y de envío, y los tokens de tema visual (colores y fuentes). Cambiar de
vertical SHALL requerir únicamente cambiar la configuración (y, opcionalmente, el dataset), nunca
recompilar ni editar lógica de negocio.

#### Scenario: La API expone la configuración de tienda

- **WHEN** el frontend solicita `GET /api/config`
- **THEN** la respuesta incluye marca, categorías, moneda, locale, reglas de impuesto/envío y tokens de tema
- **AND** el frontend usa esos valores para renderizarse, sin valores hardcodeados de un vertical

#### Scenario: Cambiar de negocio sin tocar código

- **WHEN** se reemplaza la configuración por la de otro negocio (p. ej. de "ropa/tenis" a "electrónica")
- **THEN** la tienda muestra la nueva marca, categorías, moneda y tema
- **AND** no se modifica ningún archivo de código backend ni frontend

### Requirement: Categorías y reglas de cálculo dirigidas por configuración

Las categorías del catálogo y las reglas de cálculo de impuesto y envío SHALL leerse de la configuración
de tienda. El cálculo de totales del carrito/checkout SHALL aplicar la moneda, el impuesto y el envío
definidos en la configuración vigente.

#### Scenario: Cálculo de totales según configuración

- **WHEN** se calcula el total de un carrito con una configuración que define impuesto 16% y envío fijo
- **THEN** el subtotal, impuesto y envío se calculan con esos valores
- **AND** los importes se presentan en la moneda configurada

#### Scenario: Categoría inválida rechazada

- **WHEN** se intenta crear un producto con una categoría que no existe en la configuración
- **THEN** la API responde `422` indicando categoría inválida

### Requirement: Marca renderizada desde la configuración en el frontend

El frontend SHALL renderizar el nombre/marca de la tienda a partir de `GET /api/config`
(elementos `data-store-name`), sin texto fijo de un vertical específico en el hero ni el
footer. La marca por defecto es "JV Market" y cambiarla es solo configuración.

#### Scenario: La tienda muestra la marca de la configuración

- **WHEN** se carga el storefront con la configuración por defecto
- **THEN** el hero/navbar/footer muestran "JV Market"
- **AND** no aparece copy fijo de herramientas/acero de un vertical concreto

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

