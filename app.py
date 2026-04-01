import streamlit as st
from PIL import Image, ImageDraw
import tempfile, os, time, io
import pandas as pd

st.set_page_config(page_title="MangoAI Tree Counter", page_icon="🌴", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;700;800&family=DM+Sans:wght@300;400;500&display=swap');
html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
.stApp { background: linear-gradient(160deg, #071a09 0%, #0d2b12 60%, #0f3016 100%); min-height: 100vh; }
header[data-testid="stHeader"] { background: transparent; }
section[data-testid="stSidebar"] { background: #051205 !important; border-right: 1px solid rgba(134,239,92,0.1); }
section[data-testid="stSidebar"] * { color: rgba(210,252,210,0.7) !important; }
.hero { text-align: center; padding: 2rem 1rem 1rem; }
.hero h1 { font-family: 'Syne', sans-serif; font-size: clamp(1.8rem, 4vw, 3rem); font-weight: 800; color: #f0fdf0; line-height: 1.1; margin: 0 0 8px; }
.hero h1 span { color: #86ef5c; }
.hero p { color: rgba(210,252,210,0.45); font-size: 0.95rem; max-width: 480px; margin: 0 auto; }
.metrics-row { display: flex; gap: 10px; justify-content: center; flex-wrap: wrap; margin: 1rem auto 1.5rem; max-width: 760px; }
.metric-card { background: rgba(255,255,255,0.05); border: 1px solid rgba(134,239,92,0.18); border-radius: 14px; padding: 12px 20px; text-align: center; min-width: 130px; flex: 1; }
.metric-val { font-family: 'Syne', sans-serif; font-size: 1.8rem; font-weight: 800; color: #86ef5c; line-height: 1; }
.metric-lbl { font-size: 0.65rem; letter-spacing: 0.1em; text-transform: uppercase; color: rgba(210,252,210,0.38); margin-top: 4px; }
.upload-wrap { max-width: 660px; margin: 0 auto 1.5rem; }
[data-testid="stFileUploader"] { background: rgba(255,255,255,0.025) !important; border: 2px dashed rgba(134,239,92,0.28) !important; border-radius: 16px !important; padding: 1.5rem !important; }
[data-testid="stFileUploader"] label { color: rgba(210,252,210,0.65) !important; }
.divider { border: none; border-top: 1px solid rgba(134,239,92,0.1); margin: 1.2rem 0; }
.rc { background: rgba(255,255,255,0.035); border: 1px solid rgba(134,239,92,0.1); border-radius: 18px; overflow: hidden; margin-bottom: 1.2rem; }
.rc-head { padding: 9px 14px; display: flex; align-items: center; justify-content: space-between; background: rgba(134,239,92,0.05); border-bottom: 1px solid rgba(134,239,92,0.08); }
.rc-name { font-family: 'Syne', sans-serif; font-weight: 700; color: #d1fad1; font-size: 0.85rem; }
.count-pill { background: #86ef5c; color: #071a09; font-family: 'Syne', sans-serif; font-weight: 800; font-size: 0.75rem; padding: 2px 10px; border-radius: 999px; }
.img-lbl { font-size: 0.62rem; letter-spacing: 0.12em; text-transform: uppercase; color: rgba(210,252,210,0.35); margin-bottom: 4px; }
.total-banner { background: linear-gradient(90deg, rgba(134,239,92,0.14), rgba(134,239,92,0.04)); border: 1px solid rgba(134,239,92,0.3); border-radius: 18px; padding: 1.4rem 2rem; text-align: center; margin: 0.5rem auto 1.5rem; max-width: 380px; }
.total-num { font-family: 'Syne', sans-serif; font-size: 3rem; font-weight: 800; color: #86ef5c; line-height: 1; }
.total-lbl { color: rgba(210,252,210,0.55); font-size: 0.88rem; margin-top: 6px; }
div[data-testid="stImage"] img { border-radius: 10px; width: 100%; }
.stProgress > div > div { background: #86ef5c !important; }
.stSlider > div > div > div { background: #86ef5c !important; }
div[data-testid="stDataFrame"] { border-radius: 12px; overflow: hidden; border: 1px solid rgba(134,239,92,0.15) !important; }
.stDownloadButton > button { background: rgba(134,239,92,0.15) !important; color: #86ef5c !important; border: 1px solid rgba(134,239,92,0.3) !important; border-radius: 8px !important; font-size: 0.75rem !important; }
</style>
""", unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🌴 MangoAI")
    st.markdown("**Tree Detection & Counter**")
    st.markdown("---")
    st.markdown("### ⚙️ Settings")
    confidence = st.slider("Detection Confidence", 0.1, 0.9, 0.35, 0.05,
                           help="Lower = detects more trees (may include false positives). Higher = only very confident detections.")
    st.markdown("---")
    st.markdown("### 📖 How to use")
    st.markdown("1. Upload your mango tree images\n2. Adjust confidence if needed\n3. Download annotated images\n4. Export results as CSV")
    st.markdown("---")
    st.markdown("### 🧠 Model Info")
    st.markdown("- **Model**: YOLOv8\n- **Trained on**: 150 images\n- **Annotated via**: Roboflow\n- **Epochs**: 50")

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
        draw.rectangle([x1, y1, x2, y2], outline="#00ff00", width=3)
        label = f"Tree {conf:.0%}"
        draw.rectangle([x1, y1 - 16, x1 + len(label)*7, y1], fill="#00ff00")
        draw.text((x1 + 2, y1 - 14), label, fill="#000000")
        count += 1
    return img, count

def pil_to_bytes(img):
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()

# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
  <h1>Mango Tree <span>Detection & Counter</span></h1>
  <p>Upload field or aerial images — YOLOv8 detects and counts every mango tree automatically.</p>
</div>
""", unsafe_allow_html=True)

# ── Upload ────────────────────────────────────────────────────────────────────
st.markdown('<div class="upload-wrap">', unsafe_allow_html=True)
uploaded_files = st.file_uploader("Upload mango tree images (JPG / PNG)", type=["jpg","jpeg","png"], accept_multiple_files=True)
st.markdown('</div>', unsafe_allow_html=True)

# ── Process ───────────────────────────────────────────────────────────────────
if uploaded_files:
    model = load_model()
    results_data = []
    status = st.empty()
    bar = st.progress(0)

    for i, f in enumerate(uploaded_files):
        status.markdown(f"<p style='color:rgba(210,252,210,0.5);text-align:center;font-size:0.82rem;'>Analysing <b style='color:#86ef5c'>{f.name}</b>...</p>", unsafe_allow_html=True)
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
      <div class="metric-card"><div class="metric-val">{total}</div><div class="metric-lbl">Trees Detected</div></div>
      <div class="metric-card"><div class="metric-val">{n_imgs}</div><div class="metric-lbl">Images Analysed</div></div>
      <div class="metric-card"><div class="metric-val">{avg}</div><div class="metric-lbl">Avg per Image</div></div>
      <div class="metric-card"><div class="metric-val">{best}</div><div class="metric-lbl">Best Single Image</div></div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    # ── Summary Table + CSV Export ──
    st.markdown("<h3 style='font-family:Syne,sans-serif;color:#d1fad1;font-size:1rem;margin-bottom:0.8rem;'>📊 Summary Table</h3>", unsafe_allow_html=True)
    df = pd.DataFrame([{"Image": r["name"], "Trees Detected": r["count"], "Avg Confidence": f"{r['conf']:.0%}"} for r in results_data])
    st.dataframe(df, use_container_width=True, hide_index=True)
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("⬇ Export Results as CSV", csv, "mango_tree_results.csv", "text/csv")

    st.markdown('<hr class="divider">', unsafe_allow_html=True)
    st.markdown("<h3 style='font-family:Syne,sans-serif;color:#d1fad1;font-size:1rem;margin-bottom:0.8rem;'>🖼 Detection Results</h3>", unsafe_allow_html=True)

    # ── Per-image results ──
    for r in results_data:
        st.markdown(f"""
        <div class="rc"><div class="rc-head">
          <span class="rc-name">{r['name']}</span>
          <span class="count-pill">🌴 {r['count']} trees</span>
        </div></div>
        """, unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            st.markdown('<p class="img-lbl">Original</p>', unsafe_allow_html=True)
            st.image(r["original"], use_column_width=True)
        with col2:
            st.markdown('<p class="img-lbl">Detected</p>', unsafe_allow_html=True)
            st.image(r["detected"], use_column_width=True)
            st.download_button(f"⬇ Download Annotated Image", pil_to_bytes(r["detected"]),
                               f"detected_{r['name']}", "image/png", key=f"dl_{r['name']}")
        st.markdown("<div style='margin-bottom:1rem'></div>", unsafe_allow_html=True)

    # ── Total ──
    st.markdown(f"""
    <div class="total-banner">
      <div class="total-num">🌴 {total}</div>
      <div class="total-lbl">Total Mango Trees Across All Images</div>
    </div>
    """, unsafe_allow_html=True)

else:
    st.markdown("""
    <p style='text-align:center;color:rgba(210,252,210,0.28);font-size:0.88rem;margin-top:0.5rem;'>
      Upload one or more images above to start detection.
    </p>
    """, unsafe_allow_html=True)
