# app.py

import streamlit as st
from pypdf import PdfWriter, PdfReader
import io
from PIL import Image # New import for image processing

# --- Configuration for your App ---
APP_TITLE = "Super Simple PDF Shrinker! 📄✨"
APP_ICON = "🎈"
YOUR_LINKEDIN_URL = "https://www.linkedin.com/in/rajeevbhandari87/"
# IMPORTANT: Ensure 'Logo.png' is in the ROOT of your GitHub repository,
# alongside app.py, for Streamlit Cloud to find it.
YOUR_LOGO_PATH = "Logo.png"

# --- Function to Shrink PDF Size (The Engine Room) ---
def reduce_pdf_size(uploaded_file, compression_level=9, image_quality=80):
    """
    This magical function takes your PDF and makes it smaller!
    It works by squishing things like text and pictures inside.

    Args:
        uploaded_file: The PDF file you uploaded.
        compression_level (int): How much to squish text and graphics (0-9, 9 is most).
                                 This doesn't make your images blurry!
        image_quality (int): How much to squish pictures (0-100, 0 is most squished/blurry).
                             This is where you save BIG on file size!

    Returns:
        tuple: (The shrunken PDF, original size in bytes, new size in bytes).
               Returns (None, None, None) if something goes wrong.
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

            # --- Advanced Image Compression (Conditional on Image Type and Quality Setting) ---
            if image_quality < 100: # Only try to compress if quality reduction is requested
                # Collect images into a list to avoid issues if iteration is modified by replacement
                images_on_page = list(current_page_in_writer.images)

                for pypdf_img_obj in images_on_page: # Renamed variable for clarity: this is pypdf's Image object
                    try:
                        # Ensure the object actually has the .get() method we expect from pypdf.image.Image
                        if not hasattr(pypdf_img_obj, 'get'):
                            st.warning(f"⚠️ Skipped an image on a page: Unexpected object type encountered. Cannot process its properties.")
                            continue # Skip this image if it's not a standard pypdf image object

                        # Get image filter/type as a string for easier comparison
                        img_filter_obj = pypdf_img_obj.get("/Filter")
                        img_filter_str = str(img_filter_obj) if img_filter_obj else "/Unknown"

                        # Get the actual Pillow Image object from pypdf's wrapper
                        pil_image_data = pypdf_img_obj.image

                        if pil_image_data is None: # If Pillow couldn't extract an image
                            st.info(f"ℹ️ An image on a page was found but its data could not be processed. Skipping.")
                            continue

                        # If it's a JPEG or JPEG 2000, use pypdf's direct quality setting
                        if "/DCTDecode" in img_filter_str or "/JPXDecode" in img_filter_str:
                            pypdf_img_obj.replace(pil_image_data, quality=image_quality)
                        # If it's a non-JPEG and image_quality is aggressive (<= 40%), try converting to JPEG
                        elif image_quality <= 40: # Apply aggressive conversion if quality is low
                            output_img_bytes = io.BytesIO()
                            # Convert to RGB if not already (JPEGs are typically RGB)
                            rgb_image = pil_image_data.convert("RGB")
                            rgb_image.save(output_img_bytes, format="JPEG", quality=image_quality)
                            output_img_bytes.seek(0)
                            # Replace the image with the new JPEG data and explicitly set filter
                            pypdf_img_obj.replace(output_img_bytes.getvalue(), filter='/DCTDecode')
                        else:
                            # Inform user if not JPEG and not aggressive enough quality for conversion
                            st.info(f"ℹ️ An image on a page was not compressed because it's not a JPEG "
                                    f"and your 'Picture Quality' setting ({image_quality}%) is not low enough "
                                    f"to trigger aggressive conversion (requires <= 40%).")

                    except Exception as e:
                        # This catches any other unexpected errors during image processing
                        st.warning(f"⚠️ General error trying to shrink an image on a page. "
                                   f"This might be due to a very unusual image format or structure, "
                                   f"or an issue with Pillow. Error: {type(e).__name__}: {e}")
                        # You can uncomment the line below for more detailed debugging in logs
                        # print(f"DEBUG: Image processing error: {e}")

        # Optimize the PDF structure by removing duplicate and unused objects
        writer.compress_identical_objects(remove_identicals=True, remove_orphans=True)

        # Save the compressed PDF to a BytesIO object in memory
        output_pdf_bytes = io.BytesIO()
        writer.write(output_pdf_bytes)
        output_pdf_bytes.seek(0)  # Rewind to the beginning for reading/downloading
        compressed_size_bytes = len(output_pdf_bytes.getvalue())

        return output_pdf_bytes, original_size_bytes, compressed_size_bytes

    except Exception as e:
        st.error(f"Oh no! Something went wrong during PDF processing: {e}. "
                 "This might be due to a corrupted or unusual PDF structure. Please try a different PDF.")
        return None, None, None

# --- Streamlit User Interface (What you see!) ---

st.set_page_config(
    layout="centered",
    page_title=APP_TITLE,
    page_icon=APP_ICON
)

# --- Logo Centering ---
col_logo_left, col_logo_center, col_logo_right = st.columns([1, 0.5, 1])

with col_logo_center:
    try:
        st.image(YOUR_LOGO_PATH, width=150)
    except FileNotFoundError:
        st.warning("Logo file 'Logo.png' not found. Make sure it's in the root of your GitHub repo.")
    except Exception as e:
        st.error(f"An unexpected error occurred while loading the logo: {e}")

st.title(f"{APP_ICON} {APP_TITLE}")
st.markdown("Got a PDF that's too big? Let's make it smaller! "
            "Perfect for emails, uploads, and saving space. ✨")

# --- 1. Upload Your PDF Here Section ---
st.markdown("---")
st.subheader("1. Upload Your PDF Here 👇")

uploaded_file = st.file_uploader("Drag and drop your PDF or click to browse", type="pdf")

if uploaded_file is not None:
    original_size_bytes_display = len(uploaded_file.getvalue())
    st.info(f"**Original PDF Size:** **`{original_size_bytes_display / (1024*1024):.2f} MB`** 📏")

    st.markdown("---")
    st.subheader("2. Choose How Small You Want It! 👇")
    st.markdown("This tool works best by adjusting **Picture Quality**. The **lower** the quality value, the **smaller** the file (but pictures might get a little blurry).")
    st.markdown("If you need a very small file (e.g., under 10MB), you'll likely need to reduce the Picture Quality significantly.")

    # --- Conditional Warning about Aggressive Compression ---
    st.info("""
    **💡 Tip for Super Small Files:** If you set 'Picture Quality' to **40% or lower**, the app will try to convert *all* images (even non-JPEGs like PNGs) into lower quality JPEGs for maximum shrinkage. This can sometimes make text or sharp graphics look blurry, but it's great for photos and achieving very small file sizes!
    """)

    # --- Simplified Compression Control ---
    quality_setting = st.slider(
        "🖼️ **Picture Quality** (Lower Value = Smaller File)",
        min_value=0, max_value=100, value=60, step=5,
        help="This controls the quality of images in your PDF. "
             "**100 = Best Quality (largest file)**; **0 = Lowest Quality (smallest file, pictures might be very blurry)**. "
             "Drag this slider towards 0 for the biggest file size reduction!"
    )

    compression_level = 9
    image_quality = quality_setting

    st.markdown(f"**Your Current Picture Quality Setting:** **`{quality_setting}%`** (Drag left for smaller files)")


    if st.button("🚀 Shrink My PDF Now!", type="primary"):
        with st.spinner("Processing... Your PDF is getting its workout! 💪"):
            compressed_pdf_bytes, actual_original_size_bytes, actual_compressed_size_bytes = reduce_pdf_size(
                uploaded_file, compression_level, image_quality
            )

            if compressed_pdf_bytes:
                reduction_percentage = ((actual_original_size_bytes - actual_compressed_size_bytes) / actual_original_size_bytes) * 100

                st.success("🎉 Your PDF has been successfully shrunk!")

                # --- Dynamic Size Animation / Feel the Difference ---
                st.markdown("### **Feel the Difference!**")
                col1, col2, col3 = st.columns([1, 0.5, 1])

                with col1:
                    st.metric(label="Original Size", value=f"{actual_original_size_bytes / (1024*1024):.2f} MB 📊")
                with col2:
                    st.markdown("## ➡️")
                with col3:
                    st.metric(label="Shrunk Size", value=f"{actual_compressed_size_bytes / (1024*1024):.2f} MB 👇")

                st.markdown(f"### **🥳 You Saved: `{reduction_percentage:.2f}%` of the original size!**")

                # Provide feedback on the 10MB goal
                if actual_compressed_size_bytes < (10 * 1024 * 1024):
                    st.balloons()
                    st.success(f"✅ Success! Your PDF is now under 10MB ({actual_compressed_bytes / (1024*1024):.2f} MB)! Perfect for emails!")
                else:
                    st.info(f"Your PDF is now {actual_compressed_size_bytes / (1024*1024):.2f} MB. If you need it even smaller, try reducing the 'Picture Quality' slider further (drag it closer to 0).")


                st.download_button(
                    label="⬇️ Download Your Shrunken PDF",
                    data=compressed_pdf_bytes,
                    file_name=f"shrunk_{uploaded_file.name}",
                    mime="application/pdf",
                    help="Click to download your newly shrunken PDF."
                )

                # --- Humorous and Assuring Safety Message ---
                st.markdown("---")
                st.success("✨ **Privacy Check Complete!** ✨")
                st.info("Your document was processed directly in our app's memory and **was never saved** to any server disk. "
                        "Once you download it, your original file vanishes like magic! Poof! 💨")

else: # This block displays when no file is uploaded yet
    st.markdown("---")

    st.subheader("💡 How This PDF Shrinker Works:")
    st.markdown("""
    - **Smart Text & Graphics Shrinker:** This feature tidies up text and drawings without any loss in quality. It's like expertly packing a suitcase – everything fits better!
    - **Picture Quality (Your Main Shrink Lever):** This is where the magic happens for big PDFs with images. It gently reduces picture quality to make the file much smaller. Less quality = much smaller file!
    - **Digital Declutter:** The tool also cleans up your PDF by removing any hidden, unused bits, making it even lighter.
    """)
    st.markdown("---")

# --- Footer with your information ---
st.markdown("Made with ❤️ by Rajeev Bhandari")
st.markdown(f"Connect with me on [LinkedIn]({YOUR_LINKEDIN_URL})")
