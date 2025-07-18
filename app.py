import streamlit as st
import pickle
import numpy as np
from deepface import DeepFace
import os

st.set_page_config(page_title="おかずAIプロトタイプ🍑", page_icon="🍑", layout="centered")

# カスタムCSS
st.markdown("""
    <style>
        .title {
            font-size: 50px;
            font-weight: bold;
            color: #ff69b4;
            text-align: center;
            margin-bottom: 10px;
        }
        .subtitle {
            font-size: 20px;
            text-align: center;
            margin-bottom: 30px;
        }
        .result-box {
            border: 2px solid #ff69b4;
            border-radius: 10px;
            padding: 15px;
            margin-top: 20px;
            background-color: #fff0f5;
        }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="title">おかずAIプロトタイプ🍑</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">理想のおかず、AIが探します</div>', unsafe_allow_html=True)

with open('embeddings/actresses_embeddings.pkl', 'rb') as f:
    embeddings = pickle.load(f)

uploaded_file = st.file_uploader("👇 顔画像をアップロード", type=['jpg', 'jpeg', 'png'])

if uploaded_file is not None:

    # 一時的に画像を保存
    with open("uploaded.jpg", "wb") as f:
        f.write(uploaded_file.getbuffer())

    try:
        # 顔ベクトルの取得
        embedding = DeepFace.represent(img_path="uploaded.jpg")[0]["embedding"]

        results = []
        for filename, stored_embedding in embeddings.items():
            dist = np.linalg.norm(np.array(stored_embedding) - np.array(embedding))
            results.append((filename, dist))

        results.sort(key=lambda x: x[1])
        top3 = results[:3]

        for rank, (filename, dist) in enumerate(top3, start=1):
            similarity = round(100 - dist, 2)

            if 'loli' in filename.lower():
                tag = "🎀 ロリ系"
            elif 'gyaru' in filename.lower():
                tag = "🔥 ギャル系"
            else:
                tag = "✨ 王道美人"

            st.markdown(f"""
                <div style='background-color:#f0f0f0;padding:10px;border-radius:10px;margin-bottom:10px'>
                    <b>TOP{rank}：</b> {filename} <br>
                    🧭 類似度：{similarity}% <br>
                    🏷️ 系統：{tag}
                </div>
            """, unsafe_allow_html=True)

    except:
        st.error("❌ 顔が検出できませんでした。別の画像を試してください。")
