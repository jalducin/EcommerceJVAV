# frontend-enhancements Specification

## Purpose
TBD - created by archiving change migrate-to-serverless-aws. Update Purpose after archive.
## Requirements
### Requirement: Navegación por categorías dirigida por configuración

El storefront SHALL mostrar la navegación por categorías a partir de las categorías de la configuración
de tienda (no listas hardcodeadas). Seleccionar una categoría SHALL filtrar el catálogo por ella.

#### Scenario: Render de categorías desde config

- **WHEN** se carga el catálogo con la configuración por defecto (ropa/tenis)
- **THEN** la navegación muestra las categorías definidas en la configuración
- **AND** al elegir "tenis" el listado muestra solo productos de esa categoría

### Requirement: Selector de variante genérico

La página de detalle de producto SHALL renderizar un selector de variante **genérico** que se adapte a
los atributos que cada producto declare (p. ej. talla y/o color), sin asumir un atributo fijo. NO SHALL
permitir agregar al carrito una variante sin stock.

#### Scenario: Selección de talla y color

- **WHEN** se abre un producto con variantes de talla y color
- **THEN** se muestran selectores para cada atributo presente
- **AND** agregar al carrito requiere elegir una combinación válida con stock

#### Scenario: Variante agotada no seleccionable

- **WHEN** una combinación de variante tiene stock 0
- **THEN** esa opción aparece deshabilitada o marcada como agotada
- **AND** el botón de agregar al carrito permanece bloqueado para esa combinación

### Requirement: Galería de producto y estados de UI

El detalle de producto SHALL incluir una galería de imágenes. El catálogo y el detalle SHALL manejar
explícitamente los estados de **carga**, **vacío** y **error** (sin pantallas en blanco). Todo sin
introducir frameworks JS/CSS.

#### Scenario: Estado de carga y vacío

- **WHEN** el catálogo está cargando o un filtro no devuelve resultados
- **THEN** se muestra un indicador de carga o un mensaje de "sin resultados" respectivamente

#### Scenario: Estado de error de API

- **WHEN** una llamada a la API falla
- **THEN** se muestra un mensaje de error accionable, no una pantalla en blanco ni un error de consola sin manejar

### Requirement: Accesibilidad y responsive

El storefront SHALL cumplir prácticas básicas de accesibilidad (labels en formularios, `aria-label` donde
aplique, contraste suficiente) y SHALL verse correctamente en los breakpoints 375px, 768px y 1280px
(mobile-first), reutilizando las variables de `css/variables.css`.

#### Scenario: Responsive en tres breakpoints

- **WHEN** se visualiza el catálogo y el detalle en 375px, 768px y 1280px
- **THEN** el layout se adapta sin desbordes ni solapamientos
- **AND** los controles principales son usables con teclado y lector de pantalla

