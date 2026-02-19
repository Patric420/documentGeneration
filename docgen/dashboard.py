"""
Streamlit Dashboard for the Document Generation System.

Run with:
    streamlit run dashboard.py
"""

import base64
import logging
import os
import sys
import tempfile
from pathlib import Path

import streamlit as st

from utils.file_utils import extract_text
from classifier.classify import classify_document, extract_fields
from schema import DOCUMENT_SCHEMAS
from app import generate_document, validate_inputs, TEMPLATE_MAP
from exceptions import (
    DocumentGenerationError,
    TemplateNotFoundError,
    MissingRequiredFieldError,
    ValidationError,
)

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="DocGen – Document Generation",
    page_icon="📄",
    layout="wide",
)

# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
with st.sidebar:
    logo_path = Path("images/sample_asset_0_xref_36.jpeg")
    if logo_path.exists():
        st.image(str(logo_path), width=160)
    st.title("DocGen")
    st.caption("AI-powered document generation")
    st.divider()

    st.subheader("Supported Types")
    for doc_type in DOCUMENT_SCHEMAS:
        has_template = doc_type in TEMPLATE_MAP
        badge = "✅" if has_template else "🔜"
        st.markdown(f"{badge}  **{doc_type.replace('_', ' ')}**")

    st.divider()
    st.caption("Templates marked 🔜 are coming soon.")

# ---------------------------------------------------------------------------
# Session state defaults
# ---------------------------------------------------------------------------
_DEFAULTS = {
    "stage": "upload",       # upload → fields → done
    "doc_type": None,
    "extracted_text": None,
    "tmp_path": None,
    "output_pdf": None,
    "output_tex": None,
    "user_inputs": {},       # last-used field values for re-editing
}
for key, val in _DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = val


def _reset() -> None:
    """Reset the pipeline to the upload stage."""
    for key, val in _DEFAULTS.items():
        st.session_state[key] = val


# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------
st.title("📄 Document Generation Dashboard")
st.markdown("Upload a reference document, review the detected type, fill in the fields, and generate a branded PDF.")

# ---------------------------------------------------------------------------
# Stage 1 – Upload
# ---------------------------------------------------------------------------
st.header("1️⃣  Upload Document")
uploaded_file = st.file_uploader(
    "Choose a reference document (PDF, DOCX, or image)",
    type=["pdf", "docx", "png", "jpg", "jpeg"],
    key="file_uploader",
)

if uploaded_file and st.session_state.stage == "upload":
    suffix = Path(uploaded_file.name).suffix
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(uploaded_file.getvalue())
        st.session_state.tmp_path = tmp.name

    with st.spinner("Extracting text from document…"):
        try:
            st.session_state.extracted_text = extract_text(st.session_state.tmp_path)
        except Exception as e:
            st.error(f"Extraction failed: {e}")
            st.stop()

    st.success(f"Extracted **{len(st.session_state.extracted_text):,}** characters from *{uploaded_file.name}*")

    with st.spinner("Classifying document with Gemini AI…"):
        try:
            st.session_state.doc_type = classify_document(st.session_state.extracted_text)
        except Exception as e:
            st.error(f"Classification failed: {e}")
            st.stop()

    # Auto-populate form fields from the extracted text
    with st.spinner("Extracting field values from text…"):
        schema = DOCUMENT_SCHEMAS.get(st.session_state.doc_type, {})
        all_fields = schema.get("required", []) + schema.get("optional", [])
        st.session_state.user_inputs = extract_fields(
            st.session_state.extracted_text,
            st.session_state.doc_type,
            all_fields,
        )

    st.session_state.stage = "fields"
    st.rerun()

# ---------------------------------------------------------------------------
# Stage 2 – Fields & Generation
# ---------------------------------------------------------------------------
if st.session_state.stage in ("fields", "done"):
    st.header("2️⃣  Document Details")

    doc_type = st.session_state.doc_type
    col_info, col_preview = st.columns([1, 1])

    with col_info:
        st.subheader(f"Detected type: `{doc_type}`")
        has_template = doc_type in TEMPLATE_MAP
        if has_template:
            st.success("Template available — ready to generate.")
        else:
            st.warning("No template yet for this type. Generation will fail until a template is added.")

    with col_preview:
        with st.expander("Preview / edit extracted text", expanded=False):
            edited_text = st.text_area(
                "Extracted text",
                value=st.session_state.extracted_text,
                height=300,
                key="extracted_text_editor",
                help="Edit the extracted text to fix OCR errors or adjust content, then click Re-extract to update the fields.",
            )
            if edited_text != st.session_state.extracted_text:
                st.session_state.extracted_text = edited_text

            if st.button("🔄  Re-extract fields from text", use_container_width=True):
                with st.spinner("Re-extracting field values…"):
                    all_fields = (
                        DOCUMENT_SCHEMAS.get(doc_type, {}).get("required", [])
                        + DOCUMENT_SCHEMAS.get(doc_type, {}).get("optional", [])
                    )
                    st.session_state.user_inputs = extract_fields(
                        st.session_state.extracted_text,
                        doc_type,
                        all_fields,
                    )
                st.rerun()

    # ---- Build the editable field form (always visible) ----
    schema = DOCUMENT_SCHEMAS.get(doc_type, {"required": [], "optional": []})
    required_fields = schema.get("required", [])
    optional_fields = schema.get("optional", [])
    saved = st.session_state.user_inputs  # previously used values

    st.subheader("Fill in the fields")

    with st.form("field_form"):
        user_inputs: dict[str, str] = {}

        if required_fields:
            st.markdown("**Required fields**")
            cols = st.columns(min(len(required_fields), 3))
            for idx, field in enumerate(required_fields):
                with cols[idx % len(cols)]:
                    user_inputs[field] = st.text_input(
                        field.replace("_", " "),
                        value=saved.get(field, ""),
                        key=f"req_{field}",
                    )

        if optional_fields:
            st.markdown("**Optional fields**")
            cols = st.columns(min(len(optional_fields), 3))
            for idx, field in enumerate(optional_fields):
                with cols[idx % len(cols)]:
                    user_inputs[field] = st.text_input(
                        field.replace("_", " ") + " *(optional)*",
                        value=saved.get(field, ""),
                        key=f"opt_{field}",
                    )

        btn_label = "🚀  Generate Document" if st.session_state.stage == "fields" else "🔄  Regenerate with Changes"
        submitted = st.form_submit_button(btn_label, type="primary", use_container_width=True)

    if submitted:
        clean_inputs = {k: v for k, v in user_inputs.items() if v.strip()}

        try:
            validate_inputs(doc_type, clean_inputs)
        except MissingRequiredFieldError as e:
            st.error(f"Missing required fields: {', '.join(e.missing_fields)}")
            st.stop()
        except ValidationError as e:
            st.error(str(e))
            st.stop()

        with st.spinner("Generating PDF…"):
            try:
                _, output_pdf = generate_document(
                    st.session_state.tmp_path,
                    clean_inputs,
                    extracted_text=st.session_state.extracted_text,
                    doc_type=st.session_state.doc_type,
                )
                st.session_state.output_pdf = output_pdf
                st.session_state.output_tex = output_pdf.rsplit(".", 1)[0] + ".tex"
                st.session_state.user_inputs = clean_inputs
                st.session_state.stage = "done"
                st.rerun()
            except TemplateNotFoundError:
                st.error(f"No template available for **{doc_type}**. This type is not yet supported.")
                st.stop()
            except DocumentGenerationError as e:
                st.error(f"Generation failed: {e}")
                st.stop()

# ---------------------------------------------------------------------------
# Stage 3 – PDF Preview (edit fields above to regenerate)
# ---------------------------------------------------------------------------
if st.session_state.stage == "done" and st.session_state.output_pdf:
    st.header("3️⃣  Preview")

    pdf_path = Path(st.session_state.output_pdf)
    if not pdf_path.exists():
        st.error("PDF file not found on disk. It may have been cleaned up.")
        st.stop()

    st.success(f"**{st.session_state.doc_type.replace('_', ' ')}** generated successfully!  "
               f"Edit the fields above and click **Regenerate with Changes** to update.")

    # Embedded PDF preview
    pdf_bytes = pdf_path.read_bytes()
    b64_pdf = base64.b64encode(pdf_bytes).decode("utf-8")
    pdf_iframe = (
        f'<iframe src="data:application/pdf;base64,{b64_pdf}" '
        f'width="100%" height="700" style="border:1px solid #ddd; border-radius:4px;" '
        f'type="application/pdf"></iframe>'
    )
    st.markdown(pdf_iframe, unsafe_allow_html=True)

    # Action bar
    st.divider()
    act1, act2 = st.columns([1, 1])
    with act1:
        st.download_button(
            label="⬇️  Download PDF",
            data=pdf_bytes,
            file_name=f"{st.session_state.doc_type}.pdf",
            mime="application/pdf",
            use_container_width=True,
        )
    with act2:
        if st.button("🔄  Start Over", use_container_width=True):
            _reset()
            st.rerun()

# ---------------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------------
st.divider()
st.caption("DocGen © 2026 — AI-powered document generation system")
