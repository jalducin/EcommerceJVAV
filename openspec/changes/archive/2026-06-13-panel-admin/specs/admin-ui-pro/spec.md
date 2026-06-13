## ADDED Requirements

### Requirement: Tema metálico data-driven desde store-config

La UI de administración SHALL aplicar el tema visual (colores y fuentes) mediante CSS Custom Properties cargadas desde `GET /api/config` (store-config), sin hardcodear colores en el código, de modo que el mismo panel se adapte a la marca configurada. No SHALL usar frameworks JS ni CSS.

#### Scenario: Tema cargado desde la configuración

- **WHEN** el panel se carga y obtiene la configuración de tienda
- **THEN** los tokens de tema (colores, fuentes) se aplican vía CSS Custom Properties
- **AND** ningún color queda hardcodeado en el código

#### Scenario: Sin frameworks

- **WHEN** se revisa el código del panel
- **THEN** no incluye React, Vue, Angular, Bootstrap ni Tailwind
- **AND** usa HTML5, CSS3 y JavaScript vanilla

### Requirement: Diseño responsive en los tres breakpoints

El panel SHALL ser responsive y usable en los breakpoints 375px, 768px y 1280px, con un layout mobile-first que reorganice navegación, tablas y formularios sin pérdida de contenido ni scroll horizontal.

#### Scenario: Vista en móvil 375px

- **WHEN** el panel se muestra a 375px de ancho
- **THEN** la navegación y las tablas se adaptan sin scroll horizontal
- **AND** los controles permanecen accesibles

#### Scenario: Vista en escritorio 1280px

- **WHEN** el panel se muestra a 1280px de ancho
- **THEN** aprovecha el ancho con un layout de varias columnas legible
- **AND** mantiene la jerarquía visual

### Requirement: Estados de carga, vacío y error

Cada vista del panel SHALL representar de forma explícita los estados de carga, vacío y error al consumir el API, de modo que el admin nunca vea una pantalla en blanco ni datos a medio renderizar.

#### Scenario: Carga de datos

- **WHEN** una vista está esperando la respuesta del API
- **THEN** muestra un indicador de carga accesible
- **AND** lo reemplaza por los datos o por un estado de error al resolverse

#### Scenario: Error del API

- **WHEN** una llamada al API falla
- **THEN** la vista muestra un mensaje de error con opción de reintentar
- **AND** no deja datos parciales en pantalla

### Requirement: Accesibilidad del panel

El panel SHALL cumplir requisitos de accesibilidad básicos: todos los campos con `label` asociado, atributos `aria` en componentes interactivos y controles dinámicos, y contraste de color suficiente entre texto y fondo.

#### Scenario: Formulario accesible

- **WHEN** se navega un formulario del panel con teclado o lector de pantalla
- **THEN** cada campo tiene su `label` asociado y los estados de error se anuncian vía `aria`
- **AND** el contraste entre texto y fondo cumple el mínimo de legibilidad
