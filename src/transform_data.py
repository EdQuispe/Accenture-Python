from pathlib import Path
import pandas as pd


def obtener_monto(costo_atencion: str):
    if pd.isna(costo_atencion):
        return pd.NA

    monto = str(costo_atencion).strip().upper()

    match monto:
        case "":
            return pd.NA
        case "COSTO CERO" | "SIN COSTO":
            return 0.0
        case _:
            return pd.to_numeric(monto.replace(",", "."), errors="coerce")
        
        
def clean_and_transform_atenciones(carpeta_local: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    folder_path = Path(carpeta_local)
    archivos = list(folder_path.glob('*.json'))

    if not archivos:
        raise FileNotFoundError(f'No se encontraron archivos JSON en: {folder_path}')

    columnas = [
        'Atencion ID',
        'Numero Ticket',
        'Tipo Atencion',
        'Proveedor Code',
        'Proveedor',
        'Costo Atencion'
    ]

    lista_dfs = []
    for archivo in archivos:
        df = pd.read_json(archivo)
        df = df[columnas]
        df['file_name'] = archivo.name
        lista_dfs.append(df)

    df = pd.concat(lista_dfs, ignore_index=True)

    df['atencion_id'] = pd.to_numeric(df['Atencion ID'], errors='coerce').astype('Int64')
    df['ticket_id'] = df['Numero Ticket'].astype('string').str.strip().str.upper()
    df['tipo_atencion'] = df['Tipo Atencion'].astype('string').str.strip()
    df['proveedor_id'] = pd.to_numeric(df['Proveedor Code'].astype('string').str.strip().replace('', pd.NA), errors='coerce').astype('Int64')
    df['proveedor'] = df['Proveedor'].astype('string').str.strip().str.upper()
    df["zona"] = df["file_name"].str.extract(r'_(.*?)\.json$')[0].astype('string')
    df["costo_atencion"] = df['Costo Atencion'].apply(obtener_monto).astype('Float64').round(4)

    df_atenciones = df[['atencion_id', 'ticket_id', 'tipo_atencion', 'proveedor_id', 'zona', 'costo_atencion']].copy()

    df_proveedor = df[["atencion_id", "proveedor_id", "proveedor"]].copy()

    df_proveedor = df_proveedor[df_proveedor['proveedor_id'].notna()]

    df_proveedor = (
                    df_proveedor.sort_values(["proveedor_id", "atencion_id"], ascending=[True, False])
                                .drop_duplicates(subset=["proveedor_id"])
                                [['proveedor_id', 'proveedor']]
                    )
    
    return df_atenciones, df_proveedor


def after_delimiter(ubicacion: str, delimiter: str = '-'):
    if pd.isna(ubicacion):
        return pd.NA

    ubicacion = str(ubicacion)
    if delimiter not in ubicacion:
        return pd.NA

    valor = ubicacion.split(delimiter, 1)[1].strip()
    return pd.to_numeric(valor, errors='coerce')


def clean_and_transform_tickets(carpeta_local: str, lima_file_name: str, provincia_file_name: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    folder_path = Path(carpeta_local)

    lima_path = folder_path / lima_file_name
    provincia_path = folder_path / provincia_file_name

    if not lima_path.exists():
        raise FileNotFoundError(f'No se encontro el archivo: {lima_path}')

    if not provincia_path.exists():
        raise FileNotFoundError(f'No se encontro el archivo: {provincia_path}')
    
    df_lima = pd.read_csv(lima_path, sep=";", dtype='string')
    df_lima['region'] = 'Lima'

    df_provincia = pd.read_csv(provincia_path, sep='|', dtype='string')
    df_provincia['region'] = 'Provincia'

    df_lima.rename(columns={
                    "Numero Ticket": "ticket_id", 
                    "Item ID": "item_id", 
                    "Item": "item",
                    "Resumen": "resumen",
                    "Ubicacion": "ubicacion",
                    "Modo reporte": "modo_reporte",
                    "Estado": "estado",
                    "Fecha Creacion": "fecha_creacion",
                    "Fecha Termino": "fecha_termino",
                    "Fecha Cierre": "fecha_cierre",
                    "Prioridad": "prioridad"}, 
                    inplace=True)

    df_provincia.rename(columns={
                    "NumeroTicket": "ticket_id", 
                    "ItemID": "item_id", 
                    "Item": "item",
                    "Resumen": "resumen",
                    "Ubicacion": "ubicacion",
                    "ModoReporte": "modo_reporte",
                    "Estado": "estado",
                    "FechaCreacion": "fecha_creacion",
                    "FechaTermino": "fecha_termino",
                    "FechaCierre": "fecha_cierre",
                    "Prioridad": "prioridad"}, 
                    inplace=True)
    
    df = pd.concat([df_lima, df_provincia], ignore_index=True)

    df['ticket_id'] = df['ticket_id'].astype('string').str.strip().str.upper()
    df['item_id'] = pd.to_numeric(df['item_id'].astype('string').str.strip().replace('', pd.NA), errors='coerce').astype('Int64')
    df['item'] = df['item'].astype('string').str.strip()
    df['region'] = df['region'].astype('string')
    df['agencia_id'] = df['ubicacion'].apply(after_delimiter).astype('Int64')
    df['estado'] = df['estado'].astype('string').str.strip().mask(df['estado'] == 'Terminado', 'Cerrado')
    df['fecha_creacion'] = pd.to_datetime(df['fecha_creacion'], format='%Y-%m-%d', errors='coerce')
    df['fecha_termino'] = pd.to_datetime(df['fecha_termino'], format='%d-%m-%y', errors='coerce')
    df['fecha_cierre'] = pd.to_datetime(df['fecha_cierre'], format='%d/%m/%Y', errors='coerce')
    df['prioridad'] = pd.to_numeric(df['prioridad'].astype('string').str.strip().replace('', pd.NA), errors='coerce').astype('Int64')

    df = (
            df.sort_values(['ticket_id', 'fecha_termino', 'fecha_cierre'], ascending=[True, False, False])
                   .drop_duplicates(subset=['ticket_id'])
                   .reset_index(drop=True)
                )

    df_tickets = df[['ticket_id', 'item_id', 'agencia_id', 'estado', 'fecha_creacion', 'fecha_termino', 'fecha_cierre', 'prioridad', 'region']].copy()

    df_item = df[['item_id', 'item', 'fecha_termino', 'fecha_cierre']].copy()

    df_item = df_item[df_item["item_id"].notna()]

    df_item = (
                df_item.sort_values(['item_id', 'fecha_termino', 'fecha_cierre'], ascending=[True, False, False])
                        .drop_duplicates(subset=['item_id'])
                        [["item_id", "item"]]
                )

    return df_tickets, df_item


def clean_and_transform_agencias(carpeta_local: str, nombre_archivo: str = 'Agencias.xlsx') -> pd.DataFrame:
    folder_path = Path(carpeta_local)
    ruta_archivo = folder_path / nombre_archivo

    if not ruta_archivo.exists():
        raise FileNotFoundError(f'No se encontro el archivo: {ruta_archivo}')

    df_agencias = pd.read_excel(ruta_archivo, dtype='string')
    
    df_agencias.rename(columns={
        'AgenciaID': 'agencia_id',
        'Agencia': 'agencia',
        'Region': 'region',
        'Direccion': 'direccion',
        'Distrito': 'distrito',
        'Provincia': 'provincia',
        'Departamento': 'departamento',
        'Tipo Oficina': 'tipo_oficina'
    }, inplace=True)

    df_agencias = df_agencias[["agencia_id", "agencia", "region", "direccion", "distrito", "provincia", "departamento", "tipo_oficina"]]

    df_agencias['agencia_id'] = pd.to_numeric(df_agencias['agencia_id'].str.strip().replace('', pd.NA), errors='coerce').astype('Int64')
    df_agencias['agencia'] = df_agencias['agencia'].str.strip().str.upper()
    df_agencias['region'] = df_agencias['region'].str.strip()
    df_agencias['direccion'] = df_agencias['direccion'].str.strip().str.lower()
    df_agencias['distrito'] = df_agencias['distrito'].str.strip()
    df_agencias['provincia'] = df_agencias['provincia'].str.strip()
    df_agencias['departamento'] = df_agencias['departamento'].str.strip()
    df_agencias['tipo_oficina'] = df_agencias['tipo_oficina'].str.strip()
    
    return df_agencias


def join_transaccional_tables(df_tickets: pd.DataFrame, df_atenciones: pd.DataFrame) -> pd.DataFrame:
    df_fact_atenciones = df_tickets.merge(df_atenciones, on="ticket_id", how="inner")

    df_fact_atenciones = df_fact_atenciones[["atencion_id", "ticket_id", "agencia_id", "estado", "fecha_creacion", "fecha_termino", "fecha_cierre",
                        "prioridad", "region", "tipo_atencion", "proveedor_id", "zona", "costo_atencion"]]

    return df_fact_atenciones