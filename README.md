# Vaccine Prescription Generator

Streamlit tool for generating vaccine prescription `.docx` files from a Word template and spreadsheet data.

## Landing experience

The landing page reuses the Occu-Med dark glass visual language while replacing the pricing-agreement animation with a vaccine-specific scene:

- five supplied vaccine vial assets arranged in a horizontal lineup
- color-matched breathing radiation/bloom around each vial
- moving particle field with depth, drift, bloom, and nearest-vial color influence
- existing Occu-Med logo treatment
- full-viewport click-to-enter behavior
- `prefers-reduced-motion` support

## Generator workflow

1. Upload a vaccine prescription Word template (`.docx`).
2. Upload prescription data (`.xlsx`, `.xlsm`, `.xls`, or `.csv`).
3. Use spreadsheet column names as Word template placeholders, for example `{{patient_name}}` and `{{vaccine}}`.
4. Preview the spreadsheet rows.
5. Generate one prescription document per row and download the ZIP.

## Local run

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Tests

```bash
pytest -q
python -m py_compile app.py ui_experience.py
```

## Render

The repository includes `render.yaml` with the service name `vaccine-prescription-generator`. Render builds with `requirements.txt` and starts the app with Streamlit.
