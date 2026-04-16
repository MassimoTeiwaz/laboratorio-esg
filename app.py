from __future__ import annotations

from supabase import create_client

CO2_COEFFICIENT = 0.45
SUPABASE_URL = "https://dqqwvtnseyjrbenkmhbp.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRxcXd2dG5zZXlqcmJlbmttaGJwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzYzNDg5MTYsImV4cCI6MjA5MTkyNDkxNn0.PkS9h2MFousWVehqTpokRqWjw4XMrdcLgp0VW3V64zc"
SUPABASE_TABLE = "aziende"


def main() -> None:
    print("=== Calcolatore CO2 da consumo elettrico (kWh) ===")

    company_name = input("Nome Azienda: ").strip()
    vat_number = input("Partita IVA: ").strip()

    try:
        consumption_kwh_str = input("kWh consumati: ").strip()
        consumption_kwh = float(consumption_kwh_str.replace(",", "."))
    except ValueError:
        print("Valore non valido per i kWh. Riprova eseguendo di nuovo il programma.")
        return

    co2_kg = consumption_kwh * CO2_COEFFICIENT

    client = create_client(SUPABASE_URL, SUPABASE_KEY)
    payload = {
        "nome": company_name,
        "partita_iva": vat_number,
        "consumo_kwh": consumption_kwh,
        "co2_kg": co2_kg,
    }

    try:
        res = client.table(SUPABASE_TABLE).insert(payload).execute()
        data = getattr(res, "data", None)
        if not data:
            raise RuntimeError("Inserimento riuscito ma risposta vuota.")
        print("Salvataggio riuscito su Supabase (tabella `aziende`).")
    except Exception as e:
        print(f"Salvataggio su Supabase non riuscito: {e}")


if __name__ == "__main__":
    main()
