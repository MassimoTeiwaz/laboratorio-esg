# Sistema di certificazione ESG - Laboratorio

Questo è un prototipo iniziale per il sistema di certificazione ESG.

## Esecuzione

1. Assicurati di avere installato Python 3.
2. Dal terminale, posizionati nella cartella del progetto.
3. Imposta la chiave Supabase (variabile d'ambiente `SUPABASE_KEY`).
4. Esegui:

```bash
python3 app.py
```

## Funzionalità attuale

- Inserimento del nome dell'azienda.
- Inserimento del consumo di energia elettrica in kWh.
- Calcolo immediato della CO₂ stimata usando il coefficiente 0,45 (kg CO₂ per kWh).
- Stampa del risultato a video.

