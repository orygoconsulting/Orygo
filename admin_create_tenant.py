# admin_create_tenant.py
import os, json, secrets
from pathlib import Path

TENANTS_PATH = os.getenv("TENANTS_PATH", "./tenants.json")

def load_tenants():
    if Path(TENANTS_PATH).exists():
        return json.loads(Path(TENANTS_PATH).read_text())
    return {}

def save_tenants(d):
    Path(TENANTS_PATH).write_text(json.dumps(d, indent=2))

def create_tenant(company_id, sheet_id):
    tenants = load_tenants()
    if company_id in tenants:
        raise Exception("Tenant ya existe")
    api_key = "sk-" + secrets.token_hex(16)
    tenants[company_id] = {"sheet_id": sheet_id, "api_key": api_key}
    save_tenants(tenants)
    print("Tenant creado:", company_id, api_key)
    return api_key

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3:
        print("Uso: python admin_create_tenant.py <company_id> <sheet_id>")
        exit(1)
    cid = sys.argv[1]
    sid = sys.argv[2]
    create_tenant(cid, sid)
