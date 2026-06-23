from config.settings import *
from src.extract_data import importar_archivos_ftp, importar_archivo_excel_drive, importar_archivo_excel_drive_privado



def main():
    importar_archivos_ftp(host, port, FTP_USER, FTP_PASSWORD, folder_remoto_atenciones, carpeta_atenciones)
    importar_archivos_ftp(host, port, FTP_USER, FTP_PASSWORD, folder_remoto_tickets, carpeta_tickets)
    importar_archivo_excel_drive_privado(drive_file_id, carpeta_detalles, GOOGLE_APPLICATION_CREDENTIALS, drive_file_name)

if __name__ == "__main__":
    main()