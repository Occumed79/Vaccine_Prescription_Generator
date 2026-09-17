# Vaccine Prescription Generator

A Streamlit tool for producing vaccine prescription `.docx` files from a Word template and spreadsheet data.

## Landing experience

The app opens with a full-screen Occu-Med landing scene using the supplied vaccine vial artwork. Five vials remain lined up while each gets a subtle color-matched radiation/bloom effect. A lightweight canvas layer renders drifting colored particles behind the glass frame. Reduced-motion preferences disable the continuous animation.

Click anywhere on the landing page to enter the generator.

## Generate prescriptions

Create a `.docx` template with placeholders such as:

```text
{{patient_name}}
{{vaccine}}
{{dose}}
{{date}}
```

The placeholder name must match a spreadsheet column.

1. Upload the Word prescription template.
2. Upload a CSV or Excel spreadsheet.
3. Review the preview.
4. Generate one completed `.docx` per row.
5. Download the generated files together in a ZIP with `manifest.csv`.

The placeholder engine supports normal paragraphs and Word table cells.

## Local run

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Render deployment

Runtime: Python 3.12.8

Build command:

```bash
pip install --upgrade pip && pip install -r requirements.txt && python -m py_compile app.py ui_experience.py
```

Start command:

```bash
streamlit run app.py --server.address=0.0.0.0 --server.port=$PORT --server.headless=true
```
