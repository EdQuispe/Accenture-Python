import pandas as pd
from sqlalchemy import text
from sqlalchemy.engine import Engine


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
