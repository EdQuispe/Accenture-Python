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
    df["zona"] = df["file_name"].str.extract(r'_(.*?)\.json$')[0]
    df["costo_atencion"] = df['Costo Atencion'].apply(obtener_monto)

    df_atenciones = df[['atencion_id', 'ticket_id', 'tipo_atencion', 'proveedor_id', 'proveedor', 'zona', 'costo_atencion']].copy()

    df_proveedor = df[["atencion_id", "proveedor_id", "proveedor"]].copy()

    df_proveedor = df_proveedor[df_proveedor['proveedor_id'].notna()]

    df_proveedor = (
                    df_proveedor.sort_values(["proveedor_id", "atencion_id"], ascending=[True, False])
                                .drop_duplicates(subset=["proveedor_id"])
                                [['proveedor_id', 'proveedor']]
                    )
    
    return df_atenciones, df_proveedor    