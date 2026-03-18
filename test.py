import streamlit as st
from PIL import Image
from streamlit_drawable_canvas import st_canvas
import pandas as pd
import os
import random

st.set_page_config(page_title="風景写真アンケート", layout="wide")
st.title("風景写真アンケート")

if "started" not in st.session_state:
    st.write("回答を始める前に以下を入力してください。")
    age = st.number_input("年齢", min_value=10, max_value=100, step=1)
    gender = st.radio("性別", ["男性", "女性", "その他", "回答しない"])
    if st.button("アンケートを開始する"):
        if os.path.exists("results.csv"):
            df_existing = pd.read_csv("results.csv")
            next_id = int(df_existing["subject_id"].max()) + 1
        else:
            next_id = 1
        st.session_state.subject_id = next_id
        st.session_state.age = age
        st.session_state.gender = gender
        st.session_state.started = True
        st.session_state.img_index = 0
        main_images = [
            "tests/data_compressed/red-zeppelin-egzWylxCy0o-unsplash.jpg",
            "tests/data_compressed/red-zeppelin-HwdxtOgUbe0-unsplash.jpg",
            "tests/data_compressed/red-zeppelin-KgMvud4m2Ao-unsplash.jpg",
            "tests/data_compressed/sergei-gussev-aJw0Q8F861Q-unsplash.jpg",
            "tests/data_compressed/thu-n-minh-m18gG7B-Bn4-unsplash.jpg",
            "tests/data_compressed/michael-douglas-6K4yFEdOjcw-unsplash.jpg",
            "tests/data_compressed/daniel-twal-LmDZNJVxjlA-unsplash.jpg",
            "tests/data_compressed/kir-shu-v0priul9iJ8-unsplash.jpg",
            "tests/data_compressed/simi-iluyomade-Wq2hWoaSBtY-unsplash.jpg",
            "tests/data_compressed/jack-delulio-7PCH0uapixc-unsplash.jpg",
        ]
        shuffled = main_images.copy()
        random.shuffle(shuffled)
        st.session_state.shuffled_images = ["tests/1_compressed.jpg"] + shuffled
        st.rerun()
    st.stop()

image_list = st.session_state.shuffled_images

if st.session_state.img_index >= len(image_list):
    st.success("すべての回答が完了しました。ありがとうございました！")
    st.stop()

current_img_path = image_list[st.session_state.img_index]

if st.session_state.img_index == 0:
    st.info("最初の1枚は練習です。操作に慣れてから次へ進んでください。")
    st.write("練習")
else:
    st.write(f"画像 {st.session_state.img_index} / {len(image_list) - 1}")

img = Image.open(current_img_path)
img = img.resize((800, 600), Image.LANCZOS)

st.write("1：全く美しくない　　10：非常に美しい")
score = st.slider("この風景の美しさを10段階で評価してください", 1, 10, 5)

st.write("美しいと感じる部分を矩形で囲んでください（最大3つ）")
canvas_result = st_canvas(
    fill_color="rgba(255, 0, 0, 0.1)",
    stroke_width=2,
    stroke_color="red",
    background_image=img,
    update_streamlit=False,
    width=800,
    height=600,
    drawing_mode="rect",
    key=f"canvas_{st.session_state.img_index}",
)

if st.button("次の画像へ"):
    if st.session_state.img_index > 0:
        objects = canvas_result.json_data["objects"] if canvas_result.json_data else []
        rects = []
        for obj in objects[:3]:
            rects.append({
                "x": obj["left"],
                "y": obj["top"],
                "width": obj["width"],
                "height": obj["height"]
            })
        row = {
            "subject_id": st.session_state.subject_id,
            "age": st.session_state.age,
            "gender": st.session_state.gender,
            "image": os.path.basename(current_img_path),
            "score": score,
            "rect1": rects[0] if len(rects) > 0 else None,
            "rect2": rects[1] if len(rects) > 1 else None,
            "rect3": rects[2] if len(rects) > 2 else None,
        }
        df = pd.DataFrame([row])
        csv_path = "results.csv"
        if os.path.exists(csv_path):
            df.to_csv(csv_path, mode='a', header=False, index=False)
        else:
            df.to_csv(csv_path, index=False)
    st.session_state.img_index += 1
    st.rerun()
