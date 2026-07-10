import streamlit as st
import sqlite3
import random

# --- 1. Page Setup ---
st.set_page_config(page_title="Smart Task Manager", layout="wide")
st.title("🎯 Smart Task Manager")

# --- 2. Database Setup (SQLite) ---
conn = sqlite3.connect('tasks.db')
c = conn.cursor()
# Create table if it doesn't exist
c.execute('''CREATE TABLE IF NOT EXISTS tasks 
             (id INTEGER PRIMARY KEY AUTOINCREMENT, 
              task TEXT, 
              category TEXT, 
              priority TEXT, 
              status TEXT)''')
conn.commit()

# --- 3. Sidebar Navigation ---
menu = st.sidebar.radio("Navigation", ["Add Task", "View Tasks", "Motivation"])

# --- 4. Add Task Section ---
if menu == "Add Task":
    st.subheader("➕ Add New Task")
    
    title = st.text_input("Task Title")
    category = st.selectbox("Category", ["General", "Work", "Personal", "Shopping", "Health"])
    priority = st.selectbox("Priority", ["High", "Medium", "Low"])
    
    if st.button("Add Task"):
        if title:
            # Save task to database
            c.execute("INSERT INTO tasks (task, category, priority, status) VALUES (?, ?, ?, ?)", 
                      (title, category, priority, "Pending"))
            conn.commit()
            st.success(f"✅ Task '{title}' added successfully!")
        else:
            st.error("Title cannot be empty!")

# --- 5. View Tasks Section ---
elif menu == "View Tasks":
    st.subheader("📋 My Tasks")
    
    # Fetch tasks from database
    c.execute("SELECT * FROM tasks")
    tasks = c.fetchall()
    
    if len(tasks) == 0:
        st.info("No tasks yet. Go to 'Add Task' to create one!")
    else:
        completed_count = 0
        
        for t in tasks:
            # t[0]=id, t[1]=task, t[2]=category, t[3]=priority, t[4]=status
            col1, col2, col3 = st.columns([3, 1, 1])
            
            # Display task status
            if t[4] == "Completed":
                completed_count += 1
                col1.write(f"✅ **~{t[1]}~** ({t[2]}) - Priority: {t[3]}")
            else:
                col1.write(f"⭕ **{t[1]}** ({t[2]}) - Priority: {t[3]}")
            
            # Toggle (Complete/Pending) button
            if col2.button("Toggle", key=f"toggle_{t[0]}"):
                new_status = "Pending" if t[4] == "Completed" else "Completed"
                c.execute("UPDATE tasks SET status = ? WHERE id = ?", (new_status, t[0]))
                conn.commit()
                st.rerun() 
                
            # Delete button
            if col3.button("Delete", key=f"del_{t[0]}"):
                c.execute("DELETE FROM tasks WHERE id = ?", (t[0],))
                conn.commit()
                st.rerun() 
        
        # --- Progress and Celebration ---
        if len(tasks) > 0:
            st.write("---")
            progress = completed_count / len(tasks)
            st.write(f"### Your Progress: {int(progress * 100)}%")
            st.progress(progress)
            
            if progress == 1.0:
                st.balloons()
                st.success("Great job finishing all your tasks! 🎉")

# --- 6. Motivation Section ---
elif menu == "Motivation":
    st.subheader("💡 Daily Motivation")
    quotes = [
        "Believe in yourself!", 
        "Code like a pro!", 
        "Small steps, big results!", 
        "Consistency is key!",
        "You are doing great, Maheen!"
    ]
    if st.button("Get Motivation"):
        st.info(random.choice(quotes))
