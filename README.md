# Smart-task-mangerdef save_tasks(tasks):
    with open("tasks.txt", "w") as file:
        for task in tasks:
            file.write(task + "\n")

def load_tasks():
    try:
        with open("tasks.txt", "r") as file:
            return [line.strip() for line in file.readlines()]
    except FileNotFoundError:
        return []

tasks = load_tasks()

print("Hello Marleen! I am your AI Assistant. How can I help you today?")
while True:
    action = input("\nCommands: [add/view/exit]: ").lower()

    if action == "add":
        new_task = input("Enter your task: ")
        tasks.append(new_task)
        save_tasks(tasks)
        print("Task added!")
    elif action == "view":
        print("\nYour Tasks:")
        for i, task in enumerate(tasks, 1):
            print(f"{i}. {task}")
    elif action == "exit":
        print("Goodbye Marleen! Good luck with your goals.")
        break
    else:
        print("Invalid command.")
