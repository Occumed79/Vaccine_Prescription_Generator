from __future__ import annotations

import hashlib
import io
import os
import re
import uuid
import zipfile
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Mapping, Sequence

from docx import Document

try:
    import psycopg
    from psycopg.rows import dict_row
except Exception:
    psycopg = None
    dict_row = None

TOKEN_RE = re.compile(r"\{\{\s*([A-Za-z0-9_.-]+)\s*\}\}")


def _string_values(values: Mapping[str, object]) -> dict[str, str]:
    return {str(key): "" if value is None else str(value) for key, value in values.items()}


def _render_text(text: str, values: Mapping[str, str]) -> str:
    return TOKEN_RE.sub(lambda match: values.get(match.group(1), match.group(0)), text)


def _replace_in_paragraph(paragraph, values: Mapping[str, str]) -> int:
    original = paragraph.text
    rendered = _render_text(original, values)
    if rendered == original:
        return 0
    if paragraph.runs:
        paragraph.runs[0].text = rendered
        for run in paragraph.runs[1:]:
            run.text = ""
    else:
        paragraph.add_run(rendered)
    return 1


def _iter_table_paragraphs(table):
    for row in table.rows:
        for cell in row.cells:
            yield from cell.paragraphs
            for nested in cell.tables:
                yield from _iter_table_paragraphs(nested)


def replace_placeholders(document: Document, values: Mapping[str, object]) -> int:
    """Replace ``{{column_name}}`` tokens in body paragraphs and tables."""
    normalized = _string_values(values)
    count = 0
    for paragraph in document.paragraphs:
        count += _replace_in_paragraph(paragraph, normalized)
    for table in document.tables:
        for paragraph in _iter_table_paragraphs(table):
            count += _replace_in_paragraph(paragraph, normalized)
    return count


def generate_document(template_bytes: bytes, values: Mapping[str, object]) -> bytes:
    document = Document(io.BytesIO(template_bytes))
    replace_placeholders(document, values)
    output = io.BytesIO()
    document.save(output)
    return output.getvalue()


def _safe_filename(value: object, fallback: str) -> str:
    text = str(value or "").strip()
    text = re.sub(r"[^A-Za-z0-9._ -]+", "", text).strip().replace(" ", "-")
    return text[:80] or fallback


def make_zip(
    template_bytes: bytes,
    records: Sequence[Mapping[str, object]],
) -> tuple[bytes, list[dict[str, str]]]:
    """Generate one prescription document per record and package them in a ZIP."""
    archive_buffer = io.BytesIO()
    manifest: list[dict[str, str]] = []

    with zipfile.ZipFile(archive_buffer, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for index, record in enumerate(records, start=1):
            rendered = generate_document(template_bytes, record)
            identity = (
                record.get("patient_name")
                or record.get("examinee_name")
                or record.get("name")
                or f"prescription-{index}"
            )
            stem = _safe_filename(identity, f"prescription-{index}")
            filename = f"{index:03d}-{stem}.docx"
            archive.writestr(filename, rendered)
            manifest.append({"row": str(index), "file": filename})

        manifest_text = "row,file\n" + "".join(
            f'{item["row"]},{item["file"]}\n' for item in manifest
        )
        archive.writestr("manifest.csv", manifest_text.encode("utf-8"))

    return archive_buffer.getvalue(), manifest


def _records_from_dataframe(frame) -> list[dict[str, object]]:
    clean = frame.where(frame.notna(), "")
    return clean.to_dict(orient="records")


def _read_source_file(source):
    import pandas as pd

    suffix = Path(source.name).suffix.lower()
    if suffix == ".csv":
        return pd.read_csv(source, dtype=str).fillna("")
    return pd.read_excel(source, dtype=str).fillna("")


def render_generate_tab() -> None:
    import streamlit as st

    templates, status = get_all_templates()
    st.caption(status)

    selected_template_bytes = None
    if templates:
        labels = ["Upload a one-time prescription form"] + [template.name for template in templates]
        selected = st.selectbox("Prescription form", labels)
        if selected == labels[0]:
            uploaded_template = st.file_uploader("Vaccine prescription Word template", type=["docx"], key="one_time_template")
            if uploaded_template is not None:
                selected_template_bytes = uploaded_template.getvalue()
        else:
            template = next(item for item in templates if item.name == selected)
            selected_template_bytes = get_template_bytes(template)
            if template.description:
                st.caption(template.description)
    else:
        uploaded_template = st.file_uploader("Vaccine prescription Word template", type=["docx"], key="fallback_template")
        if uploaded_template is not None:
            selected_template_bytes = uploaded_template.getvalue()

    source = st.file_uploader("Prescription data", type=["xlsx", "xlsm", "xls", "csv"])
    if selected_template_bytes is None or source is None:
        st.info("Choose a saved prescription form (or upload one) and add prescription data to continue.")
        return

    try:
        frame = _read_source_file(source)
    except Exception as exc:
        st.error(f"Could not read prescription data: {exc}")
        return

    if frame.empty:
        st.warning("The uploaded spreadsheet has no prescription rows.")
        return

    st.subheader("Prescription Preview")
    st.dataframe(frame, use_container_width=True, hide_index=True)
    st.caption("Template tokens use spreadsheet column names, for example {{patient_name}} or {{vaccine}}.")

    if st.button("Generate Vaccine Prescriptions", type="primary"):
        try:
            zip_bytes, manifest = make_zip(selected_template_bytes, _records_from_dataframe(frame))
            st.success(f"Generated {len(manifest)} vaccine prescription document(s).")
            st.download_button(
                "Download ZIP",
                data=zip_bytes,
                file_name=f"vaccine-prescriptions-{date.today().isoformat()}.zip",
                mime="application/zip",
            )
        except Exception as exc:
            st.error(f"Prescription generation failed: {exc}")


def render_configure_tab() -> None:
    import streamlit as st

    st.subheader("Saved Prescription Forms")
    templates, status = get_all_templates()
    st.caption(status)
    if templates:
        st.dataframe(
            [{"Name": t.name, "Description": t.description, "Filename": t.filename} for t in templates],
            use_container_width=True,
            hide_index=True,
        )

    st.subheader("Add Prescription Form")
    with st.form("save_vaccine_template", clear_on_submit=True):
        name = st.text_input("Form name")
        description = st.text_area("Description")
        uploaded = st.file_uploader("Prescription form (.docx)", type=["docx"])
        submitted = st.form_submit_button("Save form to Neon")

    if submitted:
        if not database_configured():
            st.error("Neon is not connected. Add DATABASE_URL in Render before saving forms.")
            return
        if not name.strip() or uploaded is None:
            st.error("Form name and .docx file are required.")
            return
        try:
            save_template_to_neon(name.strip(), description.strip(), uploaded.name, uploaded.getvalue())
            st.success("Prescription form saved permanently in Neon.")
            st.rerun()
        except Exception as exc:
            st.error(f"Could not save prescription form: {exc}")


def main() -> None:
    import streamlit as st

    from ui_experience import apply_luminous_ui, render_landing_page

    st.set_page_config(
        page_title="Vaccine Prescription Generator",
        page_icon="💉",
        layout="wide",
        initial_sidebar_state="collapsed",
    )
    apply_luminous_ui()

    if st.query_params.get("view") != "app":
        render_landing_page()

    st.markdown(
        """
        <div class="hero">
          <h1>Vaccine Prescription Generator</h1>
          <p>Generate vaccine prescriptions from saved Word forms in the Neon library. Use <code>{{column_name}}</code> tokens, then generate one document per spreadsheet row.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.button("Return to landing page"):
        st.query_params.clear()
        st.rerun()

    tab_generate, tab_forms = st.tabs(["Generate Prescriptions", "Prescription Forms"])
    with tab_generate:
        render_generate_tab()
    with tab_forms:
        render_configure_tab()


if __name__ == "__main__":
    main()
