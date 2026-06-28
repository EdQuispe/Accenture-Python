# Accenture Python ETL

Proyecto ETL en Python para extraer, transformar y cargar información operativa hacia SQL Server.

El proceso integra datos provenientes de:

- un servidor FTP con archivos de `atenciones` y `tickets`
- un archivo de detalle alojado en Google Drive
- archivos locales descargados y normalizados con `pandas`

Luego, los datos se cargan en SQL Server en un modelo de tipo datamart con tablas de dimensiones y una tabla de hechos.

## Objetivo

Automatizar la construcción de un datamart a partir de archivos heterogéneos, estandarizando formatos, unificando claves y cargando la información de forma incremental o histórica según la tabla destino.

## Flujo general

1. Se descargan archivos desde FTP:
   - `atenciones` en formato JSON
   - `tickets` en formato CSV/TXT
2. Se descarga el archivo `Agencias.xlsx` desde Google Drive.
3. Se transforman los datasets:
   - normalización de columnas
   - limpieza de tipos
   - estandarización de texto
   - conversión de fechas y montos
   - deduplicación por clave de negocio
4. Se construyen los dataframes finales:
   - `df_proveedor`
   - `df_item`
   - `df_agencias`
   - `df_fact_atenciones`
5. Se cargan los datos en SQL Server:
   - Se cuenta con la opción de carga histórica para las tablas de dimensiones y hechos.
   - En las dimensiones se ha implementado también la actualización con SCD Tipo 1.
   - La tabla fact tiene la opción de actualización incremental filtrada por ventana temporal
6. Se mantiene una gestión de logs para registrar el inicio, avance, errores y cierre de cada ejecución.

## Fuentes de datos

### FTP

El proyecto descarga archivos desde dos carpetas remotas:

- `accenture/atenciones`
- `accenture/tickets`

### Google Drive

Se obtiene el archivo de agencias desde un recurso de Drive y se guarda localmente como `Agencias.xlsx`.

## Transformaciones principales

### Atenciones

Archivo esperado: archivos `.json`

Campos tratados:

- `Atencion ID`
- `Numero Ticket`
- `Tipo Atencion`
- `Proveedor Code`
- `Proveedor`
- `Costo Atencion`

Transformaciones:

- creación de `atencion_id`, `ticket_id`, `tipo_atencion`, `proveedor_id`, `proveedor`, `zona`
- conversión de montos con soporte para valores como `COSTO CERO` y `SIN COSTO`
- generación de:
  - `df_atenciones`
  - `df_proveedor`
- deduplicación de proveedores por `proveedor_id`

### Tickets

Archivos esperados:

- `Lima.csv`
- `Provincia.txt`

Transformaciones:

- unificación de estructuras distintas entre Lima y Provincia
- estandarización de nombres de columnas
- limpieza de texto
- conversión de fechas y prioridades
- extracción de `agencia_id` desde el campo `ubicacion`
- reemplazo de estado `Terminado` por `Cerrado`
- generación de:
  - `df_tickets`
  - `df_item`

### Agencias

Archivo esperado: `Agencias.xlsx`

Transformaciones:

- renombrado de columnas
- normalización de texto
- conversión de `agencia_id` a entero nulo-compatible

## Modelo de carga en SQL Server

Las tablas objetivo se encuentran en el esquema `datamart`:

- `datamart.dim_proveedor`
- `datamart.dim_item`
- `datamart.dim_agencia`
- `datamart.fact_atenciones`

### Estrategia de carga

- **Historico**: truncado completo e inserción total
- **Incremental**: uso de `MERGE` contra una tabla staging temporal

En el flujo actual, el proyecto usa carga incremental para todas las tablas del `main.py`.

### Ventana temporal para fact_atenciones

Antes de cargar `fact_atenciones`, el dataframe se filtra por una ventana que va:

- desde el primer día del mes anterior
- hasta la fecha base configurada en el script

Esto permite limitar el volumen procesado en la tabla transaccional.

## Estructura del proyecto

```text
.
├── main.py
├── config
│   ├── config.yaml
│   ├── logging.py
│   └── settings.py
├── src
│   ├── database.py
│   ├── extract_data.py
│   ├── load_data.py
│   ├── transform_data.py
│   └── utils
│       └── file_managers.py
├── data
│   └── raw
│       ├── atenciones
│       ├── detalles
│       └── tickets
├── logs
├── google-application.json
├── .env
├── requirements.txt
└── README.md
```

## Requisitos

Dependencias utilizadas por el proyecto:

- **Python 3.12.7**
- Se recomienda usar un **entorno virtual** para aislar las dependencias del proyecto
- Instalar las librerías desde `requirements.txt`

Instalación de dependencias:

```bash
pip install -r requirements.txt
```

## Configuración

### 1. Archivo `google-application.json`

Este archivo contiene las credenciales de una cuenta de servicio de Google. Se utiliza para autenticar la aplicación y permitir la descarga de archivos desde Google Drive a través de su API.

Debes conservarlo en una ruta segura y nunca compartirlo en el repositorio, ya que funciona como llave de acceso para el proyecto.

Como referencia para obtenerlo, puedes revisar la documentación oficial de cuentas de servicio de Google:

- https://cloud.google.com/iam/docs/service-account-overview

Y también un tutorial en YouTube para ver el proceso paso a paso:

- https://www.youtube.com/results?search_query=obtener+credenciales+google+drive+api+cuenta+de+servicio+json

### 2. Archivo `.env`

Crea un archivo `.env` en la raíz del proyecto con tus variables locales.

Ejemplo de estructura:

```env
FTP_USER=tu_usuario
FTP_PASSWORD=tu_password
GOOGLE_APPLICATION_CREDENTIALS=ruta/google-application.json
USER_DB=tu_usuario_sql
PASSWORD_DB=tu_password_sql
```

## Ejecución

Desde la raíz del proyecto:

```bash
python main.py
```

## Logging

Cada ejecución genera un archivo en la carpeta `logs/` con nombre basado en la fecha y hora de ejecución.

Los logs registran:

- inicio y fin de cada etapa
- cantidad de registros procesados
- errores durante extracción, transformación o carga

## Recomendaciones

- No subir credenciales al repositorio.
- Mantener `.env` fuera del control de versiones.
- Proteger el archivo JSON de la cuenta de servicio de Google.
- Verificar que existan los directorios locales antes de ejecutar el flujo.
- Confirmar que el driver ODBC para SQL Server esté instalado en el equipo.

## Notas técnicas

- La extracción desde Google Drive soporta archivos públicos y privados.
- La carga incremental utiliza una tabla `staging` temporal para ejecutar el `MERGE`.
- Los dataframes finales están normalizados para facilitar su inserción en SQL Server.

## Mantenimiento

Si agregas nuevas fuentes o tablas, conviene actualizar:

- `config/config.yaml`
- `config/settings.py`
- `src/extract_data.py`
- `src/transform_data.py`
- `src/load_data.py`
- este `README.md`
