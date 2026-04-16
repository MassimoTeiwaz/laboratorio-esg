from __future__ import annotations

import os
from typing import Any, Dict

from supabase import create_client

SUPABASE_URL = "https://dqqwvtnseyjrbenkmhbp.supabase.co"


def get_supabase_client():
    key = os.getenv("SUPABASE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRxcXd2dG5zZXlqcmJlbmttaGJwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzYzNDg5MTYsImV4cCI6MjA5MTkyNDkxNn0.PkS9h2MFousWVehqTpokRqWjw4XMrdcLgp0VW3V64zc").strip()
    if not key:
        raise RuntimeError("Manca la variabile d'ambiente SUPABASE_KEY.")
    return create_client(SUPABASE_URL, key)


def insert_energy_emission(
    *,
    company_name: str,
    vat_number: str,
    consumption_kwh: float,
    co2_kg: float,
    table: str = "aziende",
) -> Dict[str, Any]:
    client = get_supabase_client()

    payload = {
        "nome": company_name,
        "partita_iva": vat_number,
        "consumo_kwh": consumption_kwh,
        "co2_kg": co2_kg,
    }

    res = client.table(table).insert(payload).execute()

    data = getattr(res, "data", None)
    if data is None:
        raise RuntimeError("Inserimento su Supabase fallito (nessuna risposta dati).")

    # Il client tipicamente ritorna una lista di righe inserite
    return {"table": table, "data": data}

