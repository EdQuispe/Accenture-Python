import os
import yaml
from dotenv import load_dotenv


load_dotenv()

FTP_USER = os.getenv('FTP_USER')
FTP_PASSWORD = os.getenv('FTP_PASSWORD')
GOOGLE_APPLICATION_CREDENTIALS = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')

with open('config/config.yaml', "r", encoding="utf-8") as file:
    config = yaml.safe_load(file)


ftp_server = config["ftp-server"]
local_folders = config["local-folders"]
drive_file = config["drive-file"]
files = config["files"]


host = ftp_server["host"]
port = ftp_server["port"]
folder_remoto_atenciones = ftp_server["folder_remoto_atenciones"]
folder_remoto_tickets = ftp_server["folder_remoto_tickets"]

carpeta_atenciones = local_folders["carpeta_atenciones"]
carpeta_tickets = local_folders["carpeta_tickets"]
carpeta_detalles = local_folders["carpeta_detalles"]

drive_file_id = drive_file["file_id"]
drive_file_url = drive_file["file_url"]
drive_file_name = drive_file["file_name"]

lima_file_name = files['lima_file_name']
provincia_file_name = files['provincia_file_name']
agencias_file_name = files['agencias_file_name']