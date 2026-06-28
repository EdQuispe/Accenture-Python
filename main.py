from config.settings import *
from src.extract_data import importar_archivos_ftp, importar_archivo_excel_drive_privado
from src.transform_data import clean_and_transform_atenciones, clean_and_transform_tickets, clean_and_transform_agencias, join_transaccional_tables
from src.database import get_sql_server_engine
from src.load_data import historical_or_incremental_table
from datetime import datetime
from config.logging import setup_logging


def main():

    setup_logging()

    importar_archivos_ftp(host, port, FTP_USER, FTP_PASSWORD, folder_remoto_atenciones, carpeta_atenciones)
    importar_archivos_ftp(host, port, FTP_USER, FTP_PASSWORD, folder_remoto_tickets, carpeta_tickets)
    importar_archivo_excel_drive_privado(drive_file_id, carpeta_detalles, GOOGLE_APPLICATION_CREDENTIALS, drive_file_name)

    df_atenciones, df_proveedor = clean_and_transform_atenciones(carpeta_atenciones)
    df_tickets, df_item = clean_and_transform_tickets(carpeta_tickets, lima_file_name, provincia_file_name)
    df_agencias = clean_and_transform_agencias(carpeta_detalles, agencias_file_name)
    df_fact_atenciones = join_transaccional_tables(df_tickets, df_atenciones)

    fecha_str = "30/10/2025"
    fecha = datetime.strptime(fecha_str, "%d/%m/%Y").date()

    engine = get_sql_server_engine(SQL_SERVER, USER_DB, PASSWORD_DB)

    historical_or_incremental_table("Incremental", df_proveedor, engine, "datamart", "dim_proveedor", "proveedor_id")
    historical_or_incremental_table("Incremental", df_item, engine, "datamart", "dim_item", "item_id")
    historical_or_incremental_table("Incremental", df_agencias, engine, "datamart", "dim_agencia", "agencia_id")
    historical_or_incremental_table("Incremental", df_fact_atenciones, engine, "datamart", "fact_atenciones", "atencion_id", fecha)

if __name__ == "__main__":
    main()