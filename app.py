import streamlit as st
from PIL import Image, ImageDraw
import tempfile, os, time, io
import pandas as pd
from ultralytics import YOLO

# ─── PAGE CONFIG ─────────────────────────────────────────────
st.set_page_config(
    page_title="MangoAI Tree Counter",
    page_icon="🌳",
    layout="wide"
)

# ─── CSS (LIGHT MANGO THEME) ─────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;900&family=Poppins:wght@300;400;600&display=swap');

body {font-family: 'Poppins', sans-serif;}

.stApp {
    background: linear-gradient(135deg, #fff9f2, #fff4e6, #fefce8);
}

/* HERO */
.hero-container {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 40px;
    padding: 2rem 1rem;
}

.hero-title {
    font-family: 'Playfair Display', serif;
    font-size: clamp(2.5rem, 5vw, 3.8rem);
    font-weight: 900;
    color: #7c2d12;
}

.hero-title span { color: #f59e0b; }

.hero-sub {
    color: #92400e;
    margin-top: 10px;
}

/* IMAGE */
.hero-image img {
    max-width: 100%;
    border-radius: 20px;
}

/* UPLOAD */
[data-testid="stFileUploader"] {
    border: 2px dashed #f59e0b !important;
    border-radius: 15px;
    background: white;
}

/* METRICS */
.metric-box {
    background: white;
    padding: 15px;
    border-radius: 12px;
    text-align: center;
    border: 1px solid #fde68a;
}
.metric-box h2 { color: #d97706; }

</style>
""", unsafe_allow_html=True)

# ─── HERO SECTION ────────────────────────────────────────────
st.markdown("""
<div class="hero-container">
    <div>
        <div class="hero-title">
            Smart <span>Mango Orchard</span><br>
            Tree Counter
        </div>
        <div class="hero-sub">
            AI-powered system to detect and count mango trees from images.
        </div>
    </div>

    <div class="hero-image">
        <img src="https://images.unsplash.com/photo-1501004318641-b39e6451bec6?auto=format&fit=crop&w=800&q=60">
    </div>
</div>
""", unsafe_allow_html=True)

# ─── LOAD MODEL ──────────────────────────────────────────────
@st.cache_resource
def load_model():
    return YOLO("best.pt")   # make sure this exists

model = load_model()

# ─── FILE UPLOAD ─────────────────────────────────────────────
uploaded_files = st.file_uploader(
    "Upload orchard images",
    type=["jpg", "png", "jpeg"],
    accept_multiple_files=True
)

# ─── PROCESS ─────────────────────────────────────────────────
if uploaded_files:

    results_data = []
    progress = st.progress(0)

    for i, file in enumerate(uploaded_files):

        image = Image.open(file).convert("RGB")

        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
            image.save(tmp.name)
            path = tmp.name

        result = model(path)[0]

        annotated = result.plot()
        count = len(result.boxes)

        results_data.append({
            "name": file.name,
            "image": image,
            "result": annotated,
            "count": count
        })

        os.unlink(path)
        progress.progress((i+1)/len(uploaded_files))

    total = sum(r["count"] for r in results_data)

    # ─── METRICS ─────────────────────────────────────────────
    col1, col2, col3 = st.columns(3)

    col1.markdown(f"<div class='metric-box'><h2>{total}</h2>Trees</div>", unsafe_allow_html=True)
    col2.markdown(f"<div class='metric-box'><h2>{len(results_data)}</h2>Images</div>", unsafe_allow_html=True)
    col3.markdown(f"<div class='metric-box'><h2>{round(total/len(results_data),1)}</h2>Avg</div>", unsafe_allow_html=True)

    st.markdown("---")

    # ─── RESULTS ─────────────────────────────────────────────
    for r in results_data:

        st.subheader(r["name"])

        col1, col2 = st.columns(2)

        with col1:
            st.image(r["image"], caption="Original")

        with col2:
            st.image(r["result"], caption=f"Detected: {r['count']} trees")

        st.markdown("---")

else:
    st.info("Upload images to start detection 🌳")
