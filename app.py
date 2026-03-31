import streamlit as st
from PIL import Image
from ultralytics import YOLO
import tempfile

st.title("Mango Tree Counter 🌳🥭")

model = YOLO("best.pt")

uploaded_file = st.file_uploader("Upload an image", type=["jpg", "png", "jpeg"])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    
    # Save temp file
    temp_file = tempfile.NamedTemporaryFile(delete=False)
    temp_file.write(uploaded_file.read())

    # Run YOLO
    results = model(temp_file.name)

    # Show result
    result_img = results[0].plot()
    st.image(result_img, caption="Detection Result", use_column_width=True)
