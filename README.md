# Calculadora de factura de energia - energy_invoice_calculator

Esta API permite realizar cálculos y obtener información relacionada con facturas de energía. Incluye la capacidad de calcular conceptos como Energía Activa (EA), Excedentes de Energía tipo 1 (EE1), Excedentes de Energía tipo 2 (EE2), y Comercialización de Excedentes de Energía (EC), así como proporcionar estadísticas de consumo e inyección de energía.
Se espera que este sistema sea escalable, fácil de mantener, y permita la integración con otras herramientas de análisis y procesamiento de datos.

## Requisitos Previos

- Python 3.10+
- PostgreSQL 
- Instalar dependencias:
  `pip install -r requirements.txt`

## Configuración

Clonar el repositorio: 
`git clone https://[github.com/tu_usuario/energy_invoice_calculator.git](https://github.com/jeancajr/energy_invoice_calculator.git)
    cd energy_invoice_calculator`
    
Configurar la base de datos usando el archivo energybd.sql.
Configurar la conexión a la base de datos en el archivo conexionbd.py.

## Ejecutar el Proyecto

Ejecutar FastAPI: `uvicorn main:app --reload`
La API estará disponible en http://127.0.0.1:8000.

## Documentacion de API


### POST /calculate-invoice/
Calcula los conceptos de una factura de energía para un cliente en un mes específico. Los cálculos incluyen Energía Activa (EA), Excedentes de Energía tipo 1 (EE1), Excedentes de Energía tipo 2 (EE2) y Comercialización de Excedentes de Energía (EC).
#### Request:
- URL: /calculate-invoice/
- Método: POST
- Body JSON:
          `{
            "client_id": -,
            "month": -,
            "year": -
          }`
#### Parámetros:
- client_id: (int) Identificador único del cliente.
- month: (int) El mes para el cual se quiere calcular la factura (1-12).
- year: (int) El año del mes específico.
Response:
          `{
            "EA": -,
            "EC": -,
            "EE1": -,
            "EE2": -,
            "invoice_total": -
          }`
#### Descripción de la Respuesta:
- EA: Energía Activa en Kwh multiplicada por la tarifa CU.
- EC: Comercialización de Excedentes en Kwh multiplicada por la tarifa C.
- EE1: Excedentes de Energía tipo 1 en Kwh multiplicada por la tarifa CU negativa.
- EE2: Excedentes de Energía tipo 2 en Kwh multiplicada por la tarifa hora a hora.
- invoice_total: Total de la factura sumando EA, EC, EE1 y EE2.

#### Códigos de Estado:
- 200 OK: Si el cálculo fue exitoso.
- 400 Bad Request: Si los parámetros de la solicitud son incorrectos o están incompletos.
- 404 Not Found: Si no se encuentra el cliente especificado.
Ejemplo de Error:
                  `{
                    "detail": "Client not found"
                  }`


### GET /client-statistics/{client_id}
Proporciona estadísticas de consumo e inyección de energía para un cliente específico.

#### Request:
- URL: /client-statistics/{client_id}
- Método: GET
- Path Parameters:
  client_id: (int) Identificador único del cliente.
Response:
        `{
          "client_id": -,
          "total_consumption_kwh": -,
          "total_injection_kwh": -,
          "last_update": "2024-09-17T14:53:00"
        }`
#### Descripción de la Respuesta:
- client_id: ID del cliente.
- total_consumption_kwh: Energía consumida en Kwh.
- total_injection_kwh: Energía inyectada en Kwh.
- last_update: Última fecha y hora en la que se actualizaron los datos.

#### Códigos de Estado:
- 200 OK: Si la solicitud fue exitosa.
- 404 Not Found: Si no se encuentra el cliente especificado.
Ejemplo de Error:
                `{
                  "detail": "Client with ID 999 not found"
                }`


### GET /system-load/
Muestra la carga del sistema por hora, basada en los datos de consumo de energía de todos los clientes.

#### Request:
- URL: /system-load/
- Método: GET
- Response:
          `{
            "hourly_load": {
              "2024-09-17T08:00:00": -,
              "2024-09-17T09:00:00": -,
              "2024-09-17T10:00:00": -,
              "2024-09-17T11:00:00": -
            }
          }`
#### Descripción de la Respuesta:
- hourly_load: Diccionario con los registros de la carga del sistema, donde las llaves son las horas y los valores son la carga en Kwh.

#### Códigos de Estado:
- 200 OK: Si la solicitud fue exitosa.
- 500 Internal Server Error: Si ocurre un problema con la base de datos o la lógica de cálculo.


### GET /calculate-concept/{concept}/{client_id}
Calcula un concepto específico (EA, EC, EE1, o EE2) para un cliente dado.

#### Request:
- URL: /calculate-concept/{concept}/{client_id}
- Método: GET
- Path Parameters:
  - concept: (string) El concepto que se quiere calcular (EA, EC, EE1, EE2).
  - client_id: (int) Identificador único del cliente.
Response:
        `{
          "client_id": -,
          "concept": "-",
          "value": -
        }`
#### Descripción de la Respuesta:
- client_id: ID del cliente.
- concept: El concepto calculado (EA, EC, EE1, EE2).
- value: El valor calculado del concepto en Kwh multiplicado por la tarifa correspondiente.

#### Códigos de Estado:
- 200 OK: Si la solicitud fue exitosa.
- 400 Bad Request: Si el concepto no es válido.
- 404 Not Found: Si no se encuentra el cliente especificado.
Ejemplo de Error:
                `{
                  "detail": "Invalid concept. Must be one of 'EA', 'EC', 'EE1', 'EE2'"
                }`


### GET /health-check/
Verifica si la API está funcionando correctamente.

#### Request:
- URL: /health-check/
- Método: GET
- Response:
          `{
            "status": "API is running",
            "timestamp": "2024-09-17T14:53:00"
          }`
#### Descripción de la Respuesta:
- status: Indica que la API está en funcionamiento.
- timestamp: Hora actual del servidor.

#### Códigos de Estado:
- 200 OK: Si la API está funcionando.

### Manejo de Errores Generales:
En caso de que ocurran errores en cualquier endpoint, se seguirá el formato estándar de respuesta de error en JSON:
`{
  "detail": "Mensaje de error"
}`

- 400 Bad Request: Si la solicitud es inválida o está malformada.
- 404 Not Found: Si un recurso solicitado (como un cliente) no se encuentra.
- 500 Internal Server Error: Ocurre un error en el servidor (por ejemplo, un problema de conexión con la base de datos).


## Decisiones de diseño

### Uso de FastAPI para la API (Solicitado)
Se eligió FastAPI por sus siguientes características:
- Simplicidad y rendimiento: FastAPI es una opción moderna y eficiente para construir APIs RESTful. 
- Documentación automática: FastAPI genera automáticamente la documentación de la API con Swagger y ReDoc.

### Elección de PostgreSQL como base de datos (Solicitado)
- PostgreSQL fue la base de datos seleccionada debido a su robustez, flexibilidad y compatibilidad con las operaciones SQL que requiere el proyecto.
- Maneja de manera eficiente grandes volúmenes de datos relacionados con las facturas de los clientes.

### Conexión a PostgreSQL con psycopg2.
- Se optó por psycopg2 para conexiones rápidas y control completo sobre las consultas SQL, 

### Estructura modular
- El proyecto está diseñado de forma modular, con un archivo para la conexión a la base de datos (conexionbd.py), uno para los calculos (calculos_factura.py), y uno para los endpoints principales (main.py). Esta estructura facilita futuras expansiones y modificaciones, así como el posible trabajo colaborativo entre diferentes desarrolladores.

### Gestión de errores
- En los endpoints, se implementó un manejo de excepciones utilizando HTTPException de FastAPI para asegurar que, en caso de errores durante el proceso de cálculo o consulta de la base de datos, se devuelva un mensaje claro al cliente. Esto también previene que fallas inesperadas generen errores genéricos que podrían confundir a los usuarios de la API.

## Posibles Mejoras
### Optimización de Consultas SQL
- A medida que el sistema crezca y maneje más datos, las consultas SQL para calcular el consumo y las estadísticas podrían optimizarse utilizando técnicas como la creación de índices en las tablas más consultadas o el uso de vistas materializadas. Esto para reducir el tiempo de respuesta en grandes volúmenes de datos.

### Escalabilidad y Arquitectura de Microservicios
- Ya que la aplicacion es un proyecto "pequeño", a medida que se integre con más sistemas o maneje mayores volúmenes de datos, sería beneficioso migrar hacia una arquitectura de microservicios, donde cada parte del sistema (facturación, estadísticas, etc.) funcione como un servicio independiente.

### Seguridad y Autenticación
- Para un ambiente de producción, sería esencial agregar autenticación y autorización a la API.

### Soporte de Multilingüa y Localización
- A futuro, el sistema podría expandirse para soportar diferentes idiomas y configuraciones regionales. Esto incluiría la localización de formatos de fecha, moneda, y unidades de medida, permitiendo que la API sea útil en diferentes regiones y mercados.
