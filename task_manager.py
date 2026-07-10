import streamlit as st
import json
import os
from datetime import datetime

# --- پیج سیٹ اپ ---
st.set_page_config(page_title="Smart Task Manager", layout="wide")
st.title("🎯 Smart Task Manager")

# --- ڈیٹا لوڈ اور سیو کے فنکشنز ---
def load_data():
    if os.path.exists("tasks.json"):
        with open("tasks.json", "r") as f:
            return json.load(f)
    return {"tasks": [], "task_counter": 0}

def save_data(data):
    with open("tasks.json", "w") as f:
        json.dump(data, f, indent=2)

data = load_data()
tasks = data.get("tasks", [])

# --- سائیڈ بار (مینو) ---
menu = st.sidebar.radio("Navigation", ["Add Task", "View Tasks", "Statistics"])

# --- ایڈ ٹاسک سیکشن ---
if menu == "Add Task":
    st.subheader("➕ Add New Task")
    title = st.text_input("Task Title")
    category = st.selectbox("Category", ["General", "Work", "Personal", "Shopping", "Health", "Education", "Workout"])
    priority = st.selectbox("Priority", ["LOW", "MEDIUM", "HIGH"])
    due_date = st.date_input("Due Date")
    
    if st.button("Add Task"):
        if title:
            new_task = {
                "id": data["task_counter"] + 1,
                "title": title,
                "category": category,
                "priority": priority,
                "due_date": str(due_date),
                "completed": False
            }
            tasks.append(new_task)
            data["tasks"] = tasks
            data["task_counter"] += 1
            save_data(data)
            st.success(f"✅ Task '{title}' added!")
        else:
            st.error("Title cannot be empty!")

# --- ویو ٹاسک سیکشن ---
elif menu == "View Tasks":
    st.subheader("📋 My Tasks")
    for task in tasks:
        col1, col2, col3 = st.columns([3, 1, 1])
        status = "✅" if task["completed"] else "⭕"
        col1.write(f"{status} **{task['title']}** - {task['category']}")
        
        if col2.button("Toggle", key=f"toggle_{task['id']}"):
            task["completed"] = not task["completed"]
            save_data(data)
            st.rerun()
            
        if col3.button("Delete", key=f"del_{task['id']}"):
            tasks.remove(task)
            save_data(data)
            st.rerun()

# --- سٹیٹس سیکشن ---
elif menu == "Statistics":
    st.subheader("📊 Statistics")
    completed = sum(1 for t in tasks if t["completed"])
    st.metric("Total Tasks", len(tasks))
    st.metric("Completed", completed)
    st.write("Keep it up, Maheen!")
