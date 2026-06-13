## ADDED Requirements

### Requirement: Cargador de datos idempotente

Un cargador de datos (`seed_dynamodb.py`) SHALL sembrar un dataset en la tabla DynamoDB y SHALL ser
**idempotente**: ejecutarlo varias veces NO SHALL crear duplicados ni corromper datos existentes.
Reemplaza a `seed_products.py`.

#### Scenario: Sembrado inicial

- **WHEN** se ejecuta el cargador sobre una tabla vacía
- **THEN** se crean los productos del dataset, sus variantes y un usuario admin de ejemplo
- **AND** el catálogo queda navegable

#### Scenario: Re-ejecución sin duplicar

- **WHEN** se vuelve a ejecutar el cargador sobre una tabla ya sembrada
- **THEN** los items existentes se mantienen o actualizan por clave
- **AND** no se crean registros duplicados

### Requirement: Dataset demo intercambiable de ropa y tenis (por defecto)

El dataset por defecto SHALL ser un catálogo realista de **streetwear y tenis** (ropa + sneakers) con
categorías, imágenes, precios y **variantes** (p. ej. tallas/colores). El cargador SHALL aceptar un
dataset alternativo (otro vertical) sin cambios de código, alineado con `store-configuration`.

#### Scenario: Dataset por defecto de ropa/tenis

- **WHEN** se ejecuta el cargador sin especificar dataset
- **THEN** se siembra el catálogo de ropa/tenis con variantes de talla/color
- **AND** las categorías sembradas coinciden con las de la configuración por defecto

#### Scenario: Dataset alternativo

- **WHEN** se ejecuta el cargador indicando otro dataset (p. ej. electrónica)
- **THEN** se siembra ese catálogo con sus propias categorías y atributos de variante
- **AND** no se modifica código de la aplicación

### Requirement: Migración de los datos dummy existentes

Los datos de prueba previos (basados en `seed_products.py`/SQLite) SHALL quedar reemplazados por el nuevo
dataset en DynamoDB. NO SHALL permanecer dependencia de la base relacional para datos de ejemplo.

#### Scenario: Datos previos no requeridos

- **WHEN** la tienda corre sobre DynamoDB con el nuevo cargador
- **THEN** el catálogo proviene del dataset DynamoDB
- **AND** no se requiere ninguna base SQLite/PostgreSQL para los datos demo
