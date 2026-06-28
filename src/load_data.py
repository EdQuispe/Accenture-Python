import pandas as pd
from sqlalchemy import text
from sqlalchemy.engine import Engine
from datetime import date, datetime


def truncate_and_insert_to_table(df: pd.DataFrame, engine: Engine, schema: str, table: str) -> None:
    try:

        df['fecha_actualizacion'] = pd.Timestamp.now()

        print(f"Se inició la carga del dataframe a la tabla {schema}.{table}")

        nombre_tabla = f"{schema}.{table}"

        with engine.begin() as connection:
            connection.execute(text(f"TRUNCATE TABLE {nombre_tabla}"))

        df.to_sql(name = table, con = engine, schema = schema, if_exists="append", index=False)
        
        filas = len(df)
        print(f"Se cargaron los datos a la tabla {schema}.{table}. Registros Cargados: {filas}")

    except Exception as e:
        print(f"Error durante la carga de datos a la tabla {schema}.{table}.\nDetalle del error: {e}")
        raise


def incremental_upsert_table(df: pd.DataFrame, engine: Engine, schema: str, table: str, merge_column: str) -> None:
    staging_schema = "staging"
    staging_table = table
    nombre_tabla = f"{schema}.{table}"
    nombre_staging = f"{staging_schema}.{staging_table}"

    try:
        if merge_column not in df.columns:
            raise KeyError(f"No existe la columna de upsert '{merge_column}' en el dataframe.")

        df["fecha_actualizacion"] = pd.Timestamp.now()

        columnas = list(df.columns)
        columnas_insert = ", ".join(f"[{col}]" for col in columnas)
        valores_insert = ", ".join(f"source.[{col}]" for col in columnas)
        columnas_update = [col for col in columnas if col != merge_column]
        set_update = ", ".join(f"target.[{col}] = source.[{col}]" for col in columnas_update)

        with engine.begin() as connection:
            connection.execute(text(f"IF SCHEMA_ID('{staging_schema}') IS NULL EXEC('CREATE SCHEMA {staging_schema}')"))

            df.to_sql(name=staging_table, con=connection, schema=staging_schema, if_exists="replace",index=False)

            merge_sql = text(f"""
                                MERGE INTO {nombre_tabla} AS target
                                USING {nombre_staging} AS source
                                    ON target.[{merge_column}] = source.[{merge_column}]
                                WHEN MATCHED THEN
                                    UPDATE SET {set_update}
                                WHEN NOT MATCHED BY TARGET THEN
                                    INSERT ({columnas_insert})
                                    VALUES ({valores_insert});
                            """)

            connection.execute(merge_sql)

    except Exception:
        print(f"Error durante la carga incremental de datos a la tabla {schema}.{table}")
        raise
    finally:
        with engine.begin() as connection:
            connection.execute(
                text(
                    f"IF OBJECT_ID('{staging_schema}.{staging_table}', 'U') IS NOT NULL DROP TABLE {nombre_staging}"
                )
            )


def get_month_window(fecha_actual: date) -> tuple[pd.Timestamp, pd.Timestamp]:
    fecha_base = pd.Timestamp(fecha_actual)
    fecha_base = fecha_base.normalize()

    inicio_periodo = (fecha_base - pd.DateOffset(months=1)).replace(day=1)
    fin_periodo = fecha_base

    return inicio_periodo, fin_periodo


def historical_or_incremental_table(tipo_carga: str, df: pd.DataFrame, engine: Engine, schema: str, table: str, merge_column: str | None = None, fecha_actual: date | None = None):
    if tipo_carga == "Historico":
        truncate_and_insert_to_table(df, engine, schema, table)
    else:
        if fecha_actual is not None:
            print(f"Total Registros del dataframe: ", len(df))
            fecha_inicio, fecha_fin = get_month_window(fecha_actual)
            df = df[df["fecha_creacion"].between(fecha_inicio, fecha_fin, inclusive="both")]
            
        incremental_upsert_table(df, engine, schema, table, merge_column)

    filas = len(df)
    print(f"Se cargaron los datos a la tabla {schema}.{table}. Registros procesados: {filas}")