from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from supabase import create_client

CO2_COEFFICIENT = 0.45
SUPABASE_URL = "https://dqqwvtnseyjrbenkmhbp.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRxcXd2dG5zZXlqcmJlbmttaGJwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzYzNDg5MTYsImV4cCI6MjA5MTkyNDkxNn0.PkS9h2MFousWVehqTpokRqWjw4XMrdcLgp0VW3V64zc"
SUPABASE_TABLE = "aziende"


@st.cache_resource
def get_client():
    return create_client(SUPABASE_URL, SUPABASE_KEY)


def calculate_esg_rating(
    *,
    consumo_kwh: float,
    total_employees: int,
    women_leaders: int,
    training_hours: float,
    has_code_of_ethics: bool,
) -> int:
    environmental_score = max(0.0, 35.0 - min(consumo_kwh / 1000.0, 35.0))

    if total_employees > 0:
        leadership_ratio = women_leaders / total_employees
    else:
        leadership_ratio = 0.0

    gender_score = min(25.0, leadership_ratio * 50.0)
    training_score = min(20.0, training_hours / 2.0)
    governance_score = 20.0 if has_code_of_ethics else 0.0

    final_score = environmental_score + gender_score + training_score + governance_score
    return max(0, min(100, round(final_score)))


def save_company_data(payload: dict) -> None:
    client = get_client()
    res = client.table(SUPABASE_TABLE).insert(payload).execute()
    if not getattr(res, "data", None):
        raise RuntimeError("Inserimento riuscito ma risposta vuota.")


def load_latest_companies(limit: int = 20) -> pd.DataFrame:
    client = get_client()
    query = (
        client.table(SUPABASE_TABLE)
        .select(
            "nome,partita_iva,consumo_kwh,co2_kg,numero_dipendenti,donne_ruoli_comando,ore_formazione_annue,codice_etico,rating_esg"
        )
        .order("id", desc=True)
        .limit(limit)
        .execute()
    )
    data = getattr(query, "data", []) or []
    return pd.DataFrame(data)


def render_gauge(score: int) -> None:
    figure = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=score,
            number={"suffix": "/100"},
            title={"text": "Rating ESG"},
            gauge={
                "axis": {"range": [0, 100]},
                "bar": {"color": "#0f766e"},
                "steps": [
                    {"range": [0, 40], "color": "#fecaca"},
                    {"range": [40, 70], "color": "#fde68a"},
                    {"range": [70, 100], "color": "#bbf7d0"},
                ],
            },
        )
    )
    figure.update_layout(height=320, margin=dict(l=30, r=30, t=60, b=30))
    st.plotly_chart(figure, use_container_width=True)


def main() -> None:
    st.set_page_config(page_title="Sistema Certificazione ESG - Laboratorio", layout="wide")
    st.title("Sistema Certificazione ESG - Laboratorio")
    st.caption("Raccolta dati ESG, calcolo rating e salvataggio cloud su Supabase.")

    company_col, preview_col = st.columns([2, 1])
    with company_col:
        nome = st.text_input("Nome Azienda", placeholder="Es. Green Future S.r.l.")
        partita_iva = st.text_input("P.IVA", placeholder="Es. 12345678901")

    tab_environmental, tab_social, tab_governance = st.tabs(
        ["🌱 Environmental", "🤝 Social", "⚖️ Governance"]
    )

    with tab_environmental:
        consumo_kwh = st.number_input("kWh consumati", min_value=0.0, step=1.0, format="%.2f")
        co2_preview = consumo_kwh * CO2_COEFFICIENT
        st.metric("CO2 calcolata (kg)", f"{co2_preview:.2f}")

    with tab_social:
        social_col1, social_col2, social_col3 = st.columns(3)
        with social_col1:
            total_employees = st.number_input("Numero totale dipendenti", min_value=0, step=1)
        with social_col2:
            women_leaders = st.number_input("Donne in ruoli di comando", min_value=0, step=1)
        with social_col3:
            training_hours = st.number_input(
                "Ore di formazione annue", min_value=0.0, step=1.0, format="%.2f"
            )

    with tab_governance:
        has_code_of_ethics = st.toggle("L'azienda dispone di un Codice Etico?", value=False)

    rating_score = calculate_esg_rating(
        consumo_kwh=consumo_kwh,
        total_employees=int(total_employees),
        women_leaders=int(women_leaders),
        training_hours=training_hours,
        has_code_of_ethics=has_code_of_ethics,
    )

    with preview_col:
        st.metric("Rating ESG stimato", f"{rating_score}/100")
        render_gauge(rating_score)

    if st.button("Genera Rating ESG", type="primary", use_container_width=True):
        if not nome.strip():
            st.warning("Inserisci il Nome Azienda.")
        elif not partita_iva.strip():
            st.warning("Inserisci la Partita IVA.")
        elif women_leaders > total_employees:
            st.warning("Le donne in ruoli di comando non possono superare il totale dipendenti.")
        else:
            try:
                co2_kg = consumo_kwh * CO2_COEFFICIENT
                payload = {
                    "nome": nome.strip(),
                    "partita_iva": partita_iva.strip(),
                    "consumo_kwh": consumo_kwh,
                    "co2_kg": co2_kg,
                    "numero_dipendenti": int(total_employees),
                    "donne_ruoli_comando": int(women_leaders),
                    "ore_formazione_annue": training_hours,
                    "codice_etico": has_code_of_ethics,
                    "rating_esg": rating_score,
                }
                save_company_data(payload)
                st.success("Rating ESG generato e salvato con successo su Supabase.")
            except Exception as e:
                st.error(f"Errore durante il salvataggio su Supabase: {e}")

    st.divider()
    st.subheader("Ultime aziende inserite")

    try:
        df = load_latest_companies(limit=20)
        if df.empty:
            st.info("Nessun dato presente in tabella.")
        else:
            df = df.rename(
                columns={
                    "nome": "Nome Azienda",
                    "partita_iva": "P.IVA",
                    "consumo_kwh": "kWh",
                    "co2_kg": "CO2 (kg)",
                    "numero_dipendenti": "Dipendenti",
                    "donne_ruoli_comando": "Donne in comando",
                    "ore_formazione_annue": "Ore formazione",
                    "codice_etico": "Codice Etico",
                    "rating_esg": "Rating ESG",
                }
            )
            st.dataframe(df, use_container_width=True, hide_index=True)
    except Exception as e:
        st.error(f"Impossibile leggere i dati dal database: {e}")


if __name__ == "__main__":
    main()
