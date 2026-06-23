'''
import os
import yaml
from dotenv import load_dotenv


load_dotenv()

CLAVE = os.getenv('clave')


with open('config/config.yaml', "r", encoding="utf-8") as file:
    config = yaml.safe_load(file)


FILE_SOURCE = config['file_source']
'''