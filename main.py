from config.settings import *
from src.extract_data import importar_archivos_ftp, importar_archivo_excel_drive



def main():

    importar_archivos_ftp(host, port, FTP_USER, FTP_PASSWORD, folder_remoto_atenciones, carpeta_atenciones)
    importar_archivos_ftp(host, port, FTP_USER, FTP_PASSWORD, folder_remoto_tickets, carpeta_tickets)
    importar_archivo_excel_drive(drive_file_url, carpeta_detalles, drive_file_name)


if __name__ == "__main__":
    main()