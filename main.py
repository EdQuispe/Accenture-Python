from config.settings import *
from src.extract_data import importar_archivos_ftp, importar_archivo_excel_drive_privado
from src.transform_data import clean_and_transform_atenciones, clean_and_transform_tickets, clean_and_transform_agencias, join_transaccional_tables



def main():
    importar_archivos_ftp(host, port, FTP_USER, FTP_PASSWORD, folder_remoto_atenciones, carpeta_atenciones)
    importar_archivos_ftp(host, port, FTP_USER, FTP_PASSWORD, folder_remoto_tickets, carpeta_tickets)
    importar_archivo_excel_drive_privado(drive_file_id, carpeta_detalles, GOOGLE_APPLICATION_CREDENTIALS, drive_file_name)

    df_atenciones, df_proveedor = clean_and_transform_atenciones(carpeta_atenciones)

    df_tickets, df_item = clean_and_transform_tickets(carpeta_tickets, lima_file_name, provincia_file_name)

    df_agencias = clean_and_transform_agencias(carpeta_detalles, agencias_file_name)

    df_fact_atenciones = join_transaccional_tables(df_tickets, df_atenciones)


if __name__ == "__main__":
    main()