# app.py

import streamlit as st
from pypdf import PdfWriter, PdfReader
import io

# --- Function to Reduce PDF Size (With Lossy Image Compression Option) ---
def reduce_pdf_size(uploaded_file, compression_level=9, image_quality=80):
    """
    Reduces the size of a PDF file using lossless content stream compression
    and optional lossy image compression.

    Args:
        uploaded_file: A Streamlit UploadedFile object.
        compression_level (int): Zlib compression level for content streams (0-9).
        image_quality (int): JPEG quality for images (0-100). Lower means more compression/less quality.

    Returns:
        tuple: A tuple containing (io.BytesIO object of compressed PDF, original_size_bytes, compressed_size_bytes).
               Returns (None, None, None) if an error occurs.
    """
    try:
        original_pdf_bytes = uploaded_file.getvalue()
        original_size_bytes = len(original_pdf_bytes)

        reader = PdfReader(io.BytesIO(original_pdf_bytes))
        writer = PdfWriter()

        # Iterate through each page
        for page_num in range(len(reader.pages)):
            page_from_reader = reader.pages[page_num]

            # Add the page to the writer first to ensure it's in the correct context
            writer.add_page(page_from_reader)

            # Access the newly added page in the writer's context
            current_page_in_writer = writer.pages[-1]

            # Apply lossless compression to content streams (text, lines, etc.)
            current_page_in_writer.compress_content_streams(level=compression_level)

            # Optional: Reduce image quality if images are present and image_quality < 100
            if image_quality < 100:
                for img in current_page_in_writer.images:
                    try:
                        # 'img.image' gives the PIL Image object
                        img.replace(img.image, quality=image_quality)
                    except Exception as e:
                        st.warning(f"Could not re-compress an image on a page (might be unsupported format or malformed). Error: {e}")

        # Optimize the PDF structure by removing duplicate and unused objects
        writer.compress_identical_objects(remove_identicals=True, remove_orphans=True)

        # Save the compressed PDF to a BytesIO object in memory
        output_pdf_bytes = io.BytesIO()
        writer.write(output_pdf_bytes)
        output_pdf_bytes.seek(0)  # Rewind to the beginning for reading/downloading
        compressed_size_bytes = len(output_pdf_bytes.getvalue())

        return output_pdf_bytes, original_size_bytes, compressed_size_bytes

    except Exception as e:
        st.error(f"An error occurred during PDF processing: {e}. This might be due to a corrupted or unusual PDF structure. Please try a different PDF.")
        return None, None, None

# --- Streamlit UI Layout ---
st.set_page_config(
    layout="centered",
    page_title="PDF Size Reducer",
    page_icon="📄"
)

st.title("📄 PDF Size Reducer")
st.markdown("Upload a PDF file and adjust settings to reduce its size. You can choose to sacrifice image quality for smaller files.")

# File Uploader
uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

if uploaded_file is not None:
    original_size_bytes_display = len(uploaded_file.getvalue())
    st.info(f"Original file size: **{original_size_bytes_display / (1024*1024):.2f} MB**")

    st.subheader("Compression Options")
    st.markdown("Adjust these sliders to control the level of compression. Lower image quality for smaller files.")

    # Content Stream Compression (Lossless)
    compression_level = st.slider(
        "Content Stream Compression (Lossless)",
        min_value=0, max_value=9, value=9, step=1,
        help="Applies lossless compression to text and vector graphics. 0 = no compression, 9 = highest compression (might be slower). This does NOT affect image quality."
    )

    # Image Quality (Lossy) - This is your 'lever' for desired size
    image_quality = st.slider(
        "Image Quality (Lossy) - Your Size Lever",
        min_value=0, max_value=100, value=80, step=5,
        help="Controls the quality of embedded images (like JPEG). 100 = original quality, 0 = lowest quality (most size reduction, but significant degradation). This is the primary control for reducing file size if your PDF contains images."
    )
    st.markdown(f"**Current Image Quality Setting:** {image_quality}% (Lower % = smaller file, but more visual quality loss)")


    if st.button("Compress PDF", type="primary"):
        with st.spinner("Compressing PDF... This might take a moment for larger files."):
            # Call the function with both compression_level and image_quality
            compressed_pdf_bytes, actual_original_size_bytes, actual_compressed_size_bytes = reduce_pdf_size(
                uploaded_file, compression_level, image_quality
            )

            if compressed_pdf_bytes:
                reduction_percentage = ((actual_original_size_bytes - actual_compressed_size_bytes) / actual_original_size_bytes) * 100

                st.success("PDF compressed successfully!")
                st.write(f"**Compressed file size:** {actual_compressed_size_bytes / (1024*1024):.2f} MB")
                st.write(f"**Size Reduction:** {reduction_percentage:.2f}%")

                # Provide feedback on the 10MB goal
                if actual_compressed_size_bytes < (10 * 1024 * 1024): # 10 MB in bytes
                    st.success(f"🎉 Success! The PDF is now under your 10MB target ({actual_compressed_size_bytes / (1024*1024):.2f} MB) with the chosen settings.")
                else:
                    st.info(f"The PDF was compressed to {actual_compressed_size_bytes / (1024*1024):.2f} MB. If you need it even smaller, try reducing the 'Image Quality' slider further.")

                st.download_button(
                    label="Download Compressed PDF",
                    data=compressed_pdf_bytes,
                    file_name="compressed_pdf.pdf", # Changed filename back to generic
                    mime="application/pdf",
                    help="Click to download your compressed PDF."
                )
            # Error handling in function, so no 'else' needed here

else: # This block displays when no file is uploaded yet
    st.markdown("---")
    st.markdown("### How this PDF Compressor Works:")
    st.markdown("""
    - **Content Stream Compression (Lossless):** Applies advanced zlib compression to text, vector graphics, and other content streams within the PDF. This method **does not lose any detail or quality**; it simply stores the data more efficiently.
    - **Image Quality (Lossy):** This is your main tool for significant size reduction if your PDF contains images. It re-compresses embedded images (like photos or scanned documents) to a lower quality. **Lowering this value will reduce visual fidelity but greatly reduce file size.**
    - **Object Optimization:** Scans the PDF for duplicate objects (e.g., the same font embedded multiple times) and unused data, removing them to achieve a smaller file size **without altering the visual or textual content**.
    """)
    st.markdown("Built with ❤️ using [Streamlit](https://streamlit.io/) and [`pypdf`](https://pypdf.readthedocs.io/en/stable/).")
