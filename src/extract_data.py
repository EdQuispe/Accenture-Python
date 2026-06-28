from ftplib import FTP
from pathlib import Path
from shutil import copyfileobj
from urllib.request import Request, urlopen

from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import logging

logger = logging.getLogger(__name__)

ALCANCE_DRIVE = ["https://www.googleapis.com/auth/drive.readonly"]


def crear_carpeta_si_no_existe(ruta_carpeta):
    ruta_carpeta = Path(ruta_carpeta)
    ruta_carpeta.mkdir(parents=True, exist_ok=True)
    return ruta_carpeta


def importar_archivos_ftp(ftpserver: str, port: int, user: str, password: str, carpeta_remota: str, carpeta_local: str):
    carpeta_local = Path(carpeta_local)
    carpeta_local.mkdir(parents=True, exist_ok=True)

    try:
        logger.info(f"FTP: Se ha iniciado la extracción de datos de la carpeta remota '{carpeta_remota}' a '{carpeta_local}'.")
        with FTP() as ftp:
            ftp.connect(ftpserver, port)
            ftp.login(user=user, passwd=password)
            ftp.cwd(carpeta_remota)

            archivos = [nombre for nombre in ftp.nlst() if nombre not in {".", ".."}]
            for nombre_archivo in archivos:
                ruta_local = carpeta_local / Path(nombre_archivo).name
                with ruta_local.open("wb") as archivo_local:
                    ftp.retrbinary(f"RETR {nombre_archivo}", archivo_local.write)

            logger.info(f"Archivos importados exitosamente desde FTP en la carpeta remota '{carpeta_remota}' a '{carpeta_local}'.")

    except Exception:
        logger.exception(f"Error al importar archivos desde FTP en la carpeta remota {carpeta_remota}.")
        raise


def importar_archivo_excel_drive(url_descarga: str, carpeta_local: str, nombre_archivo: str):
    carpeta_local = Path(carpeta_local)
    carpeta_local.mkdir(parents=True, exist_ok=True)

    try:
        logger.info(f"Se inició con el la extracción del archivo {nombre_archivo} de Google Drive en la ruta: {carpeta_local}")
        solicitud = Request(url_descarga, headers={"User-Agent": "Mozilla/5.0"})
        ruta_archivo = carpeta_local / nombre_archivo

        with urlopen(solicitud) as respuesta, ruta_archivo.open("wb") as archivo_local:
            copyfileobj(respuesta, archivo_local)

        logger.info(f"Se descargó exitosamente el archivo {nombre_archivo} de Google Drive en la ruta: {carpeta_local}")

    except Exception:
        logger.exception(f"Error al importar el archivo desde Google Drive con URL pública {url_descarga}.")
        raise


def importar_archivo_excel_drive_privado(file_id: str, carpeta_local: str, ruta_credenciales_json: str, nombre_archivo: str):
    carpeta_local = Path(carpeta_local)
    carpeta_local.mkdir(parents=True, exist_ok=True)

    try:
        logger.info(f"Se inició con el la extracción del archivo {nombre_archivo} de Google Drive en la ruta: {carpeta_local}")
        credenciales = Credentials.from_service_account_file(
            ruta_credenciales_json,
            scopes=ALCANCE_DRIVE,
        )
        servicio = build("drive", "v3", credentials=credenciales)
        metadata = servicio.files().get(fileId=file_id, fields="name,mimeType").execute()

        mime_type = metadata["mimeType"]
        if mime_type == "application/vnd.google-apps.spreadsheet":
            request = servicio.files().export_media(
                fileId=file_id,
                mimeType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
            if not nombre_archivo.lower().endswith(".xlsx"):
                nombre_archivo = f"{nombre_archivo}.xlsx"
        else:
            request = servicio.files().get_media(fileId=file_id)

        ruta_archivo = carpeta_local / nombre_archivo
        with ruta_archivo.open("wb") as archivo_local:
            descargador = MediaIoBaseDownload(archivo_local, request)
            terminado = False
            while not terminado:
                _, terminado = descargador.next_chunk()

        logger.info(f"Se descargó exitosamente el archivo {nombre_archivo} de Google Drive en la ruta: {carpeta_local}")
        
    except Exception:
        logger.exception(f"Error al importar el archivo desde Google Drive con ID {file_id}.")
        raise