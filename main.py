from config.settings import *
from src.extract_data import importar_archivos_ftp, importar_archivo_excel_drive_privado
from src.transform_data import clean_and_transform_atenciones, clean_and_transform_tickets, clean_and_transform_agencias, join_transaccional_tables
from src.database import get_sql_server_engine
from src.load_data import truncate_and_insert_to_table


def main():
    importar_archivos_ftp(host, port, FTP_USER, FTP_PASSWORD, folder_remoto_atenciones, carpeta_atenciones)
    importar_archivos_ftp(host, port, FTP_USER, FTP_PASSWORD, folder_remoto_tickets, carpeta_tickets)
    importar_archivo_excel_drive_privado(drive_file_id, carpeta_detalles, GOOGLE_APPLICATION_CREDENTIALS, drive_file_name)

    df_atenciones, df_proveedor = clean_and_transform_atenciones(carpeta_atenciones)
    df_tickets, df_item = clean_and_transform_tickets(carpeta_tickets, lima_file_name, provincia_file_name)
    df_agencias = clean_and_transform_agencias(carpeta_detalles, agencias_file_name)
    df_fact_atenciones = join_transaccional_tables(df_tickets, df_atenciones)

    engine = get_sql_server_engine(SQL_SERVER, USER_DB, PASSWORD_DB )

    truncate_and_insert_to_table(df_proveedor, engine, "datamart", "dim_proveedor")
    truncate_and_insert_to_table(df_item, engine, "datamart", "dim_item")
    truncate_and_insert_to_table(df_agencias, engine, "datamart", "dim_agencia")
    truncate_and_insert_to_table(df_fact_atenciones, engine, "datamart", "fact_atenciones")

if __name__ == "__main__":
    main()