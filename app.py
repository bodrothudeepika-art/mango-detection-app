import streamlit as st
from ultralytics import YOLO
from PIL import Image
import numpy as np
import cv2
import io
import os

st.set_page_config(page_title="Mango Tree Counter", layout="wide")

st.title("🥭 Mango Tree Counter")

# ✅ Debug (optional - remove later)
st.write("Files:", os.listdir())

# Load model
@st.cache_resource
def load_model():
    return YOLO("best.pt")   # make sure this file exists

model = load_model()

uploaded_file = st.file_uploader("Upload Image", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    image = Image.open(uploaded_file).convert("RGB")
    img_array = np.array(image)

    st.write("Detecting...")

    results = model(img_array)

    tree_count = len(results[0].boxes)

    annotated = results[0].plot()
    annotated_rgb = cv2.cvtColor(annotated, cv2.COLOR_BGR2RGB)

    st.write(f"🌴 Trees detected: {tree_count}")
    st.image(annotated_rgb)

else:
    st.write("Upload an image to start")
