import streamlit as st
from PIL import Image, ImageDraw
import tempfile, os, time, io
import pandas as pd

st.set_page_config(page_title="MangoAI Tree Counter", page_icon="🥭", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700;900&family=Lato:wght@300;400;700&family=Caveat:wght@500;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Lato', sans-serif;
}

/* ── Warm earth background ── */
.stApp {
    background-color: #fdf6ec;
    background-image:
        radial-gradient(ellipse at 20% 10%, rgba(217,119,6,0.07) 0%, transparent 50%),
        radial-gradient(ellipse at 80% 80%, rgba(101,78,38,0.06) 0%, transparent 50%),
        url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='400' height='400'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.75' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='400' height='400' filter='url(%23n)' opacity='0.03'/%3E%3C/svg%3E");
    min-height: 100vh;
}

header[data-testid="stHeader"] {
    background: transparent;
}

/* ── Sidebar — aged wood panel ── */
section[data-testid="stSidebar"] {
    background: #3b2710 !important;
    background-image: repeating-linear-gradient(
        90deg,
        transparent,
        transparent 18px,
        rgba(255,255,255,0.015) 18px,
        rgba(255,255,255,0.015) 19px
    ) !important;
    border-right: 4px solid #7c5228 !important;
    box-shadow: 4px 0 20px rgba(59,39,16,0.3);
}

section[data-testid="stSidebar"] * {
    color: #f5e6cc !important;
}

section[data-testid="stSidebar"] .stSlider label,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 {
    color: #f5e6cc !important;
}

/* ── Hero ── */
.hero {
    text-align: center;
    padding: 2.5rem 1rem 1rem;
    position: relative;
}

.hero-eyebrow {
    font-family: 'Caveat', cursive;
    font-size: 1.1rem;
    color: #b45309;
    letter-spacing: 0.05em;
    margin-bottom: 0.4rem;
}

.hero h1 {
    font-family: 'Playfair Display', serif;
    font-size: clamp(2rem, 5vw, 3.4rem);
    font-weight: 900;
    color: #3b2710;
    line-height: 1.1;
    margin: 0 0 10px;
}

.hero h1 span {
    color: #d97706;
    font-style: italic;
}

.hero p {
    color: #7c5228;
    font-size: 0.95rem;
    max-width: 500px;
    margin: 0 auto;
    font-weight: 300;
    line-height: 1.6;
}

.hero-divider {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 12px;
    margin: 1.5rem auto 0;
    max-width: 300px;
}

.hero-divider-line {
    flex: 1;
    height: 1px;
    background: linear-gradient(90deg, transparent, #d97706, transparent);
}

.hero-divider-icon {
    font-size: 1.2rem;
}

/* ── Metrics ── */
.metrics-row {
    display: flex;
    gap: 12px;
    justify-content: center;
    flex-wrap: wrap;
    margin: 1.5rem auto;
    max-width: 780px;
}

.metric-card {
    background: #fff;
    border: 1.5px solid #e8d5b0;
    border-radius: 16px;
    padding: 14px 22px;
    text-align: center;
    min-width: 140px;
    flex: 1;
    box-shadow: 0 2px 12px rgba(59,39,16,0.08), 0 0 0 4px rgba(217,119,6,0.04);
    position: relative;
    overflow: hidden;
}

.metric-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    background: linear-gradient(90deg, #d97706, #f59e0b);
    border-radius: 16px 16px 0 0;
}

.metric-val {
    font-family: 'Playfair Display', serif;
    font-size: 2rem;
    font-weight: 900;
    color: #b45309;
    line-height: 1;
}

.metric-lbl {
    font-size: 0.65rem;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #9a7040;
    margin-top: 5px;
    font-weight: 700;
}

/* ── Upload zone ── */
.upload-wrap {
    max-width: 660px;
    margin: 0 auto 1.5rem;
}

[data-testid="stFileUploader"] {
    background: #fffbf3 !important;
    border: 2.5px dashed #d97706 !important;
    border-radius: 18px !important;
    padding: 2rem 1.5rem !important;
}

[data-testid="stFileUploader"] label {
    color: #7c5228 !important;
    font-family: 'Lato', sans-serif !important;
}

/* ── Divider ── */
.divider {
    border: none;
    border-top: 1.5px solid #e8d5b0;
    margin: 1.5rem 0;
}

/* ── Result cards ── */
.rc {
    background: #fff;
    border: 1.5px solid #e8d5b0;
    border-radius: 18px;
    overflow: hidden;
    margin-bottom: 1.4rem;
    box-shadow: 0 4px 18px rgba(59,39,16,0.07);
}

.rc-head {
    padding: 10px 16px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    background: linear-gradient(90deg, #fef3c7, #fffbf3);
    border-bottom: 1px solid #e8d5b0;
}

.rc-name {
    font-family: 'Playfair Display', serif;
    font-weight: 700;
    color: #3b2710;
    font-size: 0.9rem;
}

.count-pill {
    background: linear-gradient(135deg, #d97706, #f59e0b);
    color: #fff;
    font-family: 'Lato', sans-serif;
    font-weight: 700;
    font-size: 0.75rem;
    padding: 3px 12px;
    border-radius: 999px;
    box-shadow: 0 2px 8px rgba(217,119,6,0.35);
}

/* ── Image labels ── */
.img-lbl {
    font-family: 'Caveat', cursive;
    font-size: 0.95rem;
    color: #9a7040;
    margin-bottom: 4px;
}

/* ── Total banner ── */
.total-banner {
    background: linear-gradient(135deg, #3b2710 0%, #7c5228 100%);
    border-radius: 20px;
    padding: 2rem;
    text-align: center;
    margin: 1rem auto 1.5rem;
    max-width: 400px;
    box-shadow: 0 8px 32px rgba(59,39,16,0.25);
    position: relative;
    overflow: hidden;
}

.total-banner::before {
    content: '🥭🌳🌿';
    font-size: 5rem;
    position: absolute;
    top: -10px; right: -10px;
    opacity: 0.12;
    line-height: 1;
}

.total-num {
    font-family: 'Playfair Display', serif;
    font-size: 3.2rem;
    font-weight: 900;
    color: #fbbf24;
    line-height: 1;
}

.total-lbl {
    color: rgba(245,230,204,0.75);
    font-size: 0.88rem;
    margin-top: 8px;
    letter-spacing: 0.04em;
}

/* ── Images ── */
div[data-testid="stImage"] img {
    border-radius: 12px;
    width: 100%;
    border: 1.5px solid #e8d5b0;
}

/* ── Progress bar ── */
.stProgress > div > div {
    background: linear-gradient(90deg, #d97706, #f59e0b) !important;
    border-radius: 999px !important;
}

/* ── Slider ── */
.stSlider > div > div > div {
    background: #d97706 !important;
}

/* ── DataFrame ── */
div[data-testid="stDataFrame"] {
    border-radius: 14px;
    overflow: hidden;
    border: 1.5px solid #e8d5b0 !important;
    box-shadow: 0 2px 12px rgba(59,39,16,0.06);
}

/* ── Download button ── */
.stDownloadButton > button {
    background: #fffbf3 !important;
    color: #b45309 !important;
    border: 1.5px solid #d97706 !important;
    border-radius: 10px !important;
    font-size: 0.78rem !important;
    font-weight: 700 !important;
    font-family: 'Lato', sans-serif !important;
    transition: all 0.2s !important;
}

.stDownloadButton > button:hover {
    background: #fef3c7 !important;
    box-shadow: 0 4px 12px rgba(217,119,6,0.2) !important;
}

/* ── Section headings ── */
.section-heading {
    font-family: 'Playfair Display', serif;
    font-size: 1.15rem;
    font-weight: 700;
    color: #3b2710;
    margin-bottom: 0.9rem;
    display: flex;
    align-items: center;
    gap: 8px;
}

/* ── Sidebar decorative ── */
.sidebar-brand {
    font-family: 'Playfair Display', serif;
    font-size: 1.4rem;
    font-weight: 900;
    color: #fbbf24 !important;
}
.sidebar-sub {
    font-family: 'Caveat', cursive;
    font-size: 1rem;
    color: #d4a574 !important;
}
</style>
""", unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("<div class='sidebar-brand'>🥭 MangoAI</div>", unsafe_allow_html=True)
    st.markdown("<div class='sidebar-sub'>Tree Detection & Counter</div>", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("### ⚙️ Detection Settings")
    confidence = st.slider("Detection Confidence", 0.1, 0.9, 0.35, 0.05,
                           help="Lower = detects more trees (may include false positives). Higher = only very confident detections.")
    st.markdown("---")
    st.markdown("### 📖 How to use")
    st.markdown("""
1. Upload your mango orchard images  
2. Adjust confidence threshold if needed  
3. View annotated detection results  
4. Download images & export CSV report
""")
    st.markdown("---")
    st.markdown("### 🌾 Model Details")
    st.markdown("""
- **Model**: YOLOv8  
- **Training images**: 150  
- **Annotations**: Roboflow  
- **Training epochs**: 50
""")

# ── Load model ────────────────────────────────────────────────────────────────
@st.cache_resource
def load_model():
    import torch
    from ultralytics import YOLO
    return YOLO("best.pt")

def draw_boxes(image, boxes, conf_threshold=0.35):
    img = image.copy().convert("RGB")
    draw = ImageDraw.Draw(img)
    count = 0
    for box in boxes:
        conf = float(box.conf[0])
        if conf < conf_threshold:
            continue
        x1, y1, x2, y2 = [int(v) for v in box.xyxy[0].tolist()]
        draw.rectangle([x1, y1, x2, y2], outline="#d97706", width=3)
        label = f"Tree {conf:.0%}"
        draw.rectangle([x1, y1 - 18, x1 + len(label)*7 + 4, y1], fill="#d97706")
        draw.text((x1 + 3, y1 - 16), label, fill="#ffffff")
        count += 1
    return img, count

def pil_to_bytes(img):
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()

# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
  <div class="hero-eyebrow">🌾 Field Intelligence for Farmers</div>
  <h1>Mango Orchard <span>Tree Counter</span></h1>
  <p>Upload field or aerial photographs of your mango orchard — our YOLOv8 model automatically detects and counts every tree for you.</p>
  <div class="hero-divider">
    <div class="hero-divider-line"></div>
    <div class="hero-divider-icon">🥭</div>
    <div class="hero-divider-line"></div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── Upload ────────────────────────────────────────────────────────────────────
st.markdown('<div class="upload-wrap">', unsafe_allow_html=True)
uploaded_files = st.file_uploader(
    "📷  Upload orchard images (JPG / PNG)",
    type=["jpg","jpeg","png"],
    accept_multiple_files=True
)
st.markdown('</div>', unsafe_allow_html=True)

# ── Process ───────────────────────────────────────────────────────────────────
if uploaded_files:
    model = load_model()
    results_data = []
    status = st.empty()
    bar = st.progress(0)

    for i, f in enumerate(uploaded_files):
        status.markdown(
            f"<p style='text-align:center;color:#9a7040;font-size:0.85rem;'>🌿 Scanning <b style='color:#b45309'>{f.name}</b>…</p>",
            unsafe_allow_html=True
        )
        bar.progress(i / len(uploaded_files))
        image = Image.open(f).convert("RGB")
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
            image.save(tmp.name)
            tmp_path = tmp.name
        result = model(tmp_path, verbose=False)[0]
        annotated, count = draw_boxes(image, result.boxes, confidence)
        avg_conf = float(sum(b.conf[0] for b in result.boxes) / len(result.boxes)) if len(result.boxes) > 0 else 0
        results_data.append({"name": f.name, "original": image, "detected": annotated, "count": count, "conf": avg_conf})
        os.unlink(tmp_path)

    bar.progress(1.0)
    time.sleep(0.2)
    status.empty()
    bar.empty()

    total = sum(r["count"] for r in results_data)
    n_imgs = len(results_data)
    avg = round(total / n_imgs, 1) if n_imgs else 0
    best = max(r["count"] for r in results_data)

    # ── Metrics ──
    st.markdown(f"""
    <div class="metrics-row">
      <div class="metric-card"><div class="metric-val">🌳 {total}</div><div class="metric-lbl">Trees Detected</div></div>
      <div class="metric-card"><div class="metric-val">📷 {n_imgs}</div><div class="metric-lbl">Images Analysed</div></div>
      <div class="metric-card"><div class="metric-val">📊 {avg}</div><div class="metric-lbl">Avg per Image</div></div>
      <div class="metric-card"><div class="metric-val">🥭 {best}</div><div class="metric-lbl">Best Single Image</div></div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    # ── Summary Table + CSV Export ──
    st.markdown("<div class='section-heading'>📋 Harvest Report</div>", unsafe_allow_html=True)
    df = pd.DataFrame([{"Image": r["name"], "Trees Detected": r["count"], "Avg Confidence": f"{r['conf']:.0%}"} for r in results_data])
    st.dataframe(df, use_container_width=True, hide_index=True)
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("⬇ Export Report as CSV", csv, "mango_orchard_report.csv", "text/csv")

    st.markdown('<hr class="divider">', unsafe_allow_html=True)
    st.markdown("<div class='section-heading'>🖼 Field Detection Results</div>", unsafe_allow_html=True)

    # ── Per-image results ──
    for r in results_data:
        st.markdown(f"""
        <div class="rc">
          <div class="rc-head">
            <span class="rc-name">🌿 {r['name']}</span>
            <span class="count-pill">🌳 {r['count']} trees found</span>
          </div>
        </div>
        """, unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            st.markdown('<p class="img-lbl">✦ Original Photo</p>', unsafe_allow_html=True)
            st.image(r["original"], use_column_width=True)
        with col2:
            st.markdown('<p class="img-lbl">✦ AI Detection</p>', unsafe_allow_html=True)
            st.image(r["detected"], use_column_width=True)
            st.download_button(
                f"⬇ Download Annotated Image",
                pil_to_bytes(r["detected"]),
                f"detected_{r['name']}",
                "image/png",
                key=f"dl_{r['name']}"
            )
        st.markdown("<div style='margin-bottom:1.2rem'></div>", unsafe_allow_html=True)

    # ── Total ──
    st.markdown(f"""
    <div class="total-banner">
      <div class="total-num">🌳 {total}</div>
      <div class="total-lbl">Total Mango Trees Across Your Orchard</div>
    </div>
    """, unsafe_allow_html=True)

else:
    st.markdown("""
    <div style='text-align:center; margin-top: 1rem;'>
      <div style='font-size:3.5rem; margin-bottom:0.8rem;'>🌾🥭🌳</div>
      <p style='color:#9a7040; font-size:0.92rem; font-family: Lato, sans-serif;'>
        Upload one or more orchard images above to begin counting.
      </p>
    </div>
    """, unsafe_allow_html=True)
