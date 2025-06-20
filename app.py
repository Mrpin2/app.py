# app.py

import streamlit as st
from pypdf import PdfWriter, PdfReader
import io

# --- Function to Reduce PDF Size (Lossless Only) ---
def reduce_pdf_size_lossless(uploaded_file):
    """
    Reduces the size of a PDF file using ONLY lossless pypdf methods.
    Image quality is NOT altered.

    Args:
        uploaded_file: A Streamlit UploadedFile object.

    Returns:
        tuple: A tuple containing (io.BytesIO object of compressed PDF, original_size_bytes, compressed_size_bytes).
               Returns (None, None, None) if an error occurs.
    """
    try:
        original_pdf_bytes = uploaded_file.getvalue()
        original_size_bytes = len(original_pdf_bytes)

        # Re-read the PDF for processing with PdfReader
        # Using io.BytesIO(original_pdf_bytes) ensures that if the original
        # uploaded_file object is consumed elsewhere, we still have the data.
        reader = PdfReader(io.BytesIO(original_pdf_bytes))
        writer = PdfWriter()

        # Iterate through each page and apply lossless compression
        for page in reader.pages:
            # Apply lossless compression to content streams (text, lines, etc.)
            # We use level=9 for maximum lossless compression.
            page.compress_content_streams(level=9)
            writer.add_page(page)

        # Optimize the PDF structure by removing duplicate and unused objects
        writer.compress_identical_objects(remove_identicals=True, remove_orphans=True)

        # Save the compressed PDF to a BytesIO object in memory
        output_pdf_bytes = io.BytesIO()
        writer.write(output_pdf_bytes)
        output_pdf_bytes.seek(0)  # Rewind to the beginning for reading/downloading
        compressed_size_bytes = len(output_pdf_bytes.getvalue())

        return output_pdf_bytes, original_size_bytes, compressed_size_bytes

    except Exception as e:
        st.error(f"An error occurred during PDF processing: {e}. Please ensure it's a valid PDF.")
        return None, None, None

# --- Streamlit UI Layout ---
st.set_page_config(
    layout="centered", # Can be "wide" or "centered"
    page_title="PDF Size Reducer (Lossless)",
    page_icon="📄" # Optional: an emoji for the browser tab icon
)

st.title("📄 PDF Size Reducer (Lossless)")
st.markdown("Upload a PDF file to reduce its size **without altering any content quality**.")
st.markdown("This app uses only lossless compression, meaning no images or text will be degraded. We will show you the maximum possible reduction.")

# File Uploader
uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

if uploaded_file is not None:
    original_size_bytes_display = len(uploaded_file.getvalue()) # For initial display
    st.info(f"Original file size: **{original_size_bytes_display / (1024*1024):.2f} MB**")

    st.subheader("Compression Process (Lossless Only)")
    st.markdown("This tool will apply the maximum possible lossless compression to your PDF.")
    st.warning("Please note: Achieving a specific large percentage reduction, or reaching a very small target size like 10MB, is often not possible with lossless compression alone, especially for PDFs with many high-resolution images. Lossless methods remove redundant data, not essential content.")

    # Button to trigger compression
    if st.button("Compress PDF (Lossless)", type="primary"):
        with st.spinner("Compressing PDF... This might take a moment for larger files."):
            compressed_pdf_bytes, actual_original_size_bytes, actual_compressed_size_bytes = reduce_pdf_size_lossless(uploaded_file)

            if compressed_pdf_bytes:
                # Calculate reduction based on returned sizes for accuracy
                reduction_percentage = ((actual_original_size_bytes - actual_compressed_size_bytes) / actual_original_size_bytes) * 100

                st.success("PDF compressed successfully!")
                st.write(f"**Compressed file size:** {actual_compressed_size_bytes / (1024*1024):.2f} MB")
                st.write(f"**Achieved Lossless Reduction:** {reduction_percentage:.2f}%")

                # Check against the 10MB goal and provide feedback
                if actual_compressed_size_bytes < (10 * 1024 * 1024): # 10 MB in bytes
                    st.success(f"🎉 Great news! The PDF is now under 10MB (specifically {actual_compressed_size_bytes / (1024*1024):.2f} MB) while maintaining original quality.")
                else:
                    st.info(f"The PDF was compressed to {actual_compressed_size_bytes / (1024*1024):.2f} MB. This is the maximum reduction achievable **without altering quality**. If you need further reduction (e.g., to reach a much smaller target), some quality degradation (e.g., in embedded images) would be necessary, which this app currently avoids.")

                # Download button
                st.download_button(
                    label="Download Compressed PDF",
                    data=compressed_pdf_bytes,
                    file_name="compressed_pdf_lossless.pdf",
                    mime="application/pdf",
                    help="Click to download your compressed PDF."
                )
            else:
                # Error message already shown in reduce_pdf_size_lossless function
                pass

st.markdown("---")
st.markdown("### How this Lossless Compressor Works:")
st.markdown("""
- **Content Stream Compression:** Applies advanced zlib compression to text, vector graphics, and other content streams within the PDF. This method **does not lose any detail or quality**; it simply stores the data more efficiently.
- **Object Optimization:** Scans the PDF for duplicate objects (e.g., the same font embedded multiple times) and unused data, removing them to achieve a smaller file size **without altering the visual or textual content**.
- **No Image Quality Alteration:** Unlike other compressors, this tool specifically avoids re-compressing images at lower quality. This guarantees the original visual fidelity of any photos or scanned documents in your PDF.
""")
st.markdown("Built with ❤️ using [Streamlit](https://streamlit.io/) and [`pypdf`](https://pypdf.readthedocs.io/en/stable/).")
