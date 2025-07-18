import streamlit as st
import pickle
import numpy as np
from deepface import DeepFace
import os

st.title("おかずAIプロトタイプ🍑")

with open('embeddings/actresses_embeddings.pkl', 'rb') as f:
    embeddings = pickle.load(f)

uploaded_file = st.file_uploader("顔画像をアップロードしてください", type=['jpg', 'jpeg', 'png'])

if uploaded_file is not None:
    with open("temp.jpg", "wb") as f:
        f.write(uploaded_file.read())

    st.image("temp.jpg", caption="アップロード画像", use_column_width=True)

    try:
        embedding = DeepFace.represent(img_path="temp.jpg", model_name='Facenet')[0]["embedding"]

        min_dist = float('inf')
        closest_filename = None

        for filename, stored_embedding in embeddings.items():
            dist = np.linalg.norm(np.array(stored_embedding) - np.array(embedding))
            if dist < min_dist:
                min_dist = dist
                closest_filename = filename

        st.success(f"✅ 一番似ているのは: {closest_filename}")
        st.write(f"🧭 類似度: {round(100 - min_dist, 2)}%")
    except:
        st.error("❌ 顔が検出できませんでした。別の画像を試してください。")
