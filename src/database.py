import urllib
from sqlalchemy import create_engine


def get_sql_server_engine(sql_server: dict, user: str, password: str):

    driver = sql_server['driver']
    server = sql_server['server']
    database = sql_server['database']

    connection_string = (
        f"DRIVER={{{driver}}};"
        f"SERVER={server};"
        f"DATABASE={database};"
        f"UID={user};"
        f"PWD={password};"
        "TrustServerCertificate=yes;"
    )

    params = urllib.parse.quote_plus(connection_string)
    try:

        engine = create_engine(
            f"mssql+pyodbc:///?odbc_connect={params}",
            fast_executemany=True
        )

        print(f"Se ha establecido de manera exitosa la conexión al servidor {server}")
    except Exception as e:
        print(f"No se ha podido establecer la conexión al servidor {server}. \nDetalle del error: {e}")
        raise

    return engine