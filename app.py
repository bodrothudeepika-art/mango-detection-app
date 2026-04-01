Set-Content -Path "app.py" -Encoding UTF8 -Value @"
import streamlit as st
from ultralytics import YOLO
from PIL import Image
import numpy as np
import cv2
import io

st.set_page_config(page_title="Mango Tree Counter", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;900&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    background-color: #0f1f0f;
    color: white;
}

.main { background-color: #0f1f0f; padding: 0; }
.block-container { padding: 0rem 2rem 2rem 2rem; }

.top-bar {
    background: linear-gradient(90deg, #1a3a1a, #2d6a4f);
    padding: 18px 30px;
    border-radius: 0 0 15px 15px;
    display: flex;
    align-items: center;
    margin-bottom: 25px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.4);
}
.top-bar h1 {
    color: white;
    font-size: 28px;
    font-weight: 800;
    margin: 0;
    letter-spacing: 2px;
}

.stat-card {
    background: linear-gradient(135deg, #1b4332, #2d6a4f);
    border-radius: 16px;
    padding: 28px 20px;
    text-align: center;
    box-shadow: 0 4px 20px rgba(0,0,0,0.3);
    margin-bottom: 20px;
}
.stat-card .label {
    font-size: 13px;
    color: #95d5b2;
    text-transform: uppercase;
    letter-spacing: 2px;
    margin-bottom: 8px;
}
.stat-card .number {
    font-size: 64px;
    font-weight: 900;
    color: white;
    line-height: 1;
}

.upload-card {
    background-color: #1a2e1a;
    border: 2px dashed #40916c;
    border-radius: 16px;
    padding: 30px 20px;
    text-align: center;
    margin-bottom: 20px;
}
.upload-card h3 {
    color: #95d5b2;
    font-size: 16px;
    margin-bottom: 5px;
}
.upload-card p {
    color: #52b788;
    font-size: 13px;
}

.image-card {
    background-color: #1a2e1a;
    border-radius: 16px;
    padding: 15px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.3);
    margin-bottom: 20px;
}
.image-card .card-title {
    font-size: 13px;
    color: #95d5b2;
    text-transform: uppercase;
    letter-spacing: 2px;
    margin-bottom: 10px;
    font-weight: 600;
}

.confidence-card {
    background-color: #1a2e1a;
    border-radius: 16px;
    padding: 20px;
    margin-bottom: 20px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.3);
}
.confidence-card .label {
    font-size: 13px;
    color: #95d5b2;
    text-transform: uppercase;
    letter-spacing: 2px;
    margin-bottom: 5px;
}
.confidence-card .value {
    font-size: 28px;
    font-weight: 700;
    color: #52b788;
}

.stButton > button {
    background: linear-gradient(135deg, #2d6a4f, #40916c);
    color: white;
    border: none;
    border-radius: 10px;
    padding: 12px 20px;
    font-size: 15px;
    font-weight: 700;
    width: 100%;
    letter-spacing: 1px;
    cursor: pointer;
    margin-bottom: 10px;
}
.stButton > button:hover {
    background: linear-gradient(135deg, #40916c, #52b788);
}

.footer {
    text-align: center;
    color: #2d6a4f;
    font-size: 13px;
    margin-top: 30px;
    padding: 15px;
    border-top: 1px solid #1b4332;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="top-bar">
    <h1>MANGO TREE COUNTER</h1>
</div>
""", unsafe_allow_html=True)

@st.cache_resource
def load_model():
    return YOLO("best.pt")

model = load_model()

left_col, right_col = st.columns([1, 2.5])

with left_col:
    st.markdown("""
    <div class="upload-card">
        <h3>Upload Farm Image</h3>
        <p>Drag & drop or browse<br>JPG, JPEG, PNG supported</p>
    </div>
    """, unsafe_allow_html=True)

    uploaded_file = st.file_uploader("", type=["jpg", "jpeg", "png"], label_visibility="collapsed")

    if uploaded_file is not None:
        image = Image.open(uploaded_file).convert("RGB")
        img_array = np.array(image)

        with st.spinner("Detecting trees..."):
            results = model(img_array)

        tree_count = len(results[0].boxes)
        boxes = results[0].boxes
        confidences = boxes.conf.tolist() if len(boxes) > 0 else []
        avg_conf = round(sum(confidences) / len(confidences) * 100, 1) if confidences else 0

        annotated = results[0].plot()
        annotated_rgb = cv2.cvtColor(annotated, cv2.COLOR_BGR2RGB)

        st.markdown(f"""
        <div class="stat-card">
            <div class="label">Total Detected Trees</div>
            <div class="number">{tree_count}</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="confidence-card">
            <div class="label">Model Confidence</div>
            <div class="value">{avg_conf}%</div>
        </div>
        """, unsafe_allow_html=True)

        result_pil = Image.fromarray(annotated_rgb)
        buf = io.BytesIO()
        result_pil.save(buf, format="JPEG")
        st.download_button(
            label="Download Result Image",
            data=buf.getvalue(),
            file_name="mango_detection_result.jpg",
            mime="image/jpeg"
        )

    else:
        st.markdown("""
        <div class="stat-card">
            <div class="label">Total Detected Trees</div>
            <div class="number">--</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="confidence-card">
            <div class="label">How to Use</div>
            <div style="color:#52b788; font-size:14px; margin-top:8px; line-height:1.8;">
                1. Upload your aerial farm photo<br>
                2. AI detects all mango trees<br>
                3. See total count instantly<br>
                4. Download the result image
            </div>
        </div>
        """, unsafe_allow_html=True)

with right_col:
    if uploaded_file is not None:
        st.markdown('<div class="image-card"><div class="card-title">Detected Mango Trees</div>', unsafe_allow_html=True)
        st.image(annotated_rgb, use_column_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="image-card" style="height:400px; display:flex; align-items:center; justify-content:center;">
            <div style="text-align:center; color:#2d6a4f;">
                <div style="font-size:60px; margin-bottom:15px;">🌿</div>
                <div style="font-size:18px; font-weight:600;">Your detection result will appear here</div>
                <div style="font-size:14px; margin-top:8px;">Upload an image to get started</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

st.markdown('<div class="footer">Mango Tree Counter | Powered by YOLOv8 & Streamlit</div>', unsafe_allow_html=True)
"@
