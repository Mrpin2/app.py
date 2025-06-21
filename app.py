# app.py

import streamlit as st
from pypdf import PdfWriter, PdfReader
import io
# To use Lottie animations, install: pip install streamlit-lottie requests
from streamlit_lottie import st_lottie
import requests

# --- Configuration for your App ---
APP_TITLE = "Super Simple PDF Shrinker! 📄✨"
APP_ICON = "🎈"
YOUR_LINKEDIN_URL = "https://www.linkedin.com/in/rajeevbhandari87/"
# IMPORTANT: Ensure 'Logo.png' is in the ROOT of your GitHub repository,
# alongside app.py, for Streamlit Cloud to find it.
YOUR_LOGO_PATH = "Logo.png"
LOTTIE_ANIMATION_URL_UPLOAD = "https://lottie.host/75421c60-a4a3-4ec6-8dd3-979f4277b949/67g8tq340F.json" # File upload animation
LOTTIE_ANIMATION_URL_COMPRESS = "https://lottie.host/17800746-8809-42b7-862d-a6d17b5f2122/tHn42x9pP3.json" # Compression/shrinking animation

# --- Helper to load Lottie Animations ---
def load_lottieurl(url: str):
    """Loads a Lottie animation JSON from a given URL."""
    try:
        r = requests.get(url, timeout=5) # Added timeout for robustness
        r.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
        return r.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to load animation from {url}. Error: {e}")
        return None
    except ValueError: # JSON decoding error
        st.error(f"Failed to decode JSON from animation URL: {url}. Is it a valid Lottie JSON?")
        return None


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
            # Think of this like neatly folding clothes – they take up less space, but nothing is lost.
            current_page_in_writer.compress_content_streams(level=compression_level)

            # --- Reduce image quality if you want a smaller file ---
            if image_quality < 100: # Only do this if you want to make images smaller
                for img in current_page_in_writer.images:
                    try:
                        # Re-squish the image with the quality you chose
                        img.replace(img.image, quality=image_quality)
                    except Exception as e:
                        st.warning(f"Couldn't make an image smaller on a page (might be a special type). Error: {e}")

        # Optimize the PDF even further: remove duplicates and unused bits
        # This is like decluttering your room – getting rid of things you don't need!
        writer.compress_identical_objects(remove_identicals=True, remove_orphans=True)

        # Save the shrunken PDF into a temporary space in your computer's memory
        output_pdf_bytes = io.BytesIO()
        writer.write(output_pdf_bytes)
        output_pdf_bytes.seek(0)  # Rewind to the beginning so we can read/download it
        compressed_size_bytes = len(output_pdf_bytes.getvalue())

        return output_pdf_bytes, original_size_bytes, compressed_size_bytes

    except Exception as e:
        st.error(f"Oh no! Something went wrong while shrinking your PDF: {e}. "
                 "This can happen with very old or damaged PDFs. Please try a different file.")
        return None, None, None

# --- Streamlit User Interface (What you see!) ---

# Set up the basic look of your app page
st.set_page_config(
    layout="centered", # Makes the content nicely centered
    page_title=APP_TITLE,
    page_icon=APP_ICON
)

# You can add your logo here!
# Ensure 'Logo.png' is in the ROOT of your GitHub repository.
try:
    st.image(YOUR_LOGO_PATH, width=150)
except FileNotFoundError:
    st.warning("Logo file not found! Make sure 'Logo.png' is in the same folder as app.py and committed to GitHub.")
except Exception as e:
    st.error(f"An unexpected error occurred while loading the logo: {e}")


st.title(f"{APP_ICON} {APP_TITLE}")
st.markdown("Got a PDF that's too big? Let's make it smaller! "
            "Perfect for emails, uploads, and saving space. ✨")

# --- 1. Upload Your PDF Here Section ---
st.markdown("---") # Separator
st.subheader("1. Upload Your PDF Here 👇")

lottie_json_upload = load_lottieurl(LOTTIE_ANIMATION_URL_UPLOAD)
if lottie_json_upload:
    st_lottie(lottie_json_upload, height=150, key="pdf_upload_animation")

uploaded_file = st.file_uploader("Drag and drop your PDF or click to browse", type="pdf")

if uploaded_file is not None:
    original_size_bytes_display = len(uploaded_file.getvalue())
    st.info(f"**Original PDF Size:** **`{original_size_bytes_display / (1024*1024):.2f} MB`** 📏")

    st.markdown("---") # Separator
    st.subheader("2. Choose How Small You Want It! 👇")
    st.markdown("This tool works best by adjusting **Picture Quality**. "
                "The lower the quality, the smaller the file (but pictures might get a little blurry).")

    # --- Simplified Compression Control ---
    # This slider directly controls the image_quality, but with friendlier labels.
    quality_setting = st.slider(
        "⚡ **Shrink Power!** (More Power = Smaller File)",
        min_value=0, max_value=100, value=75, step=5,
        help="Slide towards 'Smallest File' to greatly reduce size (pictures might become less clear). "
             "Slide towards 'Best Quality' to keep pictures crisp (larger file)."
    )

    # Map the simplified slider to image_quality and compression_level
    # We'll make 'compression_level' always max (9) for best lossless compression
    compression_level = 9
    image_quality = quality_setting # Direct mapping for simplicity

    st.markdown(f"**Your Current Setting:** You're aiming for a balance between **`{quality_setting}%`** picture quality and file size.")


    if st.button("🚀 Shrink My PDF Now!", type="primary"):
        with st.spinner("Crunching numbers and making your PDF tiny... Please wait!"):
            lottie_json_compress = load_lottieurl(LOTTIE_ANIMATION_URL_COMPRESS)
            if lottie_json_compress:
                st_lottie(lottie_json_compress, height=200, key="pdf_compress_animation")
            else:
                st.info("Animation couldn't load, but the compression is still running!")

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


                st.download_button(
                    label="⬇️ Download Your Shrunken PDF",
                    data=compressed_pdf_bytes,
                    file_name=f"shrunk_{uploaded_file.name}", # Gives a more descriptive file name
                    mime="application/pdf",
                    help="Click to download your newly shrunken PDF."
                )
            # No 'else' needed here, as the function itself handles errors with st.error

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
