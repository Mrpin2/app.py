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

        # Go through each page of your PDF
        for page_num in range(len(reader.pages)):
            page_from_reader = reader.pages[page_num]

            # Add the page to our new (soon-to-be-shrunken) PDF
            writer.add_page(page_from_reader)

            # Get the page we just added so we can work on it
            current_page_in_writer = writer.pages[-1]

            # Apply lossless compression to text, lines, etc.
            current_page_in_writer.compress_content_streams(level=compression_level)

            # --- Advanced Image Compression (Conditional on Image Type and Quality Setting) ---
            if image_quality < 100: # Only try to compress if quality reduction is requested
                for img in current_page_in_writer.images:
                    try:
                        # Attempt to re-compress all images
                        img_filter = img.get("/Filter", "/Unknown") # Get image filter/type
                        img_decode = img.get("/DecodeParms", {}) # Get decode parameters for image

                        # Check if it's already a JPEG or can be directly handled by pypdf's quality setting
                        if "/DCTDecode" in img_filter or "/JPXDecode" in img_filter: # DCTDecode for JPEG, JPXDecode for JPEG 2000
                            img.replace(img.image, quality=image_quality)
                        # If it's a non-JPEG and image_quality is aggressive, try converting to JPEG
                        elif image_quality <= 40: # Apply aggressive conversion if quality is low (e.g., <= 40%)
                            if isinstance(img.image, Image.Image): # Ensure it's a PIL Image object
                                output_img_bytes = io.BytesIO()
                                # Convert to RGB if not already (JPEGs are typically RGB)
                                rgb_image = img.image.convert("RGB")
                                rgb_image.save(output_img_bytes, format="JPEG", quality=image_quality)
                                output_img_bytes.seek(0)
                                # Replace the image with the new JPEG data
                                img.replace(output_img_bytes.getvalue(), filter='/DCTDecode')
                                # Note: This might overwrite other image properties not managed by .replace() easily.
                                # For true robust replacement, one would manually create new XObject stream.
                            else:
                                st.warning(f"⚠️ Image on page could not be processed (Unsupported format for conversion).")
                        else:
                            # Inform user if not JPEG and not aggressive enough quality for conversion
                            st.info(f"ℹ️ An image on a page was not compressed because it's not a JPEG "
                                    f"and your 'Picture Quality' setting ({image_quality}%) is not low enough "
                                    f"to trigger aggressive conversion (requires <= 40%).")

                    except Exception as e:
                        st.warning(f"⚠️ General error trying to shrink an image on a page. "
                                   f"This might be due to a very unusual image format or structure. Error: {e}")

        # Optimize the PDF even further: remove duplicates and unused bits
        writer.compress_identical_objects(remove_identicals=True, remove_orphans=True)

        # Save the shrunken PDF into a temporary space in your computer's memory
        output_pdf_bytes = io.BytesIO()
        writer.write(output_pdf_bytes)
        output_pdf_bytes.seek(0)
        compressed_size_bytes = len(output_pdf_bytes.getvalue())

        return output_pdf_bytes, original_size_bytes, compressed_size_bytes

    except Exception as e:
        st.error(f"Oh no! Something went wrong while shrinking your PDF: {e}. "
                 "This can happen with very old or damaged PDFs. Please try a different file.")
        return None, None, None

# --- Streamlit User Interface (What you see!) ---

# Set up the basic look of your app page
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
st.markdown("---") # Separator
st.subheader("1. Upload Your PDF Here 👇")

uploaded_file = st.file_uploader("Drag and drop your PDF or click to browse", type="pdf")

if uploaded_file is not None:
    original_size_bytes_display = len(uploaded_file.getvalue())
    st.info(f"**Original PDF Size:** **`{original_size_bytes_display / (1024*1024):.2f} MB`** 📏")

    st.markdown("---") # Separator
    st.subheader("2. Choose How Small You Want It! 👇")
    st.markdown("This tool works best by adjusting **Picture Quality**. The **lower** the quality value, the **smaller** the file (but pictures might get a little blurry).")
    st.markdown("If you need a very small file (e.g., under 10MB), you'll likely need to reduce the Picture Quality significantly.")

    # --- Conditional Warning about Aggressive Compression ---
    st.info("""
    **💡 Tip for Super Small Files:** If you set 'Picture Quality' to **40% or lower**, the app will try to convert *all* images (even non-JPEGs like PNGs) into lower quality JPEGs for maximum shrinkage. This can sometimes make text or sharp graphics look blurry, but it's great for photos and achieving very small file sizes!
    """)

    # --- Simplified Compression Control (Updated for Clarity) ---
    quality_setting = st.slider(
        "🖼️ **Picture Quality** (Lower Value = Smaller File)",
        min_value=0, max_value=100, value=60, step=5, # Changed default to 60 to encourage more reduction
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
                    st.markdown("## ➡️") # Simple arrow for visual flow
                with col3:
                    st.metric(label="Shrunk Size", value=f"{actual_compressed_size_bytes / (1024*1024):.2f} MB 👇")

                st.markdown(f"### **🥳 You Saved: `{reduction_percentage:.2f}%` of the original size!**")

                # Provide feedback on the 10MB goal
                if actual_compressed_size_bytes < (10 * 1024 * 1024): # 10 MB in bytes
                    st.balloons()
                    st.success(f"✅ Success! Your PDF is now under 10MB ({actual_compressed_size_bytes / (1024*1024):.2f} MB)! Perfect for emails!")
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
    st.markdown("---") # Another separator

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
