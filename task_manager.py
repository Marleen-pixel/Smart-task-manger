"""
Smart Task Manager - A Python CLI task management application
Supports categories, error handling, persistent storage, search, edit, and due dates
Created by: Maheen Affan
"""

import json
import os
from datetime import datetime
from typing import List, Dict, Optional


def display_logo():
    """Display the beautiful logo"""
    logo = """
    
    ╔══════════════════════════════════════════════════════════════════════╗
    ║                                                                      ║
    ║           ███████╗███╗   ███╗ █████╗ ██████╗ ████████╗            ║
    ║           ██╔════╝████╗ ████║██╔══██╗██╔══██╗╚══██╔══╝            ║
    ║           ██████��╗██╔████╔██║███████║██████╔╝   ██║               ║
    ║           ╚════██║██║╚██╔╝██║██╔══██║██╔══██╗   ██║               ║
    ║           ███████║██║ ╚═╝ ██║██║  ██║██║  ██║   ██║               ║
    ║           ╚══════╝╚═╝     ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝               ║
    ║                                                                      ║
    ║                    🎯 T A S K   M A N A G E R 🎯                    ║
    ║                                                                      ║
    ║        ✨ Organize • Track • Achieve ✨                            ║
    ║                                                                      ║
    ║        📋 Version 2.0 - Enhanced Edition                           ║
    ║        👨‍💻 Created by: Maheen Affan                                 ║
    ║                                                                      ║
    ╚══════════════════════════════════════════════════════════════════════╝
    
    """
    print(logo)


class TaskManager:
    """Manages tasks with categories, search, edit, and due dates"""
    
    def __init__(self, filename: str = "tasks.json"):
        self.filename = filename
        self.data = self.load_tasks()
        self.tasks = self.data.get("tasks", [])
        self.task_counter = self.data.get("task_counter", 0)
    
    def load_tasks(self) -> Dict:
        """Load tasks from file with error handling"""
        try:
            if os.path.exists(self.filename):
                with open(self.filename, "r") as file:
                    data = json.load(file)
                    # Support both old and new format
                    if isinstance(data, list):
                        return {"tasks": data, "task_counter": len(data)}
                    return data
            return {"tasks": [], "task_counter": 0}
        except json.JSONDecodeError:
            print(f"⚠️  Error: Corrupted task file. Starting fresh.")
            return {"tasks": [], "task_counter": 0}
        except IOError as e:
            print(f"⚠️  Error reading file: {e}")
            return {"tasks": [], "task_counter": 0}
    
    def save_tasks(self) -> bool:
        """Save tasks to file with error handling"""
        try:
            data = {
                "task_counter": self.task_counter,
                "tasks": self.tasks
            }
            with open(self.filename, "w") as file:
                json.dump(data, file, indent=2)
            return True
        except IOError as e:
            print(f"❌ Error saving tasks: {e}")
            return False
    
    def add_task(self, title: str, category: str = "General", description: str = "", due_date: str = "") -> bool:
        """Add a new task with validation"""
        if not title or not title.strip():
            print("❌ Error: Task title cannot be empty!")
            return False
        
        # Validate due date format if provided
        if due_date:
            try:
                datetime.strptime(due_date, "%Y-%m-%d")
            except ValueError:
                print("❌ Error: Due date must be in format YYYY-MM-DD!")
                return False
        
        self.task_counter += 1
        task = {
            "id": self.task_counter,
            "title": title.strip(),
            "category": category.strip() or "General",
            "description": description.strip(),
            "due_date": due_date,
            "completed": False,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self.tasks.append(task)
        print(f"✅ Task added: '{title}' in category '{category}'")
        return self.save_tasks()
    
    def view_tasks(self, category: Optional[str] = None) -> None:
        """View tasks, optionally filtered by category"""
        if not self.tasks:
            print("📭 No tasks found!")
            return
        
        filtered_tasks = self.tasks
        if category:
            filtered_tasks = [t for t in self.tasks if t["category"].lower() == category.lower()]
            if not filtered_tasks:
                print(f"📭 No tasks found in category '{category}'")
                return
        
        print("\n" + "=" * 90)
        print(f"{'ID':<4} {'Status':<8} {'Task':<30} {'Category':<12} {'Due Date':<12}")
        print("=" * 90)
        
        for task in filtered_tasks:
            status = "✅" if task["completed"] else "⭕"
            task_title = task["title"][:27] + "..." if len(task["title"]) > 27 else task["title"]
            category_name = task["category"][:9] + "..." if len(task["category"]) > 9 else task["category"]
            due_date = task.get("due_date", "") or "N/A"
            print(f"{task['id']:<4} {status:<8} {task_title:<30} {category_name:<12} {due_date:<12}")
        
        print("=" * 90 + "\n")
    
    def view_task_details(self, task_id: int) -> None:
        """View detailed information about a specific task"""
        try:
            task_id = int(task_id)
            task = next((t for t in self.tasks if t["id"] == task_id), None)
            
            if not task:
                print(f"❌ Error: Task with ID {task_id} not found!")
                return
            
            print("\n" + "=" * 50)
            print(f"📋 Task Details (ID: {task['id']})")
            print("=" * 50)
            print(f"Title:       {task['title']}")
            print(f"Category:    {task['category']}")
            print(f"Status:      {'✅ Completed' if task['completed'] else '⭕ Pending'}")
            print(f"Description: {task.get('description', 'N/A')}")
            print(f"Due Date:    {task.get('due_date', 'N/A')}")
            print(f"Created:     {task['created_at']}")
            print("=" * 50 + "\n")
        except ValueError:
            print("❌ Error: Please enter a valid task ID (number)")
    
    def search_tasks(self, keyword: str) -> None:
        """Search tasks by title or description"""
        if not keyword or not keyword.strip():
            print("❌ Error: Search keyword cannot be empty!")
            return
        
        keyword = keyword.lower()
        filtered_tasks = [
            t for t in self.tasks 
            if keyword in t["title"].lower() or keyword in t.get("description", "").lower()
        ]
        
        if not filtered_tasks:
            print(f"📭 No tasks found matching '{keyword}'")
            return
        
        print(f"\n🔍 Search Results for '{keyword}':")
        print("=" * 90)
        print(f"{'ID':<4} {'Status':<8} {'Task':<30} {'Category':<12} {'Due Date':<12}")
        print("=" * 90)
        
        for task in filtered_tasks:
            status = "✅" if task["completed"] else "⭕"
            task_title = task["title"][:27] + "..." if len(task["title"]) > 27 else task["title"]
            category_name = task["category"][:9] + "..." if len(task["category"]) > 9 else task["category"]
            due_date = task.get("due_date", "") or "N/A"
            print(f"{task['id']:<4} {status:<8} {task_title:<30} {category_name:<12} {due_date:<12}")
        
        print("=" * 90 + "\n")
    
    def edit_task(self, task_id: int, title: Optional[str] = None, category: Optional[str] = None, 
                  description: Optional[str] = None, due_date: Optional[str] = None) -> bool:
        """Edit an existing task"""
        try:
            task_id = int(task_id)
            task = next((t for t in self.tasks if t["id"] == task_id), None)
            
            if not task:
                print(f"❌ Error: Task with ID {task_id} not found!")
                return False
            
            # Update fields if provided
            if title and title.strip():
                task["title"] = title.strip()
            
            if category and category.strip():
                task["category"] = category.strip()
            
            if description is not None:
                task["description"] = description.strip()
            
            if due_date is not None:
                if due_date:  # If due_date is provided and not empty
                    try:
                        datetime.strptime(due_date, "%Y-%m-%d")
                        task["due_date"] = due_date
                    except ValueError:
                        print("❌ Error: Due date must be in format YYYY-MM-DD!")
                        return False
                else:
                    task["due_date"] = ""
            
            print(f"✅ Task updated: '{task['title']}'")
            return self.save_tasks()
        except ValueError:
            print("❌ Error: Please enter a valid task ID (number)")
            return False
    
    def delete_task(self, task_id: int) -> bool:
        """Delete a task by ID with validation"""
        try:
            task_id = int(task_id)
            task = next((t for t in self.tasks if t["id"] == task_id), None)
            
            if not task:
                print(f"❌ Error: Task with ID {task_id} not found!")
                return False
            
            self.tasks.remove(task)
            print(f"✅ Task deleted: '{task['title']}'")
            return self.save_tasks()
        except ValueError:
            print("❌ Error: Please enter a valid task ID (number)")
            return False
    
    def mark_complete(self, task_id: int) -> bool:
        """Mark a task as completed"""
        try:
            task_id = int(task_id)
            task = next((t for t in self.tasks if t["id"] == task_id), None)
            
            if not task:
                print(f"❌ Error: Task with ID {task_id} not found!")
                return False
            
            task["completed"] = not task["completed"]
            status = "completed" if task["completed"] else "incomplete"
            print(f"✅ Task marked as {status}: '{task['title']}'")
            return self.save_tasks()
        except ValueError:
            print("❌ Error: Please enter a valid task ID (number)")
            return False
    
    def get_categories(self) -> set:
        """Get all unique categories"""
        return set(task["category"] for task in self.tasks)
    
    def show_stats(self) -> None:
        """Show task statistics"""
        if not self.tasks:
            print("📭 No tasks to display stats for!")
            return
        
        total = len(self.tasks)
        completed = sum(1 for t in self.tasks if t["completed"])
        pending = total - completed
        
        # Count by category
        categories = self.get_categories()
        category_stats = {}
        for cat in categories:
            cat_tasks = [t for t in self.tasks if t["category"] == cat]
            cat_completed = sum(1 for t in cat_tasks if t["completed"])
            category_stats[cat] = (len(cat_tasks), cat_completed)
        
        print("\n" + "=" * 50)
        print(f"📊 Task Statistics")
        print("=" * 50)
        print(f"Total Tasks: {total}")
        print(f"Completed: {completed} ✅")
        print(f"Pending: {pending} ⭕")
        print(f"Progress: {(completed/total*100):.1f}%" if total > 0 else "Progress: 0%")
        print("\n📂 By Category:")
        for cat in sorted(categories):
            cat_total, cat_completed = category_stats[cat]
            print(f"  {cat}: {cat_completed}/{cat_total} ✅")
        print("=" * 50 + "\n")


def show_menu() -> None:
    """Display the main menu"""
    print("\n" + "=" * 60)
    print("🎯 Smart Task Manager - Enhanced Edition")
    print("=" * 60)
    print("📝 Task Management:")
    print("  [add]      - Add a new task")
    print("  [view]     - View all tasks")
    print("  [filter]   - Filter tasks by category")
    print("  [search]   - Search tasks by keyword")
    print("  [details]  - View task details")
    print("  [edit]     - Edit an existing task")
    print("  [complete] - Mark task as complete/incomplete")
    print("  [delete]   - Delete a task")
    print("\n📊 Statistics & Help:")
    print("  [stats]    - Show task statistics")
    print("  [help]     - Show this menu")
    print("  [exit]     - Exit the application")
    print("=" * 60 + "\n")


def main():
    """Main application loop"""
    display_logo()
    manager = TaskManager()
    
    print("\n👋 Hello Maheen! Welcome to Smart Task Manager!")
    print("Type 'help' to see all available commands.\n")
    
    while True:
        try:
            action = input("Enter command: ").strip().lower()
            
            if action == "add":
                title = input("Enter task title: ").strip()
                if not title:
                    print("❌ Task title cannot be empty!")
                    continue
                
                print("Categories: General, Work, Personal, Shopping, Health, Other")
                category = input("Enter category (or press Enter for 'General'): ").strip() or "General"
                
                description = input("Enter task description (optional, press Enter to skip): ").strip()
                
                due_date = input("Enter due date - YYYY-MM-DD (optional, press Enter to skip): ").strip()
                if due_date:
                    try:
                        datetime.strptime(due_date, "%Y-%m-%d")
                    except ValueError:
                        print("❌ Invalid date format! Using no due date.")
                        due_date = ""
                
                manager.add_task(title, category, description, due_date)
            
            elif action == "view":
                manager.view_tasks()
            
            elif action == "filter":
                categories = manager.get_categories()
                if not categories:
                    print("📭 No categories found!")
                    continue
                
                print(f"Available categories: {', '.join(sorted(categories))}")
                category = input("Enter category to filter: ").strip()
                manager.view_tasks(category)
            
            elif action == "search":
                keyword = input("Enter search keyword: ").strip()
                manager.search_tasks(keyword)
            
            elif action == "details":
                manager.view_tasks()
                task_id = input("Enter task ID to view details: ").strip()
                manager.view_task_details(task_id)
            
            elif action == "edit":
                manager.view_tasks()
                task_id = input("Enter task ID to edit: ").strip()
                
                try:
                    task_id_int = int(task_id)
                    task = next((t for t in manager.tasks if t["id"] == task_id_int), None)
                    
                    if not task:
                        print(f"❌ Error: Task with ID {task_id} not found!")
                        continue
                    
                    print(f"\nEditing Task: {task['title']}")
                    print("(Press Enter to keep current value)\n")
                    
                    new_title = input(f"New title [{task['title']}]: ").strip()
                    new_category = input(f"New category [{task['category']}]: ").strip()
                    new_description = input(f"New description [{task.get('description', '')}]: ").strip()
                    new_due_date_input = input(f"New due date [{task.get('due_date', 'N/A')}]: ").strip()
                    
                    new_due_date = new_due_date_input if new_due_date_input else None
                    
                    manager.edit_task(
                        task_id,
                        title=new_title if new_title else None,
                        category=new_category if new_category else None,
                        description=new_description if new_description else None,
                        due_date=new_due_date
                    )
                except ValueError:
                    print("❌ Error: Please enter a valid task ID (number)")
            
            elif action == "complete":
                manager.view_tasks()
                task_id = input("Enter task ID to mark complete/incomplete: ").strip()
                manager.mark_complete(task_id)
            
            elif action == "delete":
                manager.view_tasks()
                task_id = input("Enter task ID to delete: ").strip()
                confirm = input("Are you sure? (yes/no): ").strip().lower()
                if confirm == "yes":
                    manager.delete_task(task_id)
                else:
                    print("❌ Deletion cancelled")
            
            elif action == "stats":
                manager.show_stats()
            
            elif action == "help":
                show_menu()
            
            elif action == "exit":
                print("\n👋 Goodbye Maheen! Keep up with your tasks! 🎯\n")
                break
            
            else:
                print("❌ Invalid command! Type 'help' to see available commands.")
        
        except KeyboardInterrupt:
            print("\n\n⚠️  Application interrupted. Goodbye!")
            break
        except Exception as e:
            print(f"❌ Unexpected error: {e}")


if __name__ == "__main__":
    main()
