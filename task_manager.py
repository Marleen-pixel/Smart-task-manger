"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    SMART TASK MANAGER - PROFESSIONAL EDITION v3.0            ║
║                           Created by: Maheen Affan                           ║
║                                                                              ║
║   🎯 Features: Add • View • Search • Edit • Delete • Filter • Statistics     ║
║   💾 Storage: Persistent JSON with automatic backup                         ║
║   🔒 Security: Input validation, error handling, confirmation dialogs       ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import json
import os
import sys
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from enum import Enum


class TaskPriority(Enum):
    """Task priority levels"""
    LOW = "🟢 Low"
    MEDIUM = "🟡 Medium"
    HIGH = "🔴 High"


class TaskStatus(Enum):
    """Task status"""
    PENDING = "⭕ Pending"
    COMPLETED = "✅ Completed"


class Colors:
    """ANSI color codes for terminal"""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class TaskManager:
    """
    Professional Task Manager with full CRUD operations.
    Handles persistent storage, validation, and error management.
    """
    
    CONFIG_VERSION = "3.0"
    DEFAULT_FILENAME = "tasks.json"
    BACKUP_FILENAME = "tasks_backup.json"
    
    def __init__(self, filename: str = DEFAULT_FILENAME):
        """Initialize TaskManager with file and load existing data"""
        self.filename = filename
        self.backup_filename = filename.replace(".json", "_backup.json")
        self.data = self._load_tasks()
        self.tasks: List[Dict] = self.data.get("tasks", [])
        self.task_counter: int = self.data.get("task_counter", 0)
        self.version: str = self.data.get("version", self.CONFIG_VERSION)
    
    def _load_tasks(self) -> Dict:
        """
        Load tasks from JSON file with comprehensive error handling.
        Supports backward compatibility with old format.
        """
        try:
            if os.path.exists(self.filename):
                try:
                    with open(self.filename, "r", encoding="utf-8") as file:
                        data = json.load(file)
                        
                        # Support old format (list) → new format (dict)
                        if isinstance(data, list):
                            self._print_info("Converting old format to new format...")
                            return {
                                "version": self.CONFIG_VERSION,
                                "tasks": data,
                                "task_counter": len(data),
                                "created_at": datetime.now().isoformat()
                            }
                        return data
                except json.JSONDecodeError:
                    self._print_error("File corrupted! Starting with backup...")
                    return self._restore_from_backup()
            
            return {
                "version": self.CONFIG_VERSION,
                "tasks": [],
                "task_counter": 0,
                "created_at": datetime.now().isoformat()
            }
        
        except IOError as e:
            self._print_error(f"File read error: {e}")
            return {"version": self.CONFIG_VERSION, "tasks": [], "task_counter": 0}
    
    def _restore_from_backup(self) -> Dict:
        """Attempt to restore from backup file"""
        try:
            if os.path.exists(self.backup_filename):
                with open(self.backup_filename, "r", encoding="utf-8") as file:
                    data = json.load(file)
                    self._print_success("✅ Restored from backup!")
                    return data
        except Exception as e:
            self._print_error(f"Backup restoration failed: {e}")
        
        return {"version": self.CONFIG_VERSION, "tasks": [], "task_counter": 0}
    
    def save_tasks(self) -> bool:
        """
        Save tasks to JSON file with backup creation.
        
        Returns:
            bool: True if save successful, False otherwise
        """
        try:
            # Create backup before saving
            if os.path.exists(self.filename):
                try:
                    with open(self.filename, "r", encoding="utf-8") as f:
                        with open(self.backup_filename, "w", encoding="utf-8") as backup:
                            backup.write(f.read())
                except Exception:
                    pass  # Backup creation failure shouldn't stop save
            
            # Save current data
            data = {
                "version": self.CONFIG_VERSION,
                "task_counter": self.task_counter,
                "tasks": self.tasks,
                "last_updated": datetime.now().isoformat()
            }
            
            with open(self.filename, "w", encoding="utf-8") as file:
                json.dump(data, file, indent=2, ensure_ascii=False)
            
            return True
        
        except IOError as e:
            self._print_error(f"Save failed: {e}")
            return False
    
    def add_task(
        self,
        title: str,
        category: str = "General",
        description: str = "",
        due_date: str = "",
        priority: str = "MEDIUM"
    ) -> bool:
        """
        Add a new task with comprehensive validation.
        
        Args:
            title: Task title (required, max 100 chars)
            category: Task category (default: General)
            description: Task details (optional)
            due_date: Due date in YYYY-MM-DD format (optional)
            priority: Priority level (LOW/MEDIUM/HIGH)
        
        Returns:
            bool: True if task added successfully, False otherwise
        """
        # Validate title
        if not title or not title.strip():
            self._print_error("Task title cannot be empty!")
            return False
        
        if len(title) > 100:
            self._print_error("Task title cannot exceed 100 characters!")
            return False
        
        title = title.strip()
        
        # Validate due date
        if due_date:
            if not self._validate_date(due_date):
                self._print_error("Invalid date format! Use YYYY-MM-DD")
                return False
        
        # Validate priority
        valid_priorities = ["LOW", "MEDIUM", "HIGH"]
        if priority.upper() not in valid_priorities:
            self._print_error(f"Invalid priority! Use: {', '.join(valid_priorities)}")
            return False
        
        # Create task
        self.task_counter += 1
        
        task = {
            "id": self.task_counter,
            "title": title,
            "category": category.strip() or "General",
            "description": description.strip(),
            "due_date": due_date,
            "priority": priority.upper(),
            "completed": False,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        self.tasks.append(task)
        
        if self.save_tasks():
            self._print_success(f"✅ Task added: '{title}'")
            return True
        
        self.task_counter -= 1
        self.tasks.pop()
        return False
    
    def view_tasks(self, category: Optional[str] = None, completed: Optional[bool] = None) -> None:
        """
        Display tasks with optional filtering by category and status.
        
        Args:
            category: Filter by category (optional)
            completed: Filter by completion status (optional)
        """
        if not self.tasks:
            self._print_info("📭 No tasks found!")
            return
        
        # Apply filters
        filtered_tasks = self.tasks
        
        if category:
            filtered_tasks = [
                t for t in filtered_tasks
                if t["category"].lower() == category.lower()
            ]
        
        if completed is not None:
            filtered_tasks = [
                t for t in filtered_tasks
                if t["completed"] == completed
            ]
        
        if not filtered_tasks:
            self._print_info("📭 No tasks match your filters!")
            return
        
        # Display table
        print("\n" + "=" * 110)
        print(f"{'ID':<4} {'Status':<12} {'Priority':<12} {'Title':<30} {'Category':<12} {'Due Date':<12}")
        print("=" * 110)
        
        for task in filtered_tasks:
            status = "✅ Done" if task["completed"] else "⭕ Pending"
            title = self._truncate(task["title"], 27)
            category_name = self._truncate(task["category"], 9)
            due_date = task.get("due_date", "") or "N/A"
            priority = task.get("priority", "MEDIUM")
            
            # Color coding for priority
            priority_display = {
                "LOW": f"{Colors.GREEN}🟢 Low{Colors.END}",
                "MEDIUM": f"{Colors.YELLOW}🟡 Medium{Colors.END}",
                "HIGH": f"{Colors.RED}🔴 High{Colors.END}"
            }.get(priority, priority)
            
            print(f"{task['id']:<4} {status:<12} {priority_display:<30} {title:<30} {category_name:<12} {due_date:<12}")
        
        print("=" * 110 + "\n")
    
    def view_task_details(self, task_id: int) -> bool:
        """
        Display comprehensive details of a specific task.
        
        Args:
            task_id: ID of the task to view
        
        Returns:
            bool: True if task found, False otherwise
        """
        try:
            task_id = int(task_id)
        except ValueError:
            self._print_error("Invalid task ID format!")
            return False
        
        task = self._find_task_by_id(task_id)
        
        if not task:
            self._print_error(f"Task with ID {task_id} not found!")
            return False
        
        status = "✅ Completed" if task["completed"] else "⭕ Pending"
        priority_emoji = {
            "LOW": "🟢",
            "MEDIUM": "🟡",
            "HIGH": "🔴"
        }.get(task.get("priority", "MEDIUM"), "")
        
        print("\n" + "=" * 70)
        print(f"{Colors.HEADER}{Colors.BOLD}📋 Task Details (ID: {task['id']}){Colors.END}")
        print("=" * 70)
        print(f"{Colors.BOLD}Title:{Colors.END}       {task['title']}")
        print(f"{Colors.BOLD}Category:{Colors.END}    {task['category']}")
        print(f"{Colors.BOLD}Status:{Colors.END}      {status}")
        print(f"{Colors.BOLD}Priority:{Colors.END}    {priority_emoji} {task.get('priority', 'N/A')}")
        print(f"{Colors.BOLD}Description:{Colors.END} {task.get('description', 'N/A')}")
        print(f"{Colors.BOLD}Due Date:{Colors.END}    {task.get('due_date', 'N/A')}")
        print(f"{Colors.BOLD}Created:{Colors.END}     {task['created_at'][:10]}")
        print(f"{Colors.BOLD}Updated:{Colors.END}     {task['updated_at'][:10]}")
        print("=" * 70 + "\n")
        
        return True
    
    def search_tasks(self, keyword: str) -> bool:
        """
        Search tasks by title, description, or category.
        
        Args:
            keyword: Search keyword
        
        Returns:
            bool: True if results found, False otherwise
        """
        if not keyword or not keyword.strip():
            self._print_error("Search keyword cannot be empty!")
            return False
        
        keyword = keyword.lower()
        filtered_tasks = [
            t for t in self.tasks
            if keyword in t["title"].lower()
            or keyword in t.get("description", "").lower()
            or keyword in t["category"].lower()
        ]
        
        if not filtered_tasks:
            self._print_info(f"🔍 No tasks found matching '{keyword}'")
            return False
        
        print(f"\n{Colors.CYAN}🔍 Search Results for '{keyword}' ({len(filtered_tasks)} found){Colors.END}")
        print("=" * 110)
        print(f"{'ID':<4} {'Status':<12} {'Priority':<12} {'Title':<30} {'Category':<12} {'Due Date':<12}")
        print("=" * 110)
        
        for task in filtered_tasks:
            status = "✅ Done" if task["completed"] else "⭕ Pending"
            title = self._truncate(task["title"], 27)
            category_name = self._truncate(task["category"], 9)
            due_date = task.get("due_date", "") or "N/A"
            priority = task.get("priority", "MEDIUM")
            
            priority_display = {
                "LOW": f"{Colors.GREEN}🟢 Low{Colors.END}",
                "MEDIUM": f"{Colors.YELLOW}🟡 Medium{Colors.END}",
                "HIGH": f"{Colors.RED}🔴 High{Colors.END}"
            }.get(priority, priority)
            
            print(f"{task['id']:<4} {status:<12} {priority_display:<30} {title:<30} {category_name:<12} {due_date:<12}")
        
        print("=" * 110 + "\n")
        return True
    
    def edit_task(
        self,
        task_id: int,
        title: Optional[str] = None,
        category: Optional[str] = None,
        description: Optional[str] = None,
        due_date: Optional[str] = None,
        priority: Optional[str] = None
    ) -> bool:
        """
        Edit an existing task with validation.
        
        Args:
            task_id: ID of task to edit
            title: New title (optional)
            category: New category (optional)
            description: New description (optional)
            due_date: New due date (optional)
            priority: New priority (optional)
        
        Returns:
            bool: True if edited successfully, False otherwise
        """
        try:
            task_id = int(task_id)
        except ValueError:
            self._print_error("Invalid task ID!")
            return False
        
        task = self._find_task_by_id(task_id)
        if not task:
            self._print_error(f"Task with ID {task_id} not found!")
            return False
        
        # Validate and update fields
        if title and title.strip():
            if len(title) > 100:
                self._print_error("Title cannot exceed 100 characters!")
                return False
            task["title"] = title.strip()
        
        if category and category.strip():
            task["category"] = category.strip()
        
        if description is not None:
            task["description"] = description.strip()
        
        if due_date is not None:
            if due_date and not self._validate_date(due_date):
                self._print_error("Invalid date format! Use YYYY-MM-DD")
                return False
            task["due_date"] = due_date
        
        if priority:
            valid_priorities = ["LOW", "MEDIUM", "HIGH"]
            if priority.upper() not in valid_priorities:
                self._print_error(f"Invalid priority! Use: {', '.join(valid_priorities)}")
                return False
            task["priority"] = priority.upper()
        
        task["updated_at"] = datetime.now().isoformat()
        
        if self.save_tasks():
            self._print_success(f"✅ Task updated: '{task['title']}'")
            return True
        
        return False
    
    def delete_task(self, task_id: int) -> bool:
        """
        Delete a task with confirmation.
        
        Args:
            task_id: ID of task to delete
        
        Returns:
            bool: True if deleted, False otherwise
        """
        try:
            task_id = int(task_id)
        except ValueError:
            self._print_error("Invalid task ID!")
            return False
        
        task = self._find_task_by_id(task_id)
        if not task:
            self._print_error(f"Task with ID {task_id} not found!")
            return False
        
        # Get confirmation
        print(f"\n{Colors.YELLOW}{Colors.BOLD}⚠️  Confirm deletion:{Colors.END}")
        print(f"Title: {task['title']}")
        print(f"Category: {task['category']}\n")
        
        confirm = input(f"{Colors.RED}Are you sure you want to delete this task? (yes/no): {Colors.END}").strip().lower()
        
        if confirm != "yes":
            self._print_info("❌ Deletion cancelled")
            return False
        
        self.tasks.remove(task)
        
        if self.save_tasks():
            self._print_success(f"✅ Task deleted: '{task['title']}'")
            return True
        
        self.tasks.append(task)
        return False
    
    def mark_complete(self, task_id: int) -> bool:
        """
        Toggle task completion status.
        
        Args:
            task_id: ID of task to toggle
        
        Returns:
            bool: True if updated, False otherwise
        """
        try:
            task_id = int(task_id)
        except ValueError:
            self._print_error("Invalid task ID!")
            return False
        
        task = self._find_task_by_id(task_id)
        if not task:
            self._print_error(f"Task with ID {task_id} not found!")
            return False
        
        task["completed"] = not task["completed"]
        task["updated_at"] = datetime.now().isoformat()
        status = "✅ Completed" if task["completed"] else "⭕ Incomplete"
        
        if self.save_tasks():
            self._print_success(f"Task marked as {status}: '{task['title']}'")
            return True
        
        return False
    
    def get_categories(self) -> set:
        """Get all unique categories"""
        return set(task["category"] for task in self.tasks)
    
    def show_stats(self) -> None:
        """Display comprehensive task statistics"""
        if not self.tasks:
            self._print_info("📭 No tasks to display stats!")
            return
        
        total = len(self.tasks)
        completed = sum(1 for t in self.tasks if t["completed"])
        pending = total - completed
        
        # Priority breakdown
        priority_counts = {
            "LOW": sum(1 for t in self.tasks if t.get("priority") == "LOW"),
            "MEDIUM": sum(1 for t in self.tasks if t.get("priority") == "MEDIUM"),
            "HIGH": sum(1 for t in self.tasks if t.get("priority") == "HIGH")
        }
        
        # Category breakdown
        categories = self.get_categories()
        category_stats = {}
        for cat in categories:
            cat_tasks = [t for t in self.tasks if t["category"] == cat]
            cat_completed = sum(1 for t in cat_tasks if t["completed"])
            category_stats[cat] = (len(cat_tasks), cat_completed)
        
        # Overdue tasks
        today = datetime.now().date()
        overdue = sum(
            1 for t in self.tasks
            if t.get("due_date") and not t["completed"]
            and datetime.strptime(t["due_date"], "%Y-%m-%d").date() < today
        )
        
        # Display stats
        print("\n" + "=" * 70)
        print(f"{Colors.HEADER}{Colors.BOLD}📊 Task Statistics{Colors.END}")
        print("=" * 70)
        
        print(f"\n{Colors.BOLD}Overall:{Colors.END}")
        print(f"  Total Tasks: {total}")
        print(f"  ✅ Completed: {completed}")
        print(f"  ⭕ Pending: {pending}")
        print(f"  📈 Progress: {(completed/total*100):.1f}%")
        
        if overdue > 0:
            print(f"  ⚠️  Overdue: {Colors.RED}{overdue}{Colors.END}")
        
        print(f"\n{Colors.BOLD}By Priority:{Colors.END}")
        print(f"  🟢 Low: {priority_counts['LOW']}")
        print(f"  🟡 Medium: {priority_counts['MEDIUM']}")
        print(f"  🔴 High: {priority_counts['HIGH']}")
        
        print(f"\n{Colors.BOLD}By Category:{Colors.END}")
        for cat in sorted(categories):
            cat_total, cat_completed = category_stats[cat]
            percentage = (cat_completed / cat_total * 100) if cat_total > 0 else 0
            print(f"  {cat}: {cat_completed}/{cat_total} ({percentage:.0f}%)")
        
        print("=" * 70 + "\n")
    
    # ========== Helper Methods ==========
    
    def _find_task_by_id(self, task_id: int) -> Optional[Dict]:
        """Find task by ID"""
        return next((t for t in self.tasks if t["id"] == task_id), None)
    
    def _validate_date(self, date_str: str) -> bool:
        """Validate date format YYYY-MM-DD"""
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
            return True
        except ValueError:
            return False
    
    @staticmethod
    def _truncate(text: str, length: int) -> str:
        """Truncate text with ellipsis"""
        return text[:length] + "..." if len(text) > length else text
    
    @staticmethod
    def _print_success(message: str) -> None:
        """Print success message"""
        print(f"{Colors.GREEN}✅ {message}{Colors.END}")
    
    @staticmethod
    def _print_error(message: str) -> None:
        """Print error message"""
        print(f"{Colors.RED}❌ {message}{Colors.END}")
    
    @staticmethod
    def _print_info(message: str) -> None:
        """Print info message"""
        print(f"{Colors.CYAN}ℹ️  {message}{Colors.END}")


def display_logo():
    """Display the professional logo"""
    logo = f"""
    {Colors.CYAN}{Colors.BOLD}
    ╔══════════════════════════════════════════════════════════════════════════════╗
    ║                                                                              ║
    ║           ███████╗███╗   ███╗ █████╗ ██████╗ ████████╗                      ║
    ║           ██╔════╝████╗ ████║██╔══██╗██╔══██╗╚══██╔══╝                      ║
    ║           ███████╗██╔████╔██║███████║██████╔╝   ██║                         ║
    ║           ╚════██║██║╚██╔╝██║██╔══██║██╔══██╗   ██║                         ║
    ║           ███████║██║ ╚═╝ ██║██║  ██║██║  ██║   ██║                         ║
    ║           ╚══════╝╚═╝     ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝                         ║
    ║                                                                              ║
    ║                    🎯 T A S K   M A N A G E R 🎯                            ║
    ║                        Professional Edition v3.0                            ║
    ║                                                                              ║
    ║        ✨ Organize • Track • Achieve • Succeed ✨                          ║
    ║                                                                              ║
    ║                    Created by: Maheen Affan                                 ║
    ║                                                                              ║
    ╚══════════════════════════════════════════════════════════════════════════════╝
    {Colors.END}
    """
    print(logo)


def show_menu():
    """Display the main menu"""
    menu = f"""
    {Colors.HEADER}{Colors.BOLD}🎯 Smart Task Manager - Main Menu{Colors.END}
    {Colors.BOLD}{'='*70}{Colors.END}
    
    {Colors.BLUE}📝 Task Management:{Colors.END}
      [1] add       - Add a new task
      [2] view      - View all tasks
      [3] search    - Search tasks by keyword
      [4] filter    - Filter by category/status
      [5] details   - View task details
      [6] edit      - Edit existing task
      [7] complete  - Mark task as complete/incomplete
      [8] delete    - Delete a task
    
    {Colors.BLUE}📊 Statistics & Help:{Colors.END}
      [9] stats     - Show task statistics
      [10] help     - Show this menu
      [0] exit      - Exit the application
    
    {Colors.BOLD}{'='*70}{Colors.END}
    """
    print(menu)


def main():
    """Main application loop"""
    display_logo()
    manager = TaskManager()
    
    print(f"{Colors.GREEN}{Colors.BOLD}👋 Hello Maheen! Welcome to Smart Task Manager!{Colors.END}")
    print(f"{Colors.CYAN}Type 'help' or '10' to see all available commands.{Colors.END}\n")
    
    while True:
        try:
            action = input(f"{Colors.BOLD}Enter command (or 'help'): {Colors.END}").strip().lower()
            
            if action in ["1", "add"]:
                print(f"\n{Colors.BOLD}➕ Add New Task{Colors.END}")
                title = input("Task title: ").strip()
                if not title:
                    print(f"{Colors.RED}❌ Title cannot be empty!{Colors.END}")
                    continue
                
                print("Categories: General, Work, Personal, Shopping, Health, Education, Other")
                category = input("Category (press Enter for 'General'): ").strip() or "General"
                description = input("Description (optional): ").strip()
                
                print("Priority: LOW, MEDIUM, HIGH (press Enter for 'MEDIUM')")
                priority = input("Priority: ").strip().upper() or "MEDIUM"
                
                due_date = input("Due date YYYY-MM-DD (optional): ").strip()
                
                manager.add_task(title, category, description, due_date, priority)
            
            elif action in ["2", "view"]:
                print(f"\n{Colors.BOLD}📋 View Tasks{Colors.END}")
                category_filter = input("Filter by category (press Enter to skip): ").strip()
                
                print("View: [a]ll, [p]ending, [c]ompleted (press Enter for all)")
                status_input = input("Status filter: ").strip().lower()
                
                status_filter = None
                if status_input == "p":
                    status_filter = False
                elif status_input == "c":
                    status_filter = True
                
                manager.view_tasks(
                    category=category_filter if category_filter else None,
                    completed=status_filter
                )
            
            elif action in ["3", "search"]:
                keyword = input(f"\n{Colors.BOLD}🔍 Search keyword: {Colors.END}").strip()
                manager.search_tasks(keyword)
            
            elif action in ["4", "filter"]:
                print(f"\n{Colors.BOLD}🔗 Filter Tasks{Colors.END}")
                categories = manager.get_categories()
                if categories:
                    print(f"Available categories: {', '.join(sorted(categories))}")
                    category = input("Enter category: ").strip()
                    manager.view_tasks(category=category)
                else:
                    print(f"{Colors.RED}❌ No categories found!{Colors.END}")
            
            elif action in ["5", "details"]:
                manager.view_tasks()
                task_id = input(f"\n{Colors.BOLD}Enter task ID to view details: {Colors.END}").strip()
                manager.view_task_details(task_id)
            
            elif action in ["6", "edit"]:
                print(f"\n{Colors.BOLD}✏️  Edit Task{Colors.END}")
                manager.view_tasks()
                task_id = input("Enter task ID to edit: ").strip()
                
                try:
                    task_id_int = int(task_id)
                    task = manager._find_task_by_id(task_id_int)
                    
                    if not task:
                        print(f"{Colors.RED}❌ Task not found!{Colors.END}")
                        continue
                    
                    print(f"\nEditing: {task['title']}")
                    print("(Press Enter to keep current value)\n")
                    
                    new_title = input(f"New title [{task['title']}]: ").strip()
                    new_category = input(f"New category [{task['category']}]: ").strip()
                    new_description = input(f"New description [{task.get('description', '')}]: ").strip()
                    new_priority = input(f"New priority [{task.get('priority', 'MEDIUM')}]: ").strip()
                    new_due_date = input(f"New due date [{task.get('due_date', 'N/A')}]: ").strip()
                    
                    manager.edit_task(
                        task_id,
                        title=new_title if new_title else None,
                        category=new_category if new_category else None,
                        description=new_description if new_description else None,
                        priority=new_priority if new_priority else None,
                        due_date=new_due_date if new_due_date else None
                    )
                except ValueError:
                    print(f"{Colors.RED}❌ Invalid task ID!{Colors.END}")
            
            elif action in ["7", "complete"]:
                manager.view_tasks()
                task_id = input(f"\n{Colors.BOLD}Enter task ID to toggle: {Colors.END}").strip()
                manager.mark_complete(task_id)
            
            elif action in ["8", "delete"]:
                manager.view_tasks()
                task_id = input(f"\n{Colors.BOLD}Enter task ID to delete: {Colors.END}").strip()
                manager.delete_task(task_id)
            
            elif action in ["9", "stats"]:
                manager.show_stats()
            
            elif action in ["10", "help"]:
                show_menu()
            
            elif action in ["0", "exit"]:
                print(f"\n{Colors.GREEN}{Colors.BOLD}👋 Goodbye Maheen! Keep achieving your goals! 🎯{Colors.END}\n")
                break
            
            else:
                print(f"{Colors.YELLOW}⚠️  Invalid command! Type 'help' or '10' to see available commands.{Colors.END}")
        
        except KeyboardInterrupt:
            print(f"\n\n{Colors.YELLOW}⚠️  Application interrupted. Goodbye!{Colors.END}\n")
            break
        except Exception as e:
            print(f"{Colors.RED}❌ Unexpected error: {e}{Colors.END}")


if __name__ == "__main__":
    main()
