# Vaccine Landing + Generator Shell Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the Vaccine Prescription Generator from the Pricing Agreement Generator's proven Streamlit shell, replacing all agreement-specific behavior with a vaccine-specific generator shell and a full-screen animated vial landing scene.

**Architecture:** Keep the same two-file separation used by the source app: `app.py` owns routing and vaccine prescription generation; `ui_experience.py` owns shared dark/glass styling and the landing component. The landing component embeds the authoritative Occu-Med logo plus supplied vial PNG assets, uses CSS pseudo-elements for color-matched breathing auras, and a lightweight `<canvas>` JavaScript particle system for the drifting particle field. The main generator uses a generic Word-template placeholder engine (`{{column_name}}`) so it remains vaccine-prescription specific without importing pricing-agreement fields, currencies, or agreement logic.

**Tech Stack:** Python 3.12.8, Streamlit 1.41.1, python-docx 1.0.2, pandas 2.2.3, HTML/CSS/JavaScript embedded with `streamlit.components.v1.html`.

**Spec:** `docs/superpowers/specs/2026-09-17-vaccine-landing-design.md`

## Global Constraints

- Reuse `assets/occu-med-logo.png` from `Pricing_Agreement_Generator` unchanged.
- Use the supplied vaccine vial artwork without regenerating or stylistically altering it.
- Vials stay in a horizontal lineup; they do not orbit or float around the screen.
- Each vial gets a slowly breathing, color-matched radiation/bloom effect.
- Particle movement is generated live in-browser and remains subtle.
- Preserve the pricing generator's full-screen landing-to-app transition pattern and glass frame language.
- Remove all pricing-agreement terminology, service/price lists, currency logic, agreement templates, and floating pricing-sheet animation.
- Respect `prefers-reduced-motion`.
- Python runtime remains 3.12.8 and Render stays on the existing free-compatible Python web-service configuration.

---

### Task 1: Build the vaccine prescription generator engine and app routing

**Files:**
- Create: `app.py`
- Create: `tests/test_app.py`
- Modify: `requirements.txt`

**Interfaces:**
- Consumes: `ui_experience.apply_luminous_ui()` and `ui_experience.render_landing_page()` from Task 2.
- Produces: `replace_placeholders(document, values) -> int`, `generate_document(template_bytes, values) -> bytes`, `make_zip(template_bytes, records) -> tuple[bytes, list[dict[str, str]]]`, and `main() -> None`.

- [ ] **Step 1: Write failing unit tests for placeholder replacement and ZIP generation.**

```python
from io import BytesIO
from zipfile import ZipFile

from docx import Document

import app


def _template_bytes(text: str) -> bytes:
    doc = Document()
    doc.add_paragraph(text)
    out = BytesIO()
    doc.save(out)
    return out.getvalue()


def test_generate_document_replaces_braced_placeholders():
    result = app.generate_document(
        _template_bytes("Patient: {{patient_name}} | Vaccine: {{vaccine}}"),
        {"patient_name": "Alex Example", "vaccine": "Tdap"},
    )
    doc = Document(BytesIO(result))
    assert "Patient: Alex Example | Vaccine: Tdap" in "\n".join(p.text for p in doc.paragraphs)


def test_make_zip_creates_one_docx_per_record():
    records = [
        {"patient_name": "Alpha", "vaccine": "MMR"},
        {"patient_name": "Beta", "vaccine": "Hepatitis B"},
    ]
    zip_bytes, manifest = app.make_zip(
        _template_bytes("{{patient_name}} - {{vaccine}}"), records
    )
    with ZipFile(BytesIO(zip_bytes)) as archive:
        docx_names = [name for name in archive.namelist() if name.endswith(".docx")]
    assert len(docx_names) == 2
    assert len(manifest) == 2
```

- [ ] **Step 2: Run the tests and verify they fail because `app.py` does not exist yet.**

Run: `pytest tests/test_app.py -q`
Expected: collection/import failure for `app`.

- [ ] **Step 3: Implement the minimal generic Word-template engine and Streamlit app.**

`app.py` must:
- replace `{{column_name}}` placeholders across paragraphs and table cells;
- accept CSV/XLSX rows and a `.docx` prescription template;
- preview the input rows;
- generate one completed `.docx` per row plus `manifest.csv` in a ZIP;
- expose the landing page unless `?view=app` is present;
- contain no agreement/pricing/currency-specific terminology or fields.

- [ ] **Step 4: Run tests and compile checks.**

Run: `pytest tests/test_app.py -q && python -m py_compile app.py`
Expected: all tests PASS and compile exits 0.

- [ ] **Step 5: Commit Task 1.**

```bash
git add app.py tests/test_app.py requirements.txt
git commit -m "feat: add vaccine prescription generator shell"
```

### Task 2: Implement the animated vial landing experience

**Files:**
- Create: `ui_experience.py`
- Create: `tests/test_ui_experience.py`
- Create binary assets under `assets/`: `occu-med-logo.png`, `vial-purple.png`, `vial-green.png`, `vial-blue.png`, `vial-cyan.png`, `vial-green-alt.png`

**Interfaces:**
- Produces: `apply_luminous_ui() -> None`, `_build_landing_html() -> str`, and `render_landing_page() -> None`.
- `app.py` imports `apply_luminous_ui` and `render_landing_page`.

- [ ] **Step 1: Write failing structural tests for the landing HTML.**

```python
import ui_experience


def test_landing_html_contains_vial_lineup_particle_canvas_and_logo():
    html = ui_experience._build_landing_html()
    assert 'id="particle-field"' in html
    assert 'class="vial-lineup"' in html
    assert html.count('class="vial ') >= 5
    assert 'occu-med-logo' in html


def test_landing_html_respects_reduced_motion():
    html = ui_experience._build_landing_html()
    assert "prefers-reduced-motion" in html
    assert "matchMedia('(prefers-reduced-motion: reduce)')" in html
```

- [ ] **Step 2: Run the tests and verify they fail because `ui_experience.py` does not exist yet.**

Run: `pytest tests/test_ui_experience.py -q`
Expected: collection/import failure for `ui_experience`.

- [ ] **Step 3: Implement the landing component.**

The HTML/CSS/JS must include:
- pricing-generator-style nested glass frame and dark navy/black background;
- unchanged repository logo centered above or visually integrated with the lineup;
- five supplied vial PNGs in one horizontal lineup using `object-fit: contain`;
- a per-vial CSS aura (`::before`/wrapper layer) using the vial's configured RGB color, animated with slow scale/blur/opacity breathing;
- a full-stage canvas particle field with depth, varying radius/alpha/speed, upward + lateral drift, and occasional bloom;
- nearest-vial color influence based on each particle's x-position;
- mobile scaling/wrapping prevention so the lineup remains coherent without overflow;
- `@media (prefers-reduced-motion: reduce)` that disables aura animation;
- JavaScript `matchMedia('(prefers-reduced-motion: reduce)')` that stops particle motion and draws a static field;
- the existing click-through pattern to `?view=app`.

- [ ] **Step 4: Run UI tests and compile checks.**

Run: `pytest tests/test_ui_experience.py -q && python -m py_compile ui_experience.py`
Expected: all tests PASS and compile exits 0.

- [ ] **Step 5: Commit Task 2.**

```bash
git add ui_experience.py tests/test_ui_experience.py assets/
git commit -m "feat: add animated vaccine vial landing scene"
```

### Task 3: Integrate deployment configuration and perform end-to-end verification

**Files:**
- Modify: `render.yaml`
- Modify: `README.md`

**Interfaces:**
- Consumes: `app.main()` and all assets from Tasks 1-2.
- Produces: a Render-startable Streamlit service on `main`.

- [ ] **Step 1: Update Render build/start commands to compile and run the new app.**

Use:

```yaml
buildCommand: "pip install --upgrade pip && pip install -r requirements.txt && python -m py_compile app.py ui_experience.py"
startCommand: "streamlit run app.py --server.address=0.0.0.0 --server.port=$PORT --server.headless=true"
```

Do not add Blueprint-only or paid deployment requirements.

- [ ] **Step 2: Update README to describe the vaccine generator, token placeholders, landing animation, local run, and Render commands.**

Document only behavior that actually exists after Tasks 1-2.

- [ ] **Step 3: Run the full verification suite.**

Run:

```bash
pytest -q
python -m py_compile app.py ui_experience.py
python - <<'PY'
import app
import ui_experience
html = ui_experience._build_landing_html()
assert "Pricing Agreement" not in html
assert "price-sheet" not in html
assert "particle-field" in html
assert "vial-lineup" in html
print("verification-ok")
PY
```

Expected: tests PASS, compile exits 0, and `verification-ok` prints.

- [ ] **Step 4: Review responsive and accessibility hooks in the generated HTML.**

Confirm source contains mobile media queries, `prefers-reduced-motion`, meaningful image `alt` attributes, and no horizontal page overflow rules.

- [ ] **Step 5: Commit Task 3.**

```bash
git add render.yaml README.md
git commit -m "chore: finalize vaccine generator deployment"
```
