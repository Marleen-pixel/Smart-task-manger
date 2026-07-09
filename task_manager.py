"""
Smart Task Manager - A Python CLI task management application
Supports categories, error handling, and persistent storage
"""

import json
import os
from datetime import datetime
from typing import List, Dict, Optional


class TaskManager:
    """Manages tasks with categories and persistence"""
    
    def __init__(self, filename: str = "tasks.json"):
        self.filename = filename
        self.tasks = self.load_tasks()
    
    def load_tasks(self) -> List[Dict]:
        """Load tasks from file with error handling"""
        try:
            if os.path.exists(self.filename):
                with open(self.filename, "r") as file:
                    return json.load(file)
            return []
        except json.JSONDecodeError:
            print(f"⚠️  Error: Corrupted task file. Starting fresh.")
            return []
        except IOError as e:
            print(f"⚠️  Error reading file: {e}")
            return []
    
    def save_tasks(self) -> bool:
        """Save tasks to file with error handling"""
        try:
            with open(self.filename, "w") as file:
                json.dump(self.tasks, file, indent=2)
            return True
        except IOError as e:
            print(f"❌ Error saving tasks: {e}")
            return False
    
    def add_task(self, title: str, category: str = "General") -> bool:
        """Add a new task with validation"""
        if not title or not title.strip():
            print("❌ Error: Task title cannot be empty!")
            return False
        
        task = {
            "id": len(self.tasks) + 1,
            "title": title.strip(),
            "category": category.strip() or "General",
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
        
        print("\n" + "=" * 70)
        print(f"{'ID':<4} {'Status':<8} {'Task':<35} {'Category':<15}")
        print("=" * 70)
        
        for task in filtered_tasks:
            status = "✅" if task["completed"] else "⭕"
            task_title = task["title"][:32] + "..." if len(task["title"]) > 32 else task["title"]
            category_name = task["category"][:12] + "..." if len(task["category"]) > 12 else task["category"]
            print(f"{task['id']:<4} {status:<8} {task_title:<35} {category_name:<15}")
        
        print("=" * 70 + "\n")
    
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
        
        print("\n" + "=" * 40)
        print(f"📊 Task Statistics")
        print("=" * 40)
        print(f"Total Tasks: {total}")
        print(f"Completed: {completed} ✅")
        print(f"Pending: {pending} ⭕")
        print(f"Progress: {(completed/total*100):.1f}%" if total > 0 else "Progress: 0%")
        print("=" * 40 + "\n")


def show_menu() -> None:
    """Display the main menu"""
    print("\n" + "=" * 50)
    print("🎯 Smart Task Manager")
    print("=" * 50)
    print("Commands:")
    print("  [add]      - Add a new task")
    print("  [view]     - View all tasks")
    print("  [filter]   - Filter tasks by category")
    print("  [complete] - Mark task as complete/incomplete")
    print("  [delete]   - Delete a task")
    print("  [stats]    - Show task statistics")
    print("  [help]     - Show this menu")
    print("  [exit]     - Exit the application")
    print("=" * 50 + "\n")


def main():
    """Main application loop"""
    manager = TaskManager()
    
    print("\n👋 Hello Marleen! Welcome to Smart Task Manager!")
    print("Type 'help' to see all available commands.\n")
    
    while True:
        try:
            action = input("Enter command: ").strip().lower()
            
            if action == "add":
                title = input("Enter task title: ").strip()
                if not title:
                    print("❌ Task title cannot be empty!")
                    continue
                
                print("Categories: General, Work, Personal, Shopping, Other")
                category = input("Enter category (or press Enter for 'General'): ").strip() or "General"
                manager.add_task(title, category)
            
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
            
            elif action == "complete":
                manager.view_tasks()
                try:
                    task_id = input("Enter task ID to mark complete/incomplete: ").strip()
                    manager.mark_complete(task_id)
                except ValueError:
                    print("❌ Error: Please enter a valid task ID")
            
            elif action == "delete":
                manager.view_tasks()
                try:
                    task_id = input("Enter task ID to delete: ").strip()
                    manager.delete_task(task_id)
                except ValueError:
                    print("❌ Error: Please enter a valid task ID")
            
            elif action == "stats":
                manager.show_stats()
            
            elif action == "help":
                show_menu()
            
            elif action == "exit":
                print("\n👋 Goodbye Marleen! Keep up with your tasks! 🎯\n")
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
