import logging
import os
from datetime import datetime


def setup_logging():

    # Crear carpeta logs si no existe
    os.makedirs("logs", exist_ok=True)


    fecha_actual = datetime.now()
    fecha_format = fecha_actual.strftime("%Y%m%d%H%M%S")
    file_name_log = f'logs/{fecha_format}.log'

    logging.basicConfig(
        level=logging.INFO,
        force=True,
        format=(
            "%(asctime)s - "
            "%(levelname)s - "
            "%(name)s - "
            "%(message)s"
        ),
        

        handlers=[
            # Guardar logs en archivo
            logging.FileHandler(file_name_log, encoding="utf-8"),

            # Mostrar logs en consola
            logging.StreamHandler()
        ]
    )