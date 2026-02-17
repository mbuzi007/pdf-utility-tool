import streamlit as st
from pypdf import PdfReader, PdfWriter
import io

st.set_page_config(
    page_title="PDF Utility Tool",
    page_icon="📄",
    layout="wide"
)

# ==============================
# Utility Functions
# ==============================

def parse_page_input(input_str, max_pages):
    pages = set()
    parts = input_str.split(',')

    for part in parts:
        part = part.strip()
        if '-' in part:
            start, end = part.split('-')
            start, end = int(start), int(end)
            if start > end:
                raise ValueError("Invalid range: start page greater than end page.")
            for p in range(start, end + 1):
                if 1 <= p <= max_pages:
                    pages.add(p)
        else:
            p = int(part)
            if 1 <= p <= max_pages:
                pages.add(p)

    return sorted(pages)


def merge_pdfs(files):
    writer = PdfWriter()

    for file in files:
        reader = PdfReader(file)
        for page in reader.pages:
            writer.add_page(page)

    output = io.BytesIO()
    writer.write(output)
    output.seek(0)
    return output


def extract_pages(file, pages):
    reader = PdfReader(file)
    writer = PdfWriter()

    for page_num in pages:
        writer.add_page(reader.pages[page_num - 1])

    output = io.BytesIO()
    writer.write(output)
    output.seek(0)
    return output


# ==============================
# UI
# ==============================

st.title("📄 PDF Utility Tool")
st.markdown("Secure internal tool to merge or extract pages from PDF documents.")

tab1, tab2 = st.tabs(["🔍 Extract Pages", "📎 Merge PDFs"])


# ==========================================
# EXTRACT PAGES
# ==========================================
with tab1:
    st.subheader("Extract Specific Pages")

    uploaded_file = st.file_uploader(
        "Upload a PDF",
        type="pdf",
        key="extract"
    )

    page_input = st.text_input(
        "Enter pages (e.g. 1,3-5)",
        placeholder="Example: 1, 2-4"
    )

    if st.button("Extract Pages", type="primary"):
        if not uploaded_file:
            st.warning("Please upload a PDF.")
        elif not page_input:
            st.warning("Please enter page numbers.")
        else:
            try:
                reader = PdfReader(uploaded_file)
                max_pages = len(reader.pages)

                pages = parse_page_input(page_input, max_pages)
                output = extract_pages(uploaded_file, pages)

                st.success(f"Successfully extracted {len(pages)} page(s).")

                st.download_button(
                    label="Download Extracted PDF",
                    data=output,
                    file_name=f"{uploaded_file.name.replace('.pdf','')}_extracted.pdf",
                    mime="application/pdf"
                )

            except Exception as e:
                st.error(f"Error: {str(e)}")


# ==========================================
# MERGE PDFs
# ==========================================
with tab2:
    st.subheader("Merge Multiple PDFs")

    merge_files = st.file_uploader(
        "Upload PDFs (drag to reorder)",
        type="pdf",
        accept_multiple_files=True,
        key="merge"
    )

    if st.button("Merge PDFs", type="primary"):
        if not merge_files or len(merge_files) < 2:
            st.warning("Please upload at least two PDFs.")
        else:
            try:
                output = merge_pdfs(merge_files)

                st.success("PDFs merged successfully!")

                st.download_button(
                    label="Download Merged PDF",
                    data=output,
                    file_name="merged_document.pdf",
                    mime="application/pdf"
                )

            except Exception as e:
                st.error(f"Error: {str(e)}")
