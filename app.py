import streamlit as st
from ultralytics import YOLO
from PIL import Image
import tempfile
import os
import time

# ─── Page Config ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Mango Tree Counter",
    page_icon="🌴",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─── Custom CSS ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500&display=swap');

  html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
  }

  /* Background */
  .stApp {
    background: linear-gradient(135deg, #0a1f0e 0%, #0d2b12 40%, #0f3016 100%);
    min-height: 100vh;
  }

  /* Hide default header */
  header[data-testid="stHeader"] { background: transparent; }

  /* ── Hero Banner ── */
  .hero {
    text-align: center;
    padding: 3.5rem 2rem 2rem;
  }
  .hero-badge {
    display: inline-block;
    background: rgba(134, 239, 92, 0.12);
    border: 1px solid rgba(134, 239, 92, 0.35);
    color: #86ef5c;
    font-family: 'DM Sans', sans-serif;
    font-size: 0.72rem;
    font-weight: 500;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    padding: 0.35rem 1rem;
    border-radius: 999px;
    margin-bottom: 1.2rem;
  }
  .hero h1 {
    font-family: 'Syne', sans-serif;
    font-size: clamp(2.4rem, 5vw, 3.8rem);
    font-weight: 800;
    color: #f0fdf0;
    line-height: 1.1;
    margin: 0 0 0.8rem;
  }
  .hero h1 span { color: #86ef5c; }
  .hero-sub {
    color: rgba(220, 252, 220, 0.55);
    font-size: 1.05rem;
    font-weight: 300;
    max-width: 520px;
    margin: 0 auto;
  }

  /* ── Metric Cards ── */
  .metrics-row {
    display: flex;
    gap: 1rem;
    justify-content: center;
    flex-wrap: wrap;
    margin: 2rem auto 2.5rem;
    max-width: 760px;
  }
  .metric-card {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(134, 239, 92, 0.15);
    border-radius: 16px;
    padding: 1.2rem 2rem;
    min-width: 160px;
    text-align: center;
    backdrop-filter: blur(10px);
  }
  .metric-val {
    font-family: 'Syne', sans-serif;
    font-size: 2.2rem;
    font-weight: 800;
    color: #86ef5c;
    line-height: 1;
  }
  .metric-lbl {
    font-size: 0.75rem;
    font-weight: 500;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: rgba(220, 252, 220, 0.45);
    margin-top: 0.35rem;
  }

  /* ── Upload Zone ── */
  .upload-section {
    max-width: 680px;
    margin: 0 auto 2.5rem;
  }
  [data-testid="stFileUploader"] {
    background: rgba(255,255,255,0.03) !important;
    border: 2px dashed rgba(134, 239, 92, 0.3) !important;
    border-radius: 18px !important;
    padding: 2rem !important;
    transition: border-color 0.25s;
  }
  [data-testid="stFileUploader"]:hover {
    border-color: rgba(134, 239, 92, 0.6) !important;
  }
  [data-testid="stFileUploader"] label {
    color: rgba(220,252,220,0.7) !important;
  }

  /* ── Result Cards ── */
  .result-card {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(134, 239, 92, 0.12);
    border-radius: 20px;
    overflow: hidden;
    margin-bottom: 1.5rem;
    backdrop-filter: blur(8px);
  }
  .result-card-header {
    padding: 0.9rem 1.4rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
    border-bottom: 1px solid rgba(134,239,92,0.1);
    background: rgba(134,239,92,0.05);
  }
  .result-card-title {
    font-family: 'Syne', sans-serif;
    font-weight: 700;
    color: #d1fad1;
    font-size: 0.95rem;
  }
  .count-badge {
    background: #86ef5c;
    color: #0a1f0e;
    font-family: 'Syne', sans-serif;
    font-weight: 800;
    font-size: 0.85rem;
    padding: 0.25rem 0.85rem;
    border-radius: 999px;
  }
  .result-card-body {
    padding: 1rem;
    display: flex;
    gap: 1rem;
  }
  .img-label {
    font-size: 0.7rem;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    color: rgba(220,252,220,0.4);
    margin-bottom: 0.4rem;
    font-weight: 500;
  }

  /* ── Success Banner ── */
  .success-banner {
    background: linear-gradient(90deg, rgba(134,239,92,0.15), rgba(134,239,92,0.05));
    border: 1px solid rgba(134,239,92,0.35);
    border-radius: 16px;
    padding: 1.4rem 2rem;
    text-align: center;
    margin: 1rem auto 2rem;
    max-width: 500px;
  }
  .success-banner .big-num {
    font-family: 'Syne', sans-serif;
    font-size: 3.5rem;
    font-weight: 800;
    color: #86ef5c;
    line-height: 1;
  }
  .success-banner .big-lbl {
    color: rgba(220,252,220,0.65);
    font-size: 0.95rem;
    margin-top: 0.3rem;
  }

  /* ── Divider ── */
  .section-divider {
    border: none;
    border-top: 1px solid rgba(134,239,92,0.1);
    margin: 2rem 0;
  }

  /* ── Streamlit element overrides ── */
  .stButton > button {
    background: #86ef5c !important;
    color: #0a1f0e !important;
    border: none !important;
    border-radius: 10px !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;
    padding: 0.6rem 1.8rem !important;
    cursor: pointer;
  }
  div[data-testid="stImage"] img {
    border-radius: 12px;
    width: 100%;
  }

  /* Progress bar */
  .stProgress > div > div {
    background: #86ef5c !important;
  }
</style>
""", unsafe_allow_html=True)

# ─── Load Model ──────────────────────────────────────────────────────────────
@st.cache_resource
def load_model():
    return YOLO("best.pt")

model = load_model()

# ─── Hero ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
  <div class="hero-badge">🛰️ AI-Powered Remote Sensing</div>
  <h1>Mango Tree<br><span>Detection & Counter</span></h1>
  <p class="hero-sub">Upload aerial or field images to automatically detect, annotate, and count mango trees using YOLOv8.</p>
</div>
""", unsafe_allow_html=True)

# ─── Session State ───────────────────────────────────────────────────────────
if "results_data" not in st.session_state:
    st.session_state.results_data = []

# ─── Upload ──────────────────────────────────────────────────────────────────
st.markdown('<div class="upload-section">', unsafe_allow_html=True)
uploaded_files = st.file_uploader(
    "📂  Drop images here or click to browse",
    type=["jpg", "png", "jpeg"],
    accept_multiple_files=True,
    label_visibility="visible",
)
st.markdown('</div>', unsafe_allow_html=True)

# ─── Process ─────────────────────────────────────────────────────────────────
if uploaded_files:
    results_data = []

    status_text = st.empty()
    progress_bar = st.progress(0)

    for i, uploaded_file in enumerate(uploaded_files):
        status_text.markdown(f"<p style='color:rgba(220,252,220,0.5);text-align:center;font-size:0.85rem;'>Analysing <b style='color:#86ef5c'>{uploaded_file.name}</b>…</p>", unsafe_allow_html=True)
        progress_bar.progress((i) / len(uploaded_files))

        image = Image.open(uploaded_file).convert("RGB")

        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
            image.save(tmp.name)
            tmp_path = tmp.name

        result = model(tmp_path)[0]
        count = len(result.boxes)
        result_img = result.plot()  # numpy array (BGR)

        results_data.append({
            "name": uploaded_file.name,
            "original": image,
            "detected": result_img,
            "count": count,
        })

        os.unlink(tmp_path)
        time.sleep(0.1)

    progress_bar.progress(1.0)
    status_text.empty()
    progress_bar.empty()

    total = sum(r["count"] for r in results_data)

    # ── Metrics ──
    st.markdown(f"""
    <div class="metrics-row">
      <div class="metric-card">
        <div class="metric-val">{total}</div>
        <div class="metric-lbl">Trees Detected</div>
      </div>
      <div class="metric-card">
        <div class="metric-val">{len(results_data)}</div>
        <div class="metric-lbl">Images Analysed</div>
      </div>
      <div class="metric-card">
        <div class="metric-val">{round(total/len(results_data),1) if results_data else 0}</div>
        <div class="metric-lbl">Avg per Image</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

    # ── Per-image Results ──
    st.markdown("<h3 style='font-family:Syne,sans-serif;color:#d1fad1;font-size:1.15rem;margin-bottom:1.2rem;'>📸 Detection Results</h3>", unsafe_allow_html=True)

    for r in results_data:
        st.markdown(f"""
        <div class="result-card">
          <div class="result-card-header">
            <span class="result-card-title">🖼 {r['name']}</span>
            <span class="count-badge">🌴 {r['count']} trees</span>
          </div>
        </div>
        """, unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            st.markdown('<p class="img-label">Original</p>', unsafe_allow_html=True)
            st.image(r["original"], use_column_width=True)
        with col2:
            st.markdown('<p class="img-label">Detected</p>', unsafe_allow_html=True)
            st.image(r["detected"], channels="BGR", use_column_width=True)

        st.markdown("<div style='margin-bottom:1.5rem'></div>", unsafe_allow_html=True)

    # ── Grand Total ──
    st.markdown(f"""
    <div class="success-banner">
      <div class="big-num">🌴 {total}</div>
      <div class="big-lbl">Total Mango Trees Detected Across All Images</div>
    </div>
    """, unsafe_allow_html=True)

else:
    st.markdown("""
    <p style='text-align:center;color:rgba(220,252,220,0.3);font-size:0.9rem;margin-top:1rem;'>
      Upload one or more images above to begin detection.
    </p>
    """, unsafe_allow_html=True)