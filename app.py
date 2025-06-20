# app.py

import streamlit as st
from pypdf import PdfWriter, PdfReader
import io

# --- Function to Reduce PDF Size ---
def reduce_pdf_size(uploaded_file, compression_level=9, image_quality=80):
    """
    Reduces the size of a PDF file using pypdf.

    Args:
        uploaded_file: A Streamlit UploadedFile object.
        compression_level (int): Zlib compression level for content streams (0-9).
        image_quality (int): JPEG quality for images (0-100).

    Returns:
        io.BytesIO: A BytesIO object containing the compressed PDF data.
    """
    try:
        reader = PdfReader(uploaded_file)
        writer = PdfWriter()

        # Iterate through each page and apply compression
        for page in reader.pages:
            # Apply lossless compression to content streams (text, lines, etc.)
            # This is generally very effective without quality loss.
            page.compress_content_streams(level=compression_level)

            # Optional: Reduce image quality if images are present on the page
            # This can significantly reduce file size but introduces some quality loss.
            for img in page.images:
                try:
                    # 'img.image' gives the PIL Image object
                    img.replace(img.image, quality=image_quality)
                except Exception as e:
                    # Catch specific errors related to image processing if needed
                    # For simplicity, we just warn the user.
                    st.warning(f"Could not compress an image on a page. Image might be unsupported format or malformed. Error: {e}")
            writer.add_page(page)

        # Optimize the PDF structure by removing duplicate and unused objects
        writer.compress_identical_objects(remove_identicals=True, remove_orphans=True)

        # Save the compressed PDF to a BytesIO object in memory
        output_pdf_bytes = io.BytesIO()
        writer.write(output_pdf_bytes)
        output_pdf_bytes.seek(0)  # Rewind to the beginning for reading/downloading
        return output_pdf_bytes

    except Exception as e:
        st.error(f"An error occurred during PDF processing: {e}")
        return None

# --- Streamlit UI Layout ---
st.set_page_config(
    layout="centered", # Can be "wide" or "centered"
    page_title="PDF Size Reducer",
    page_icon="📄" # Optional: an emoji for the browser tab icon
)

st.title("📄 PDF Size Reducer")
st.markdown("Upload a PDF file, adjust compression settings, and download a smaller version.")

# File Uploader
uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

if uploaded_file is not None:
    # Get original file size
    original_size = len(uploaded_file.getvalue())
    st.info(f"Original file size: **{original_size / (1024*1024):.2f} MB**")

    st.subheader("Compression Options")
    st.markdown("Adjust these sliders to control the level of compression. Higher compression can mean smaller files but might take longer or reduce image quality.")

    # Compression Level for Content Streams (text, vectors)
    compression_level = st.slider(
        "Content Stream Compression (Lossless)",
        min_value=0, max_value=9, value=9, step=1,
        help="Applies lossless compression to text and vector graphics. 0 = no compression, 9 = highest compression (might be slower)."
    )

    # Image Quality for Embedded Images
    image_quality = st.slider(
        "Image Quality (Lossy)",
        min_value=0, max_value=100, value=80, step=5,
        help="Reduces the quality of embedded images (like JPEG). 100 = original quality, 0 = lowest quality (most compression). Set to 100 to avoid image compression."
    )

    # Button to trigger compression
    if st.button("Compress PDF", type="primary"):
        with st.spinner("Compressing PDF... This might take a moment for large files."):
            compressed_pdf_bytes = reduce_pdf_size(uploaded_file, compression_level, image_quality)

            if compressed_pdf_bytes:
                compressed_size = len(compressed_pdf_bytes.getvalue())
                reduction_percentage = ((original_size - compressed_size) / original_size) * 100

                st.success("PDF compressed successfully!")
                st.write(f"**Compressed file size:** {compressed_size / (1024*1024):.2f} MB")
                st.write(f"**Size Reduction:** {reduction_percentage:.2f}%")

                # Download button
                st.download_button(
                    label="Download Compressed PDF",
                    data=compressed_pdf_bytes,
                    file_name="compressed_pdf.pdf",
                    mime="application/pdf",
                    help="Click to download your compressed PDF."
                )
            else:
                st.error("Failed to compress PDF. Please check the console for errors or try a different file.")

st.markdown("---")
st.markdown("Built with ❤️ using [Streamlit](https://streamlit.io/) and [`pypdf`](https://pypdf.readthedocs.io/en/stable/).")
st.markdown("### How it works:")
st.markdown("""
- **Content Stream Compression (Lossless):** Applies zlib compression to text, vector graphics, and other content streams within the PDF. This doesn't lose any detail.
- **Image Quality (Lossy):** Re-compresses images within the PDF to a lower quality (like a lower quality JPEG). This can significantly reduce file size but will make images less sharp.
- **Object Optimization:** Removes duplicate objects and unused data within the PDF structure.
""")
