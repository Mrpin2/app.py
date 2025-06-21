# app.py

import streamlit as st
from pypdf import PdfWriter, PdfReader
import io

# --- Configuration for your App ---
APP_TITLE = "Super Simple PDF Shrinker! 📄✨" # Catchy title
APP_ICON = "🎈" # A fun emoji for the browser tab
YOUR_LINKEDIN_URL = "https://www.linkedin.com/in/rajeevbhandari87/" # Your LinkedIn URL
YOUR_LOGO_PATH = "your_logo.png" # <--- IMPORTANT: Replace with your logo's file name
                                # Make sure 'your_logo.png' is in the same folder as app.py
LOTTIE_ANIMATION_URL = "https://lottie.host/75421c60-a4a3-4ec6-8dd3-979f4277b949/67g8tq340F.json" # Example Lottie JSON URL for a file upload animation
                                                                                               # Find more at lottiefiles.com!

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

            # --- EXPERIMENTAL: Reduce image quality if you want a smaller file ---
            if image_quality < 100: # Only do this if you want to make images smaller
                for img in current_page_in_writer.images:
                    try:
                        # Re-squish the image with the quality you chose
                        img.replace(img.image, quality=image_quality)
                    except Exception as e:
                        # Sometimes an image might be tricky, we'll let you know!
                        st.warning(f"Couldn't make an image smaller (might be a special type). Error: {e}")

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
# Ensure 'your_logo.png' is in the same directory as this script.
# st.image(YOUR_LOGO_PATH, width=150) # Uncomment this line and replace 'your_logo.png' with your actual logo file name

st.title(f"{APP_ICON} {APP_TITLE}")
st.markdown("Got a PDF that's too big? Let's make it smaller! "
            "Perfect for emails, uploads, and saving space. ✨")

# --- Animation Placeholder ---
# To add cool animations, you'll need the 'streamlit_lottie' library.
# Install it: pip install streamlit-lottie
# Then, import it:
# from streamlit_lottie import st_lottie
# import requests # You might need this to load Lottie animations from a URL

# def load_lottieurl(url: str):
#     r = requests.get(url)
#     if r.status_code != 200:
#         return None
#     return r.json()

# lottie_json = load_lottieurl(LOTTIE_ANIMATION_URL)
# if lottie_json:
#     st_lottie(lottie_json, height=200, key="pdf_animation")
# else:
#     st.info("No cool animation? Make sure the Lottie URL is correct and install 'streamlit_lottie'!")

st.write("---") # A nice separator line

# File Uploader Section
st.subheader("1. Upload Your PDF Here 👇")
uploaded_file = st.file_uploader("Drag and drop your PDF or click to browse", type="pdf")

if uploaded_file is not None:
    original_size_bytes_display = len(uploaded_file.getvalue())
    st.info(f"**Original PDF Size:** **`{original_size_bytes_display / (1024*1024):.2f} MB`** 📏")

    st.subheader("2. Choose How Much to Shrink It! 👇")
    st.markdown("Want a *really* small file? Lower the 'Image Quality' setting. "
                "Higher quality means a bigger file, but better-looking pictures.")

    # --- Compression Options ---

    # Content Stream Compression (Lossless) - explained simply
    compression_level = st.slider(
        "✨ **Smart Text & Graphics Shrinker** (No Quality Loss)",
        min_value=0, max_value=9, value=9, step=1,
        help="This tidies up text and drawings in your PDF without losing any detail. "
             "Think of it as organizing files – they're the same, just neater and smaller! "
             "Setting 9 is the best for shrinking (might take a tiny bit longer)."
    )

    # Image Quality (Lossy) - Explained as the main 'lever'
    image_quality = st.slider(
        "🖼️ **Picture Quality** (Your Main Size Lever!)",
        min_value=0, max_value=100, value=80, step=5,
        help="This is the most powerful setting for reducing PDF size, especially if your PDF has photos or scanned pages. "
             "**100 = Best Quality (bigger file)**, **0 = Lowest Quality (super small file, but pictures might look blurry!)**. "
             "Try different values to find your perfect balance!"
    )
    st.markdown(f"**Current Picture Quality Setting:** `{image_quality}%` (Lower % = smaller file, more blur)")


    if st.button("🚀 Shrink My PDF Now!", type="primary"):
        with st.spinner("Crunching numbers and shrinking your PDF... This might take a moment!"):
            # Call our main shrinking function
            compressed_pdf_bytes, actual_original_size_bytes, actual_compressed_size_bytes = reduce_pdf_size(
                uploaded_file, compression_level, image_quality
            )

            if compressed_pdf_bytes:
                reduction_percentage = ((actual_original_size_bytes - actual_compressed_size_bytes) / actual_original_size_bytes) * 100

                st.success("🎉 Your PDF has been successfully shrunk!")
                st.write(f"**Shrunk File Size:** `{actual_compressed_size_bytes / (1024*1024):.2f} MB`")
                st.write(f"**You Saved:** `{reduction_percentage:.2f}%` of the original size!")

                # Provide feedback on the 10MB goal (if that's a common target)
                if actual_compressed_size_bytes < (10 * 1024 * 1024): # 10 MB in bytes
                    st.balloons() # A little celebration!
                    st.success(f"🥳 Great news! Your PDF is now under the 10MB target (`{actual_compressed_size_bytes / (1024*1024):.2f} MB`) with these settings!")
                else:
                    st.info(f"Your PDF is now `{actual_compressed_size_bytes / (1024*1024):.2f} MB`. If you need it even smaller, try moving the 'Picture Quality' slider down further.")

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
    - **Smart Text & Graphics Shrinker (Lossless):** This clever part compresses the text and drawings in your PDF without changing how they look. It's like zipping up a folder – the contents are the same, just packed tighter!
    - **Picture Quality (Lossy):** This is your secret weapon for super small files! If your PDF has photos or scanned pages, this feature will make them smaller by gently reducing their quality. Lower numbers mean smaller files but slightly less crisp pictures.
    - **Digital Declutter (Object Optimization):** The tool also cleans up your PDF by removing any duplicate information or unused bits that might be hiding inside. It's all about making your file as lean as possible!
    """)
    st.markdown("---")

# --- Footer with your information ---
st.markdown("Made with ❤️ by Rajeev Bhandari")
st.markdown(f"Connect with me on [LinkedIn]({YOUR_LINKEDIN_URL})")
# If you uncommented the logo line above, you might want to adjust its position
# or size to fit well with the footer.

# --- Instructions for the user to run this ---
st.sidebar.markdown("### How to Use This App:")
st.sidebar.markdown("""
1.  **Save this code** as `app.py` on your computer.
2.  **Save your logo** (e.g., `your_logo.png`) in the **same folder** as `app.py`.
    * *If you don't have a logo, you can comment out the `st.image(YOUR_LOGO_PATH, width=150)` line above.*
3.  **Open your computer's terminal or command prompt.**
4.  **Navigate to the folder** where you saved `app.py` (e.g., `cd path/to/your/folder`).
5.  **Install the necessary libraries:**
    `pip install streamlit pypdf`
    * *For animations, also install `pip install streamlit-lottie requests` and uncomment the animation block.*
6.  **Run the app:**
    `streamlit run app.py`
7.  A web page will open in your browser, and you're ready to shrink PDFs!
""")
