from ftplib import FTP
from pathlib import Path
from shutil import copyfileobj
from urllib.request import Request, urlopen


def importar_archivos_ftp(ftpserver: str, port: int, user: str, password: str, carpeta_remota: str, carpeta_local: str):
    carpeta_local = Path(carpeta_local)
    carpeta_local.mkdir(parents=True, exist_ok=True)

    try:
        with FTP() as ftp:
            ftp.connect(ftpserver, port)
            ftp.login(user=user, passwd=password)
            ftp.cwd(carpeta_remota)

            archivos = [nombre for nombre in ftp.nlst() if nombre not in {".", ".."}]
            for nombre_archivo in archivos:
                ruta_local = carpeta_local / Path(nombre_archivo).name
                with ruta_local.open("wb") as archivo_local:
                    ftp.retrbinary(f"RETR {nombre_archivo}", archivo_local.write)

            print(f"Archivos importados exitosamente desde FTP en la carpeta remota '{carpeta_remota}' a '{carpeta_local}'.")

    except Exception as error:
        raise RuntimeError(
            f"Error al importar archivos desde FTP en la carpeta remota '{carpeta_remota}'."
        ) from error
    

def importar_archivo_excel_drive(url_descarga: str, carpeta_local: str, nombre_archivo: str):
    carpeta_local = Path(carpeta_local)
    carpeta_local.mkdir(parents=True, exist_ok=True)

    try:
        solicitud = Request(url_descarga, headers={"User-Agent": "Mozilla/5.0"})
        ruta_archivo = carpeta_local / nombre_archivo

        with urlopen(solicitud) as respuesta, ruta_archivo.open("wb") as archivo_local:
            copyfileobj(respuesta, archivo_local)

        print(f"Se descargó exitosamente el archivo {nombre_archivo} de Google Drive en la ruta: {carpeta_local}")

    except Exception as error:
        raise RuntimeError(
            f"Error al importar el archivo desde Google Drive con URL pública '{url_descarga}'."
        ) from error