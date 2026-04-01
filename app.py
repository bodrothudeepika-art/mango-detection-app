import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import tempfile
import os
import time

st.set_page_config(
    page_title="MangoSense · Tree Counter",
    page_icon="🥭",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;900&family=Outfit:wght@300;400;500;600&display=swap');

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
html, body, [class*="css"] { font-family: 'Outfit', sans-serif; }

.stApp {
    background: #fdf6ec;
    background-image:
        radial-gradient(ellipse 80% 50% at 50% -10%, rgba(255,180,30,0.18) 0%, transparent 70%),
        radial-gradient(ellipse 60% 40% at 90% 110%, rgba(255,120,20,0.12) 0%, transparent 65%);
    min-height: 100vh;
}

header[data-testid="stHeader"] { background: transparent; }

/* ── HERO ── */
.hero-wrap {
    position: relative;
    text-align: center;
    padding: 4rem 1rem 2.5rem;
    overflow: hidden;
}
.hero-orb {
    position: absolute;
    border-radius: 50%;
    filter: blur(60px);
    pointer-events: none;
    z-index: 0;
}
.orb-a { width: 340px; height: 340px; background: rgba(255,180,30,0.22); top: -80px; left: 50%; transform: translateX(-50%); }
.orb-b { width: 200px; height: 200px; background: rgba(255,110,20,0.13); top: 20px; left: 15%; }
.orb-c { width: 180px; height: 180px; background: rgba(230,200,50,0.15); top: 40px; right: 12%; }
.hero-inner { position: relative; z-index: 1; }

.brand-chip {
    display: inline-flex; align-items: center; gap: 7px;
    background: rgba(255,255,255,0.7);
    border: 1px solid rgba(230,150,20,0.35);
    border-radius: 999px;
    padding: 5px 16px 5px 10px;
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #b56a00;
    margin-bottom: 22px;
    backdrop-filter: blur(8px);
}
.brand-chip .dot {
    width: 7px; height: 7px; border-radius: 50%;
    background: #f59e0b;
    animation: pulse-dot 2s ease-in-out infinite;
}
@keyframes pulse-dot {
    0%,100% { opacity: 1; transform: scale(1); }
    50% { opacity: 0.5; transform: scale(0.7); }
}

.hero-title {
    font-family: 'Playfair Display', Georgia, serif;
    font-size: clamp(2.4rem, 5.5vw, 4rem);
    font-weight: 900;
    color: #1a1008;
    line-height: 1.08;
    letter-spacing: -0.02em;
    margin-bottom: 18px;
}
.hero-title .accent { color: #e07b00; }
.hero-title .light { color: #7c5e2a; }

.hero-sub {
    font-size: 1.02rem;
    font-weight: 300;
    color: #7c5e2a;
    max-width: 500px;
    margin: 0 auto 2.5rem;
    line-height: 1.65;
}

/* ── STAT PILLS ── */
.stat-row {
    display: flex;
    gap: 10px;
    justify-content: center;
    flex-wrap: wrap;
    margin-bottom: 2.8rem;
}
.stat-pill {
    background: rgba(255,255,255,0.75);
    border: 1px solid rgba(230,150,20,0.28);
    border-radius: 12px;
    padding: 12px 22px;
    text-align: center;
    backdrop-filter: blur(10px);
    min-width: 130px;
    transition: transform 0.2s, box-shadow 0.2s;
}
.stat-pill:hover { transform: translateY(-3px); box-shadow: 0 8px 24px rgba(180,100,0,0.12); }
.stat-num {
    font-family: 'Playfair Display', serif;
    font-size: 1.8rem;
    font-weight: 700;
    color: #d97706;
    line-height: 1;
}
.stat-lbl {
    font-size: 0.65rem;
    font-weight: 600;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: #a07830;
    margin-top: 4px;
}

/* ── DIVIDER ── */
.mango-divider {
    display: flex; align-items: center; gap: 12px;
    max-width: 680px; margin: 0 auto 2.2rem;
}
.mango-divider::before, .mango-divider::after {
    content: ''; flex: 1;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(200,130,20,0.3), transparent);
}
.divider-icon { font-size: 1.1rem; }

/* ── UPLOAD BOX ── */
.upload-section { max-width: 680px; margin: 0 auto 2.5rem; }

[data-testid="stFileUploader"] {
    background: rgba(255,255,255,0.65) !important;
    border: 2px dashed rgba(215,140,20,0.45) !important;
    border-radius: 20px !important;
    padding: 2.2rem 2rem !important;
    backdrop-filter: blur(12px) !important;
    transition: border-color 0.25s !important;
}
[data-testid="stFileUploader"]:hover {
    border-color: rgba(215,140,20,0.75) !important;
}
[data-testid="stFileUploader"] label {
    color: #7c5e2a !important;
    font-weight: 400 !important;
}

/* ── RESULTS ── */
.results-heading {
    font-family: 'Playfair Display', serif;
    font-size: 1.35rem;
    font-weight: 700;
    color: #1a1008;
    margin-bottom: 1.2rem;
    display: flex;
    align-items: center;
    gap: 10px;
}

.result-card {
    background: rgba(255,255,255,0.78);
    border: 1px solid rgba(215,150,20,0.22);
    border-radius: 20px;
    overflow: hidden;
    margin-bottom: 1.6rem;
    backdrop-filter: blur(10px);
    box-shadow: 0 2px 20px rgba(180,100,0,0.06);
    transition: box-shadow 0.25s;
}
.result-card:hover { box-shadow: 0 6px 32px rgba(180,100,0,0.13); }

.card-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 13px 18px;
    background: linear-gradient(90deg, rgba(255,200,60,0.12), rgba(255,140,20,0.06));
    border-bottom: 1px solid rgba(215,150,20,0.15);
}
.card-filename {
    font-family: 'Playfair Display', serif;
    font-weight: 700;
    font-size: 0.92rem;
    color: #3d2800;
}
.count-badge {
    background: linear-gradient(135deg, #f59e0b, #e07b00);
    color: #fff;
    font-family: 'Outfit', sans-serif;
    font-weight: 700;
    font-size: 0.78rem;
    padding: 4px 14px;
    border-radius: 999px;
    letter-spacing: 0.04em;
}

.img-label {
    font-size: 0.62rem;
    font-weight: 600;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: #a07830;
    margin-bottom: 6px;
}

/* ── TOTAL BANNER ── */
.total-banner {
    max-width: 520px;
    margin: 0.5rem auto 3rem;
    background: linear-gradient(135deg, #fff8e6 0%, #fff3d4 100%);
    border: 2px solid rgba(215,150,20,0.4);
    border-radius: 24px;
    padding: 2.4rem 2rem;
    text-align: center;
    box-shadow: 0 10px 40px rgba(180,100,0,0.1);
    position: relative;
    overflow: hidden;
}
.total-banner::before {
    content: '';
    position: absolute;
    top: -30px; right: -30px;
    width: 140px; height: 140px;
    background: radial-gradient(circle, rgba(255,200,60,0.3), transparent 70%);
    border-radius: 50%;
}
.total-banner::after {
    content: '';
    position: absolute;
    bottom: -20px; left: -20px;
    width: 100px; height: 100px;
    background: radial-gradient(circle, rgba(255,140,20,0.2), transparent 70%);
    border-radius: 50%;
}
.total-emoji { font-size: 2.2rem; margin-bottom: 8px; }
.total-num {
    font-family: 'Playfair Display', serif;
    font-size: 4rem;
    font-weight: 900;
    color: #c96b00;
    line-height: 1;
    margin-bottom: 6px;
    position: relative; z-index: 1;
}
.total-sub {
    font-size: 0.9rem;
    font-weight: 400;
    color: #9a6c20;
    position: relative; z-index: 1;
}
.total-images-note {
    font-size: 0.72rem;
    color: #c4922a;
    margin-top: 6px;
    position: relative; z-index: 1;
    letter-spacing: 0.06em;
}

/* ── PROGRESS ── */
.stProgress > div > div { background: linear-gradient(90deg, #f59e0b, #e07b00) !important; border-radius: 999px !important; }

/* ── EMPTY STATE ── */
.empty-hint {
    text-align: center;
    color: #c4922a;
    font-size: 0.88rem;
    margin-top: 0.8rem;
    opacity: 0.7;
}

div[data-testid="stImage"] img { border-radius: 12px; width: 100%; }
</style>
""", unsafe_allow_html=True)


# ── Model loader ──────────────────────────────────────────────────────────────
@st.cache_resource
def load_model():
    import torch
    from ultralytics import YOLO
    model = YOLO("best.pt")
    return model


def draw_boxes(image: Image.Image, boxes) -> Image.Image:
    img = image.copy().convert("RGB")
    draw = ImageDraw.Draw(img)
    for box in boxes:
        x1, y1, x2, y2 = [int(v) for v in box.xyxy[0].tolist()]
        # Outer glow effect (layered rects)
        for offset, alpha in [(4, 40), (2, 80)]:
            draw.rectangle(
                [x1 - offset, y1 - offset, x2 + offset, y2 + offset],
                outline=(255, 160, 20, alpha), width=1
            )
        draw.rectangle([x1, y1, x2, y2], outline="#e07b00", width=3)
        # Label pill
        draw.rectangle([x1, y1 - 22, x1 + 62, y1], fill="#e07b00")
        draw.text((x1 + 5, y1 - 18), "🥭 Tree", fill="#ffffff")
    return img


# ── HERO ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero-wrap">
  <div class="hero-orb orb-a"></div>
  <div class="hero-orb orb-b"></div>
  <div class="hero-orb orb-c"></div>
  <div class="hero-inner">
    <div class="brand-chip"><span class="dot"></span>MangoSense AI · YOLOv8</div>
    <h1 class="hero-title">
      Detect Every<br>
      <span class="accent">Mango Tree</span><br>
      <span class="light">Instantly</span>
    </h1>
    <p class="hero-sub">
      Upload field or aerial images — our trained AI model identifies and counts every mango tree with precision.
    </p>
  </div>
</div>
""", unsafe_allow_html=True)

# ── UPLOAD ────────────────────────────────────────────────────────────────────
st.markdown('<div class="upload-section">', unsafe_allow_html=True)
uploaded_files = st.file_uploader(
    "Drop your mango field images here (JPG / PNG)",
    type=["jpg", "jpeg", "png"],
    accept_multiple_files=True,
    label_visibility="visible",
)
st.markdown('</div>', unsafe_allow_html=True)

# ── PROCESSING ────────────────────────────────────────────────────────────────
if uploaded_files:
    model = load_model()
    results_data = []

    status = st.empty()
    bar = st.progress(0)

    for i, f in enumerate(uploaded_files):
        status.markdown(
            f"<p style='color:#9a6c20;text-align:center;font-size:0.85rem;padding:0.4rem 0;'>"
            f"Scanning <b style='color:#e07b00'>{f.name}</b> for mango trees …</p>",
            unsafe_allow_html=True,
        )
        bar.progress(i / len(uploaded_files))

        image = Image.open(f).convert("RGB")
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
            image.save(tmp.name)
            tmp_path = tmp.name

        result = model(tmp_path, verbose=False)[0]
        count = len(result.boxes)
        annotated = draw_boxes(image, result.boxes)

        results_data.append({
            "name": f.name,
            "original": image,
            "detected": annotated,
            "count": count,
        })
        os.unlink(tmp_path)

    bar.progress(1.0)
    time.sleep(0.25)
    status.empty()
    bar.empty()

    # ── SUMMARY METRICS ──────────────────────────────────────────────────────
    total = sum(r["count"] for r in results_data)
    n_imgs = len(results_data)
    avg = round(total / n_imgs, 1) if n_imgs else 0
    highest = max(results_data, key=lambda r: r["count"])

    st.markdown(f"""
    <div class="stat-row">
      <div class="stat-pill">
        <div class="stat-num">{total}</div>
        <div class="stat-lbl">Trees Found</div>
      </div>
      <div class="stat-pill">
        <div class="stat-num">{n_imgs}</div>
        <div class="stat-lbl">Images Scanned</div>
      </div>
      <div class="stat-pill">
        <div class="stat-num">{avg}</div>
        <div class="stat-lbl">Avg / Image</div>
      </div>
      <div class="stat-pill">
        <div class="stat-num">{highest['count']}</div>
        <div class="stat-lbl">Most in One Image</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="mango-divider">
      <span class="divider-icon">🥭</span>
    </div>
    """, unsafe_allow_html=True)

    # ── PER-IMAGE RESULTS ────────────────────────────────────────────────────
    st.markdown('<p class="results-heading">🔍 Detection Results</p>', unsafe_allow_html=True)

    for r in results_data:
        st.markdown(f"""
        <div class="result-card">
          <div class="card-header">
            <span class="card-filename">{r['name']}</span>
            <span class="count-badge">🥭 {r['count']} {'tree' if r['count'] == 1 else 'trees'} detected</span>
          </div>
        </div>
        """, unsafe_allow_html=True)

        col1, col2 = st.columns(2, gap="medium")
        with col1:
            st.markdown('<p class="img-label">Original Image</p>', unsafe_allow_html=True)
            st.image(r["original"], use_column_width=True)
        with col2:
            st.markdown('<p class="img-label">AI Detection Overlay</p>', unsafe_allow_html=True)
            st.image(r["detected"], use_column_width=True)

        st.markdown("<div style='margin-bottom:0.4rem'></div>", unsafe_allow_html=True)

    # ── TOTAL BANNER ─────────────────────────────────────────────────────────
    st.markdown(f"""
    <div class="total-banner">
      <div class="total-emoji">🥭</div>
      <div class="total-num">{total}</div>
      <div class="total-sub">Total Mango Trees Detected</div>
      <div class="total-images-note">Across all {n_imgs} uploaded {'image' if n_imgs == 1 else 'images'}</div>
    </div>
    """, unsafe_allow_html=True)

else:
    st.markdown(
        "<p class='empty-hint'>Upload one or more field images above to begin detection.</p>",
        unsafe_allow_html=True,
    )
