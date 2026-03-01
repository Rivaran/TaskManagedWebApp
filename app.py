import streamlit as st
import os
from datetime import date
from streamlit_supabase_auth import login_form
from supabase import create_client

# -----------------------
# Supabase client
# -----------------------
supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)

st.set_page_config(page_title="Daily Check App", layout="centered")

selected_date = date.today()

# -----------------------
# Login
# -----------------------
session = login_form(
    url=os.getenv("SUPABASE_URL"),
    apiKey=os.getenv("SUPABASE_KEY"),
    providers=["google"]
)

if not session:
    st.stop()

access_token = session["access_token"]

supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)

supabase.postgrest.auth(access_token)

user_id = session["user"]["id"]

# -----------------------
# DB操作
# -----------------------
def get_tasks():
    response = supabase.table("tasks") \
        .select("*") \
        .eq("task_date", str(selected_date)) \
        .order("id") \
        .execute()

    return response.data

def get_all_tasks():
    response = supabase.table("tasks") \
        .select("*") \
        .order("id") \
        .execute()

    return response.data

def add_task():
    if st.session_state.new_task.strip():
        supabase.table("tasks").insert({
            "user_id": user_id,
            "task_date": str(selected_date),
            "title": st.session_state.new_task,
            "done": False
        }).execute()

        st.session_state.new_task = ""
        st.rerun()

def mark_done(task_id):
    supabase.table("tasks") \
        .update({"done": True}) \
        .eq("id", task_id) \
        .execute()
    st.rerun()

def delete_task(task_id):
    supabase.table("tasks") \
        .delete() \
        .eq("id", task_id) \
        .execute()
    st.rerun()

# -----------------------
# UI
# -----------------------
colA, colB = st.columns([2.5, 1])

with colA:

    st.markdown("### 📝 今日やることリスト")

    # -----------------------
    # 日付選択
    # -----------------------
    selected_date = st.date_input("日付を選択", date.today())

    st.text_input("やることを追加", key="new_task")
    st.button("追加", on_click=add_task)

    tasks = get_tasks()

    st.subheader("📌 今日のタスク")

    for task in tasks:
        if not task["done"]:
            col1, col2 = st.columns([8,1])

            with col1:
                if st.checkbox(task["title"], key=f"check_{task['id']}"):
                    mark_done(task["id"])

            with col2:
                if st.button("🗑", key=f"del_{task['id']}"):
                    delete_task(task["id"])

    st.subheader("✅ やったこと")

    for task in tasks:
        if task["done"]:
            st.write(f"✔ {task['title']}")

with colB:

    st.markdown("##### 🏆 達成スタンプ")

    all_tasks = get_all_tasks()

    done_count = sum(1 for task in all_tasks if task["done"])

    st.markdown(
        f"<div style='font-size:40px; line-height:1.6;'>"
        + "🌸 " * done_count +
        "</div>",
        unsafe_allow_html=True
    )
