# sheets_helpers.py (actualizado a google-auth)
import os
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from pathlib import Path

# Alcance de permisos (solo lectura para seguridad)
SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets.readonly",
    "https://www.googleapis.com/auth/drive.readonly",
]

def get_gsheet_client(service_account_json_path: str):
    """Devuelve un cliente autorizado de gspread usando google-auth."""
    path = Path(service_account_json_path)
    if not path.exists():
        raise FileNotFoundError(f"Google service account JSON no encontrado en: {path}")
    creds = Credentials.from_service_account_file(str(path), scopes=SCOPE)
    client = gspread.authorize(creds)
    return client


def read_sheet_as_df(client, spreadsheet_id: str, sheet_name: str) -> pd.DataFrame:
    """Lee un sheet de Google Sheets y devuelve un DataFrame."""
    sh = client.open_by_key(spreadsheet_id)
    ws = sh.worksheet(sheet_name)
    data = ws.get_all_records()
    df = pd.DataFrame(data)
    return df
