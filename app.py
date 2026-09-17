from __future__ import annotations

import io
import re
import zipfile
from datetime import date
from pathlib import Path
from typing import Mapping, Sequence

from docx import Document

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


def main() -> None:
    import pandas as pd
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
          <p>Complete vaccine prescription Word templates from spreadsheet data. Use <code>{{column_name}}</code> tokens in the template, then generate one document per row.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.button("Return to landing page"):
        st.query_params.clear()
        st.rerun()

    template = st.file_uploader("Vaccine prescription Word template", type=["docx"])
    source = st.file_uploader("Prescription data", type=["xlsx", "xlsm", "xls", "csv"])

    if template is None or source is None:
        st.info("Upload a .docx prescription template and a spreadsheet to continue.")
        return

    try:
        suffix = Path(source.name).suffix.lower()
        if suffix == ".csv":
            frame = pd.read_csv(source, dtype=str).fillna("")
        else:
            frame = pd.read_excel(source, dtype=str).fillna("")
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
            zip_bytes, manifest = make_zip(template.getvalue(), _records_from_dataframe(frame))
            st.success(f"Generated {len(manifest)} vaccine prescription document(s).")
            st.download_button(
                "Download ZIP",
                data=zip_bytes,
                file_name=f"vaccine-prescriptions-{date.today().isoformat()}.zip",
                mime="application/zip",
            )
        except Exception as exc:
            st.error(f"Prescription generation failed: {exc}")


if __name__ == "__main__":
    main()
