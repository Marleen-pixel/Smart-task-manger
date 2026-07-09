# Smart Task Manager 🎯

A feature-rich Python CLI task manager with categories, error handling, and persistent storage.

## Features ✨

- **Add Tasks** - Create tasks with custom categories
- **View Tasks** - Display all tasks in a formatted table
- **Filter by Category** - View tasks for specific categories
- **Mark Complete** - Toggle task completion status
- **Delete Tasks** - Remove tasks you no longer need
- **Task Statistics** - View progress and completion stats
- **Persistent Storage** - Tasks saved to JSON file automatically
- **Error Handling** - Robust validation and error messages
- **User-Friendly UI** - Clear menus and emoji indicators

## Installation 📦

1. Clone the repository:
```bash
git clone https://github.com/Marleen-pixel/Smart-task-manger.git
cd Smart-task-manger
```

2. Ensure Python 3.6+ is installed:
```bash
python --version
```

## Usage 🚀

Run the application:
```bash
python task_manager.py
```

### Available Commands

| Command | Description |
|---------|-------------|
| `add` | Add a new task with optional category |
| `view` | Display all tasks |
| `filter` | Filter tasks by category |
| `complete` | Mark a task as complete/incomplete |
| `delete` | Delete a task |
| `stats` | Show task statistics |
| `help` | Display help menu |
| `exit` | Exit the application |

### Example Session

```
👋 Hello Marleen! Welcome to Smart Task Manager!
Type 'help' to see all available commands.

Enter command: add
Enter task title: Buy groceries
Enter category (or press Enter for 'General'): Shopping
✅ Task added: 'Buy groceries' in category 'Shopping'

Enter command: view
======================================================================
ID   Status   Task                             Category       
======================================================================
1    ⭕       Buy groceries                    Shopping       
======================================================================

Enter command: complete
Enter task ID to mark complete/incomplete: 1
✅ Task marked as completed: 'Buy groceries'

Enter command: stats
========================================
📊 Task Statistics
========================================
Total Tasks: 1
Completed: 1 ✅
Pending: 0 ⭕
Progress: 100.0%
========================================
```

## File Format 📄

Tasks are stored in `tasks.json` with the following structure:

```json
[
  {
    "id": 1,
    "title": "Buy groceries",
    "category": "Shopping",
    "completed": true,
    "created_at": "2026-07-09 11:46:57"
  }
]
```

## Features in Detail 🔍

### Error Handling
- Validates empty task titles
- Handles file read/write errors
- Detects corrupted JSON files
- Graceful error messages with guidance

### Categories
- Organize tasks into categories
- Default category: "General"
- Filter tasks by category
- View all available categories

### Data Persistence
- Automatic saving after each change
- JSON format for easy backup
- Recovery from file errors

## Improvements Over Original Version 🎨

✅ **Object-Oriented Design** - Clean TaskManager class  
✅ **Error Handling** - Try-catch blocks for file operations  
✅ **Categories Support** - Organize tasks by category  
✅ **Better UI** - Formatted tables and emoji indicators  
✅ **Task Statistics** - Progress tracking  
✅ **Input Validation** - Prevents invalid data entry  
✅ **Type Hints** - Better code documentation  
✅ **Extended Commands** - More functionality  

## Future Enhancements 🚀

- [ ] Due dates for tasks
- [ ] Task priorities (High, Medium, Low)
- [ ] Search functionality
- [ ] Export to CSV/PDF
- [ ] Recurring tasks
- [ ] Task reminders/notifications

## License 📝

Free to use and modify!

## Author 👨‍💻

Created by **Marleen Affan**

---

**Happy task managing!** 📝✨
