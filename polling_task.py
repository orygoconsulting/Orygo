# polling_task.py
import os, json, hashlib, time
from pathlib import Path
import pandas as pd
from sheets_helpers import get_gsheet_client, read_sheet_as_df
from ingest_docs_and_table import index_document_text

TENANTS_PATH = os.getenv("TENANTS_PATH", "./tenants.json")
GOOGLE_SA_PATH = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON_PATH")
POLL_INTERVAL = int(os.getenv("POLL_INTERVAL", "600"))  # segundos, 600 = 10 min
CACHE_PATH = Path(".cache/polling_state.json")

def hash_dataframe(df: pd.DataFrame) -> str:
    """Crea un hash único del contenido del DataFrame."""
    return hashlib.md5(pd.util.hash_pandas_object(df, index=True).values).hexdigest()

def load_state():
    if CACHE_PATH.exists():
        return json.loads(CACHE_PATH.read_text())
    return {}

def save_state(state: dict):
    CACHE_PATH.parent.mkdir(exist_ok=True)
    CACHE_PATH.write_text(json.dumps(state, indent=2))

def check_tenant(tenant_id: str, tenant_info: dict, state: dict, gclient):
    sheet_id = tenant_info.get("sheet_id")
    sheet_tab = tenant_info.get("sheet_tab", "Company_X")
    if not sheet_id:
        print(f"[WARN] Tenant {tenant_id} sin sheet_id, se omite.")
        return state

    try:
        df = read_sheet_as_df(gclient, sheet_id, sheet_tab)
        sig = hash_dataframe(df)
        old_sig = state.get(tenant_id, {}).get("sheet_hash")

        if old_sig != sig:
            print(f"[UPDATE] Cambios detectados en {tenant_id}/{sheet_tab}.")
            # Aquí puedes hacer la acción que quieras al detectar cambio:
            # Ejemplo: recalcular resumen, reindexar, actualizar dashboard...
            # index_document_text("Datos actualizados", "auto-update", {}, company_id=tenant_id)

            state[tenant_id] = {"sheet_hash": sig, "last_update": time.time()}
        else:
            print(f"[OK] Sin cambios en {tenant_id}/{sheet_tab}.")
    except Exception as e:
        print(f"[ERROR] {tenant_id}: {e}")
    return state

def run_polling():
    print("=== Inicio polling de Google Sheets ===")
    if not Path(TENANTS_PATH).exists():
        raise FileNotFoundError(f"No se encontró {TENANTS_PATH}")
    tenants = json.loads(Path(TENANTS_PATH).read_text())
    gclient = get_gsheet_client(GOOGLE_SA_PATH)

    state = load_state()
    for tenant_id, info in tenants.items():
        state = check_tenant(tenant_id, info, state, gclient)

    save_state(state)
    print("=== Polling completado ===")

if __name__ == "__main__":
    while True:
        run_polling()
        print(f"Esperando {POLL_INTERVAL} segundos...")
        time.sleep(POLL_INTERVAL)
