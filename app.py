import streamlit as st
import json
import os
from datetime import date

st.set_page_config(page_title="Daily Check App", layout="centered")

DATA_FILE = "tasks.json"

# -----------------------
# データ読み込み
# -----------------------
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def add_task():
    if st.session_state.new_task.strip():
        data[selected_date_str].append({
            "title": st.session_state.new_task,
            "done": False
        })
        save_data(data)
        st.session_state.new_task = ""

data = load_data()

col1, col2 = st.columns([2.5, 1])

with col1:

    # -----------------------
    # 日付選択
    # -----------------------
    selected_date = st.date_input("日付を選択", date.today())
    selected_date_str = str(selected_date)

    if selected_date_str not in data:
        data[selected_date_str] = []

    st.markdown("### 📝 今日やることリスト")

    # -----------------------
    # タスク追加
    # -----------------------
    st.text_input("やることを追加", key="new_task")
    st.button("追加", on_click=add_task)

    st.subheader("📌 今日のタスク")
    for i, task in enumerate(data[selected_date_str]):
        if not task["done"]:
            if st.checkbox(task["title"], key=f"todo_{i}"):
                data[selected_date_str][i]["done"] = True
                save_data(data)
                st.rerun()

    st.subheader("✅ やったこと")

    for task in data[selected_date_str]:
        if task["done"]:
            st.write(f"✔ {task['title']}")

with col2:
    st.markdown("##### 🏆 達成スタンプ")

    done_count = sum(
        task["done"]
        for tasks in data.values()
        for task in tasks
    )

    st.markdown(
        f"<div style='font-size:40px; line-height:1.6;'>"
        + "🌸 " * done_count +
        "</div>",
        unsafe_allow_html=True
    )

