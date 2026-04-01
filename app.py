import streamlit as st
from PIL import Image
import io
import base64

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="MangoAI – Tree Detection & Counter",
    page_icon="🥭",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS + HTML background scene ───────────────────────────────────────
BACKGROUND_HTML = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,700;1,600&family=DM+Sans:wght@400;500;600&display=swap');

/* ── Reset & base ── */
html, body, [data-testid="stAppViewContainer"] {
    font-family: 'DM Sans', sans-serif !important;
    background: transparent !important;
}
[data-testid="stAppViewContainer"] > .main {
    background: transparent !important;
}
[data-testid="stSidebar"] {
    background: rgba(92, 58, 26, 0.96) !important;
    border-right: 2px solid rgba(232,130,12,0.35) !important;
}
[data-testid="stSidebar"] * { color: #FDF6E8 !important; }
[data-testid="stSidebar"] .stSlider > div > div { background: #E8820C !important; }

/* ── Full-page nature background ── */
.scene-bg {
    position: fixed;
    top: 0; left: 0; right: 0; bottom: 0;
    background: linear-gradient(
        180deg,
        #6BBDE8 0%,
        #A8DDF5 15%,
        #C5ECA0 40%,
        #6BAF2A 60%,
        #4A8A1A 73%,
        #2E5A0A 100%
    );
    z-index: -1;
    overflow: hidden;
}

/* Sun */
.sun {
    position: absolute; top: 30px; right: 120px;
    width: 72px; height: 72px;
    background: radial-gradient(circle, #FFE566 35%, #FFB800 65%, rgba(255,184,0,0) 100%);
    border-radius: 50%;
    animation: pulse-sun 4s ease-in-out infinite;
}
@keyframes pulse-sun { 0%,100%{box-shadow:0 0 28px 10px rgba(255,200,0,.35)} 50%{box-shadow:0 0 44px 18px rgba(255,200,0,.55)} }

/* Clouds */
.cloud { position: absolute; background: rgba(255,255,255,0.88); border-radius: 50px; }
.cloud::before { content:''; position:absolute; background:rgba(255,255,255,0.88); border-radius:50%; }
.c1{width:100px;height:30px;top:44px;left:80px;animation:drift 18s linear infinite;}
.c1::before{width:50px;height:42px;top:-20px;left:14px;}
.c2{width:72px;height:22px;top:72px;left:240px;animation:drift 24s linear infinite;}
.c2::before{width:34px;height:28px;top:-13px;left:10px;}
.c3{width:80px;height:24px;top:54px;right:200px;animation:drift 20s linear infinite reverse;}
.c3::before{width:38px;height:32px;top:-14px;left:12px;}
@keyframes drift { from{transform:translateX(0)} to{transform:translateX(30px)} }

/* ── MANGO TREES ── */
.tree { position: absolute; bottom: 130px; }
.trunk { position:absolute; bottom:0; left:50%; transform:translateX(-50%); background:#6B3D10; border-radius:4px; }
.canopy { position:absolute; border-radius:50%; }
.mfruit { position:absolute; width:14px; height:18px; background:linear-gradient(135deg,#FFCC00 30%,#FF8C00); border-radius:50% 50% 50% 60%/60% 50% 60% 50%; }

/* Big left tree */
.tL{left:20px;}
.tL .trunk{width:26px;height:110px;}
.tL .l1{width:150px;height:140px;background:#1A5E0E;bottom:96px;left:-62px;}
.tL .l2{width:124px;height:114px;background:#297A1C;bottom:118px;left:-34px;}
.tL .l3{width:100px;height:94px;background:#3EA02A;bottom:138px;left:-10px;}
.tL .f1{top:40px;left:34px;} .tL .f2{top:60px;left:14px;} .tL .f3{top:56px;left:72px;} .tL .f4{top:76px;left:46px;}

/* Big right tree */
.tR{right:20px;}
.tR .trunk{width:26px;height:110px;}
.tR .l1{width:150px;height:140px;background:#1A5E0E;bottom:96px;left:-64px;}
.tR .l2{width:124px;height:114px;background:#297A1C;bottom:118px;left:-44px;}
.tR .l3{width:100px;height:94px;background:#3EA02A;bottom:138px;left:-6px;}
.tR .f1{top:38px;left:20px;} .tR .f2{top:58px;left:58px;} .tR .f3{top:52px;left:84px;} .tR .f4{top:72px;left:38px;}

/* Mid trees */
.tML{left:140px;}
.tML .trunk{width:18px;height:78px;}
.tML .l1{width:114px;height:102px;background:#195C0E;bottom:66px;left:-48px;}
.tML .l2{width:90px;height:82px;background:#268018;bottom:86px;left:-26px;}
.tML .f1{top:36px;left:24px;} .tML .f2{top:52px;left:50px;}

.tMR{right:140px;}
.tMR .trunk{width:18px;height:78px;}
.tMR .l1{width:114px;height:102px;background:#195C0E;bottom:66px;left:-48px;}
.tMR .l2{width:90px;height:82px;background:#268018;bottom:86px;left:-26px;}
.tMR .f1{top:36px;left:20px;} .tMR .f2{top:52px;left:46px;}

/* Ground */
.ground{position:absolute;bottom:0;left:0;right:0;height:135px;background:linear-gradient(180deg,#4E8C1E 0%,#3A6C14 30%,#5C3A1A 70%,#3A2008 100%);}
.gwave{position:absolute;top:-22px;left:-8px;right:-8px;height:42px;background:#5EA820;border-radius:50% 50% 0 0/100% 100% 0 0;}

/* ── FARMER CHARACTER ── */
.farmer-wrap{position:absolute;bottom:134px;left:50%;transform:translateX(-50%);display:flex;flex-direction:column;align-items:center;width:80px;}
.f-hat-brim{width:64px;height:15px;background:#C05A08;border-radius:50%;margin-bottom:-5px;z-index:2;position:relative;}
.f-hat-top{width:38px;height:22px;background:#E8820C;border-radius:7px 7px 3px 3px;margin:0 auto;position:relative;z-index:3;}
.f-head{width:40px;height:40px;background:#D4956A;border-radius:50%;margin:0 auto;position:relative;z-index:4;}
.f-eye-l,.f-eye-r{position:absolute;width:5px;height:5px;background:#3A2008;border-radius:50%;top:14px;}
.f-eye-l{left:9px;} .f-eye-r{right:9px;}
.f-smile{position:absolute;top:24px;left:10px;width:20px;height:8px;border-bottom:2.5px solid #3A2008;border-radius:0 0 50% 50%;}
.f-neck{width:16px;height:9px;background:#C07A50;margin:0 auto;}
.f-body{width:50px;height:50px;background:#2E7A50;border-radius:7px 7px 12px 12px;margin:0 auto;position:relative;}
.f-collar{position:absolute;top:0;left:50%;transform:translateX(-50%);width:0;height:0;border-left:9px solid transparent;border-right:9px solid transparent;border-top:14px solid #D4956A;}
.f-pocket{position:absolute;top:14px;right:9px;width:11px;height:9px;background:#256640;border-radius:2px;border:1px solid rgba(0,0,0,.2);}
.f-arm-l{position:absolute;top:5px;left:-16px;width:17px;height:38px;background:#2E7A50;border-radius:9px;transform:rotate(14deg);}
.f-arm-r{position:absolute;top:5px;right:-16px;width:17px;height:38px;background:#2E7A50;border-radius:9px;transform:rotate(-14deg);}
.f-hand-l{position:absolute;bottom:-7px;left:1px;width:13px;height:13px;background:#D4956A;border-radius:50%;}
.f-hand-r{position:absolute;bottom:-7px;right:1px;width:13px;height:13px;background:#D4956A;border-radius:50%;}
.f-tool{position:absolute;bottom:-7px;right:-1px;width:4px;height:42px;background:#8B5E3C;border-radius:2px;transform:rotate(-10deg);transform-origin:bottom center;}
.f-pants{width:50px;height:34px;background:#3A5A9A;margin:0 auto;position:relative;border-radius:2px 2px 7px 7px;}
.f-pants::before{content:'';position:absolute;top:0;left:50%;transform:translateX(-50%);width:2px;height:100%;background:rgba(0,0,0,.2);}
.f-boots{display:flex;justify-content:center;gap:7px;}
.f-boot{width:22px;height:15px;background:#3A2008;border-radius:2px 2px 7px 7px;}
.f-shadow{width:54px;height:9px;background:rgba(0,0,0,.18);border-radius:50%;margin:3px auto 0;}

/* ── MAIN CONTENT CARD ── */
.main-card {
    background: rgba(253,246,232,0.97);
    border-radius: 22px;
    border: 2px solid rgba(232,130,12,0.35);
    padding: 28px 32px 24px;
    box-shadow: 0 12px 40px rgba(0,0,0,0.22);
    max-width: 640px;
    margin: 0 auto;
}
.app-title {
    font-family: 'Playfair Display', serif !important;
    font-size: 2.4rem !important;
    font-weight: 700 !important;
    color: #5C3A1A !important;
    text-align: center;
    line-height: 1.2;
    margin-bottom: 0.2rem;
}
.app-tagline {
    font-family: 'Playfair Display', serif;
    font-style: italic;
    font-size: 1rem;
    color: #E8820C;
    text-align: center;
    margin-bottom: 1rem;
}
.app-subtitle {
    font-size: 0.88rem;
    color: #7A5A30;
    text-align: center;
    line-height: 1.6;
    margin-bottom: 1.2rem;
}
.divider-line {
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(232,130,12,0.5), transparent);
    margin: 1rem 0;
}

/* ── Sidebar labels ── */
[data-testid="stSidebar"] .stMarkdown h2 {
    font-family: 'Playfair Display', serif !important;
    color: #FFB800 !important;
    font-size: 1.2rem !important;
}
[data-testid="stSidebar"] label {
    color: #F5E8CC !important;
    font-weight: 500 !important;
}

/* ── Upload button ── */
[data-testid="stFileUploader"] {
    border: 2px dashed #E8820C !important;
    border-radius: 14px !important;
    background: rgba(232,130,12,0.06) !important;
    padding: 1rem !important;
}
[data-testid="stFileUploader"] button {
    background: linear-gradient(135deg, #E8820C, #B85A05) !important;
    color: white !important;
    border-radius: 8px !important;
    border: none !important;
}

/* ── Metric cards ── */
[data-testid="metric-container"] {
    background: rgba(232,130,12,0.1) !important;
    border: 1px solid rgba(232,130,12,0.3) !important;
    border-radius: 12px !important;
    padding: 12px !important;
}
[data-testid="metric-container"] label {
    color: #7A5A30 !important;
}
[data-testid="metric-container"] [data-testid="stMetricValue"] {
    color: #B85A05 !important;
    font-weight: 700 !important;
}

/* ── Buttons ── */
.stButton > button {
    background: linear-gradient(135deg, #E8820C, #B85A05) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    padding: 0.5rem 1.5rem !important;
    font-family: 'DM Sans', sans-serif !important;
    transition: opacity .2s !important;
}
.stButton > button:hover { opacity: 0.88 !important; }
</style>

<!-- BACKGROUND SCENE -->
<div class="scene-bg">
  <div class="sun"></div>
  <div class="cloud c1"></div>
  <div class="cloud c2"></div>
  <div class="cloud c3"></div>

  <!-- Big Left Tree -->
  <div class="tree tL">
    <div class="canopy l1"></div>
    <div class="canopy l2"></div>
    <div class="canopy l3">
      <div class="mfruit f1"></div><div class="mfruit f2"></div>
      <div class="mfruit f3"></div><div class="mfruit f4"></div>
    </div>
    <div class="trunk"></div>
  </div>

  <!-- Mid Left Tree -->
  <div class="tree tML">
    <div class="canopy l1"></div>
    <div class="canopy l2">
      <div class="mfruit f1"></div><div class="mfruit f2"></div>
    </div>
    <div class="trunk"></div>
  </div>

  <!-- Mid Right Tree -->
  <div class="tree tMR">
    <div class="canopy l1"></div>
    <div class="canopy l2">
      <div class="mfruit f1"></div><div class="mfruit f2"></div>
    </div>
    <div class="trunk"></div>
  </div>

  <!-- Big Right Tree -->
  <div class="tree tR">
    <div class="canopy l1"></div>
    <div class="canopy l2"></div>
    <div class="canopy l3">
      <div class="mfruit f1"></div><div class="mfruit f2"></div>
      <div class="mfruit f3"></div><div class="mfruit f4"></div>
    </div>
    <div class="trunk"></div>
  </div>

  <!-- FARMER -->
  <div class="farmer-wrap">
    <div class="f-hat-top"></div>
    <div class="f-hat-brim"></div>
    <div class="f-head">
      <div class="f-eye-l"></div>
      <div class="f-eye-r"></div>
      <div class="f-smile"></div>
    </div>
    <div class="f-neck"></div>
    <div class="f-body">
      <div class="f-collar"></div>
      <div class="f-pocket"></div>
      <div class="f-arm-l"><div class="f-hand-l"></div></div>
      <div class="f-arm-r">
        <div class="f-hand-r"></div>
        <div class="f-tool"></div>
      </div>
    </div>
    <div class="f-pants"></div>
    <div class="f-boots">
      <div class="f-boot"></div>
      <div class="f-boot"></div>
    </div>
    <div class="f-shadow"></div>
  </div>

  <!-- Ground -->
  <div class="ground"><div class="gwave"></div></div>
</div>
"""

st.markdown(BACKGROUND_HTML, unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🥭 MangoAI")
    st.markdown("*Tree Detection & Counter*")
    st.divider()

    st.markdown("### ⚙️ Detection Settings")
    confidence = st.slider(
        "Detection Confidence",
        min_value=0.0, max_value=1.0,
        value=0.30, step=0.01,
        help="Higher = fewer but more confident detections"
    )

    st.divider()
    st.markdown("### 📖 How to Use")
    steps = [
        "📤 Upload orchard images",
        "🎚️ Adjust confidence threshold",
        "🔍 View annotated results",
        "💾 Download images & CSV",
    ]
    for i, s in enumerate(steps, 1):
        st.markdown(f"**{i}.** {s}")

    st.divider()
    st.markdown(
        "<div style='font-size:11px;color:#C8A878;text-align:center;'>Powered by YOLOv8<br>🌾 Field Intelligence for Farmers</div>",
        unsafe_allow_html=True
    )

# ── Main content ──────────────────────────────────────────────────────────────
st.markdown(
    """
    <div style='text-align:center;margin-top:2rem;'>
      <div style='font-family:"Playfair Display",serif;font-style:italic;font-size:1rem;color:#E8820C;margin-bottom:.4rem;'>
        🌾 Field Intelligence for Farmers
      </div>
      <div style='font-family:"Playfair Display",serif;font-size:2.6rem;font-weight:700;color:#5C3A1A;
                  background:rgba(253,246,232,0.85);display:inline-block;padding:.2rem 1.2rem;
                  border-radius:14px;line-height:1.2;'>
        Mango Orchard Tree Counter
      </div>
      <div style='font-size:.9rem;color:#5C3A1A;margin-top:.6rem;
                  background:rgba(253,246,232,0.75);display:inline-block;
                  padding:.3rem 1rem;border-radius:10px;'>
        Upload field or aerial photographs — our YOLOv8 model automatically detects &amp; counts every tree.
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown("<div style='margin-top:1.4rem;'></div>", unsafe_allow_html=True)

# Upload zone
col_l, col_c, col_r = st.columns([1, 3, 1])
with col_c:
    uploaded_files = st.file_uploader(
        "📷 Upload orchard images (JPG / PNG)",
        type=["jpg", "jpeg", "png"],
        accept_multiple_files=True,
        help="Upload one or more aerial or field photos of your mango orchard.",
    )

# ── Results ───────────────────────────────────────────────────────────────────
if uploaded_files:
    st.markdown("<div style='margin-top:1rem;'></div>", unsafe_allow_html=True)

    # Summary metrics
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("📁 Images Uploaded", len(uploaded_files))
    m2.metric("🎯 Confidence", f"{confidence:.2f}")
    m3.metric("🌳 Trees Detected", "–")   # replace with your model output
    m4.metric("📊 Avg / Image", "–")       # replace with your model output

    st.markdown("<div style='margin-top:1rem;'></div>", unsafe_allow_html=True)

    for uploaded_file in uploaded_files:
        with st.expander(f"🖼️ {uploaded_file.name}", expanded=True):
            img = Image.open(uploaded_file)
            col_img, col_info = st.columns([2, 1])

            with col_img:
                st.image(img, caption="Uploaded Image", use_column_width=True)

            with col_info:
                st.markdown(
                    f"""
                    <div style='background:rgba(253,246,232,0.95);border-radius:12px;
                                border:1px solid rgba(232,130,12,.3);padding:16px;'>
                      <div style='font-family:"Playfair Display",serif;font-size:1.1rem;
                                  color:#B85A05;margin-bottom:10px;font-weight:700;'>
                        📋 Image Info
                      </div>
                      <p style='color:#5C3A1A;font-size:.85rem;margin:4px 0;'>
                        <b>File:</b> {uploaded_file.name}
                      </p>
                      <p style='color:#5C3A1A;font-size:.85rem;margin:4px 0;'>
                        <b>Size:</b> {img.size[0]} × {img.size[1]} px
                      </p>
                      <p style='color:#5C3A1A;font-size:.85rem;margin:4px 0;'>
                        <b>Confidence:</b> {confidence:.2f}
                      </p>
                      <hr style='border:none;border-top:1px solid rgba(232,130,12,.25);margin:10px 0;'>
                      <p style='color:#9A7A50;font-size:.8rem;font-style:italic;'>
                        🔄 Run detection to see tree count &amp; annotations.
                      </p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                if st.button("🔍 Detect Trees", key=f"detect_{uploaded_file.name}"):
                    with st.spinner("Running YOLOv8 detection..."):
                        # ── Replace this block with your actual YOLOv8 inference ──
                        # from ultralytics import YOLO
                        # model = YOLO("best.pt")
                        # results = model(img, conf=confidence)
                        # annotated = results[0].plot()
                        # tree_count = len(results[0].boxes)
                        # st.image(annotated, caption=f"Detected {tree_count} trees")
                        st.info("✅ Plug in your YOLOv8 model here!")

else:
    # Placeholder when no images uploaded
    st.markdown(
        """
        <div style='text-align:center;margin-top:2rem;padding:2rem 1rem;
                    background:rgba(253,246,232,0.75);border-radius:18px;
                    border:2px dashed rgba(232,130,12,0.4);max-width:500px;margin-left:auto;margin-right:auto;'>
          <div style='font-size:3rem;margin-bottom:.6rem;'>🌿 🥭 🌳</div>
          <div style='font-size:.9rem;color:#7A5A30;'>
            Upload one or more orchard images above to begin counting.
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
