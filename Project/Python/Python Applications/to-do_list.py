import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import json
import os
from datetime import datetime

class TodoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("To-Do List App")
        self.root.geometry("700x500")
        self.root.minsize(600, 400)
        
        # Set default save file path
        self.save_file = "todo_tasks.json"
        
        # List to store tasks
        self.tasks = []
        
        # Create main frame
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create styles
        self.style = ttk.Style()
        self.style.configure("TFrame", background="#f5f5f5")
        self.style.configure("Header.TLabel", font=("Arial", 16, "bold"), background="#f5f5f5")
        self.style.configure("Task.TFrame", background="white", relief="solid", borderwidth=1)
        self.style.configure("Complete.Task.TFrame", background="#e8f5e9")
        self.style.configure("Task.TCheckbutton", background="white")
        self.style.configure("Complete.Task.TCheckbutton", background="#e8f5e9")
        self.style.configure("Task.TLabel", background="white")
        self.style.configure("Complete.Task.TLabel", background="#e8f5e9", foreground="#757575")
        
        # Create header
        self.header_frame = ttk.Frame(self.main_frame, style="TFrame")
        self.header_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.header_label = ttk.Label(self.header_frame, text="To-Do List", style="Header.TLabel")
        self.header_label.pack(side=tk.LEFT, pady=5)
        
        # Create task input frame
        self.input_frame = ttk.Frame(self.main_frame, style="TFrame")
        self.input_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.task_entry = ttk.Entry(self.input_frame, font=("Arial", 12), width=40)
        self.task_entry.pack(side=tk.LEFT, padx=(0, 5), fill=tk.X, expand=True)
        self.task_entry.bind("<Return>", lambda e: self.add_task())
        
        # Create the due date frame
        self.date_frame = ttk.Frame(self.input_frame, style="TFrame")
        self.date_frame.pack(side=tk.LEFT, padx=(0, 5))
        
        # Due date selector
        self.due_date_var = tk.StringVar()
        self.due_date_var.set("No Due Date")
        
        self.due_date_button = ttk.Button(
            self.date_frame, 
            textvariable=self.due_date_var, 
            command=self.set_due_date, 
            width=15
        )
        self.due_date_button.pack(side=tk.LEFT)
        
        # Priority selector
        self.priority_var = tk.StringVar()
        self.priority_var.set("Normal")
        
        self.priority_option = ttk.Combobox(
            self.input_frame, 
            textvariable=self.priority_var, 
            values=["Low", "Normal", "High"], 
            state="readonly", 
            width=10
        )
        self.priority_option.pack(side=tk.LEFT, padx=(0, 5))
        
        # Add task button
        self.add_button = ttk.Button(
            self.input_frame, 
            text="Add Task", 
            command=self.add_task,
            style="Accent.TButton"
        )
        self.add_button.pack(side=tk.LEFT)
        
        # Try to create a custom accent style for the add button
        try:
            self.style.configure("Accent.TButton", background="#4caf50", foreground="white")
            self.style.map("Accent.TButton", 
                         background=[("active", "#66bb6a"), ("pressed", "#43a047")],
                         foreground=[("active", "white"), ("pressed", "white")])
        except:
            # If the style configuration fails, we just use the default style
            pass
        
        # Create scrollable frame for tasks
        self.canvas = tk.Canvas(self.main_frame, background="#f5f5f5", highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self.main_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.tasks_frame = ttk.Frame(self.canvas, style="TFrame")
        self.canvas_frame = self.canvas.create_window((0, 0), window=self.tasks_frame, anchor=tk.NW)
        
        # Configure canvas scrolling
        self.tasks_frame.bind("<Configure>", self.on_frame_configure)
        self.canvas.bind("<Configure>", self.on_canvas_configure)
        self.canvas.bind_all("<MouseWheel>", self.on_mousewheel)
        
        # Create bottom button frame
        self.button_frame = ttk.Frame(self.main_frame, style="TFrame")
        self.button_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Clear completed button
        self.clear_button = ttk.Button(
            self.button_frame, 
            text="Clear Completed", 
            command=self.clear_completed
        )
        self.clear_button.pack(side=tk.LEFT, padx=(0, 5))
        
        # Delete all button
        self.delete_all_button = ttk.Button(
            self.button_frame, 
            text="Delete All", 
            command=self.delete_all
        )
        self.delete_all_button.pack(side=tk.LEFT, padx=(0, 5))
        
        # Statistics label
        self.stats_label = ttk.Label(
            self.button_frame, 
            text="Tasks: 0 | Completed: 0",
            style="Task.TLabel"
        )
        self.stats_label.pack(side=tk.RIGHT)
        
        # Create context menu for tasks
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="Edit", command=self.edit_selected_task)
        self.context_menu.add_command(label="Delete", command=self.delete_selected_task)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Change Due Date", command=self.change_selected_due_date)
        self.context_menu.add_command(label="Set Priority", command=self.change_selected_priority)
        
        # Selected task reference
        self.selected_task_frame = None
        self.task_frames = []
        
        # Load saved tasks
        self.load_tasks()
        
        # Bind app close event
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
    
    def on_frame_configure(self, event):
        """Reset the scroll region to encompass the inner frame"""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
    
    def on_canvas_configure(self, event):
        """When the canvas is resized, resize the inner frame to match"""
        self.canvas.itemconfig(self.canvas_frame, width=event.width)
    
    def on_mousewheel(self, event):
        """Scroll the canvas with the mousewheel"""
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    
    def set_due_date(self):
        """Open a dialog to set a due date"""
        current_date = self.due_date_var.get()
        if current_date == "No Due Date":
            current_date = datetime.now().strftime("%Y-%m-%d")
            
        result = simpledialog.askstring(
            "Set Due Date",
            "Enter due date (YYYY-MM-DD):",
            initialvalue=current_date
        )
        
        if result:
            try:
                # Validate date format
                datetime.strptime(result, "%Y-%m-%d")
                self.due_date_var.set(result)
            except ValueError:
                messagebox.showerror("Error", "Invalid date format. Use YYYY-MM-DD.")
                self.set_due_date()  # Try again
        else:
            # User cancelled, set to "No Due Date"
            self.due_date_var.set("No Due Date")
    
    def add_task(self):
        """Add a new task to the list"""
        task_text = self.task_entry.get().strip()
        if not task_text:
            return
        
        # Create a new task
        task = {
            "text": task_text,
            "completed": False,
            "created": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "due_date": self.due_date_var.get() if self.due_date_var.get() != "No Due Date" else None,
            "priority": self.priority_var.get()
        }
        
        # Add to tasks list
        self.tasks.append(task)
        
        # Add task to UI
        self.create_task_frame(task, len(self.tasks) - 1)
        
        # Clear entry and reset defaults
        self.task_entry.delete(0, tk.END)
        self.due_date_var.set("No Due Date")
        self.priority_var.set("Normal")
        
        # Update statistics
        self.update_statistics()
    
    def create_task_frame(self, task, index):
        """Create a frame for a task and add it to the UI"""
        frame_style = "Complete.Task.TFrame" if task["completed"] else "Task.TFrame"
        task_frame = ttk.Frame(self.tasks_frame, style=frame_style, padding=5)
        task_frame.pack(fill=tk.X, pady=2, padx=5)
        task_frame.index = index  # Store the task index
        
        # Checkbox for completion status
        checkbox_style = "Complete.Task.TCheckbutton" if task["completed"] else "Task.TCheckbutton"
        check_var = tk.BooleanVar(value=task["completed"])
        checkbox = ttk.Checkbutton(
            task_frame, 
            variable=check_var,
            style=checkbox_style,
            command=lambda idx=index, var=check_var: self.toggle_task(idx, var)
        )
        checkbox.pack(side=tk.LEFT)
        
        # Task content
        label_style = "Complete.Task.TLabel" if task["completed"] else "Task.TLabel"
        
        # Format task text based on priority
        task_text = task["text"]
        if task["priority"] == "High":
            task_text = f"[HIGH] {task_text}"
        elif task["priority"] == "Low":
            task_text = f"[LOW] {task_text}"
        
        # Add due date if exists
        if task["due_date"]:
            task_text = f"{task_text} (Due: {task['due_date']})"
        
        task_label = ttk.Label(
            task_frame, 
            text=task_text,
            style=label_style
        )
        task_label.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # If completed, strike-through the text
        if task["completed"]:
            task_label.configure(font=("TkDefaultFont", 10, "overstrike"))
        
        # Bind events for context menu
        for widget in [task_frame, task_label, checkbox]:
            widget.bind("<Button-3>", lambda e, tf=task_frame: self.show_context_menu(e, tf))
            widget.bind("<Button-1>", lambda e, tf=task_frame: self.select_task(tf))
        
        # Add to task frames list
        self.task_frames.append(task_frame)
        
        return task_frame
    
    def select_task(self, task_frame):
        """Select a task and highlight it"""
        # Deselect current selection if exists
        if self.selected_task_frame:
            self.selected_task_frame.configure(relief="solid")
        
        # Select the new task
        self.selected_task_frame = task_frame
        task_frame.configure(relief="raised")
    
    def show_context_menu(self, event, task_frame):
        """Show the context menu for a task"""
        self.select_task(task_frame)
        self.context_menu.tk_popup(event.x_root, event.y_root)
    
    def toggle_task(self, index, var):
        """Toggle the completion status of a task"""
        # Update task data
        self.tasks[index]["completed"] = var.get()
        
        # Update UI
        frame = self.task_frames[index]
        label = frame.winfo_children()[1]  # The label is the second child
        
        if var.get():  # Task completed
            frame.configure(style="Complete.Task.TFrame")
            frame.winfo_children()[0].configure(style="Complete.Task.TCheckbutton")
            label.configure(style="Complete.Task.TLabel", font=("TkDefaultFont", 10, "overstrike"))
        else:  # Task not completed
            frame.configure(style="Task.TFrame")
            frame.winfo_children()[0].configure(style="Task.TCheckbutton")
            label.configure(style="Task.TLabel", font=("TkDefaultFont", 10))
        
        # Update statistics
        self.update_statistics()
    
    def edit_selected_task(self):
        """Edit the selected task"""
        if not self.selected_task_frame:
            return
        
        index = self.selected_task_frame.index
        task = self.tasks[index]
        
        # Show dialog to edit task
        new_text = simpledialog.askstring(
            "Edit Task", 
            "Task text:", 
            initialvalue=task["text"]
        )
        
        if new_text and new_text.strip():
            # Update task data
            task["text"] = new_text.strip()
            
            # Update UI
            self.refresh_tasks()
    
    def delete_selected_task(self):
        """Delete the selected task"""
        if not self.selected_task_frame:
            return
        
        index = self.selected_task_frame.index
        
        # Remove task from data
        self.tasks.pop(index)
        
        # Reset selected task
        self.selected_task_frame = None
        
        # Update UI
        self.refresh_tasks()
    
    def change_selected_due_date(self):
        """Change the due date of the selected task"""
        if not self.selected_task_frame:
            return
        
        index = self.selected_task_frame.index
        task = self.tasks[index]
        
        # Get current due date
        current_date = task["due_date"] if task["due_date"] else "No Due Date"
        if current_date == "No Due Date":
            current_date = datetime.now().strftime("%Y-%m-%d")
        
        # Show dialog to set new due date
        result = simpledialog.askstring(
            "Change Due Date",
            "Enter due date (YYYY-MM-DD):",
            initialvalue=current_date
        )
        
        if result:
            try:
                # Validate date format
                datetime.strptime(result, "%Y-%m-%d")
                task["due_date"] = result
            except ValueError:
                messagebox.showerror("Error", "Invalid date format. Use YYYY-MM-DD.")
                return
        else:
            # User cancelled, set to None
            task["due_date"] = None
        
        # Update UI
        self.refresh_tasks()
    
    def change_selected_priority(self):
        """Change the priority of the selected task"""
        if not self.selected_task_frame:
            return
        
        index = self.selected_task_frame.index
        task = self.tasks[index]
        
        # Show dialog to set new priority
        new_priority = simpledialog.askstring(
            "Set Priority",
            "Enter priority (Low, Normal, High):",
            initialvalue=task["priority"]
        )
        
        if new_priority and new_priority in ["Low", "Normal", "High"]:
            task["priority"] = new_priority
            self.refresh_tasks()
    
    def clear_completed(self):
        """Remove all completed tasks"""
        if not any(task["completed"] for task in self.tasks):
            return
        
        confirm = messagebox.askyesno(
            "Confirm", 
            "Are you sure you want to remove all completed tasks?"
        )
        
        if confirm:
            # Remove completed tasks
            self.tasks = [task for task in self.tasks if not task["completed"]]
            
            # Reset selected task
            self.selected_task_frame = None
            
            # Update UI
            self.refresh_tasks()
    
    def delete_all(self):
        """Delete all tasks"""
        if not self.tasks:
            return
        
        confirm = messagebox.askyesno(
            "Confirm", 
            "Are you sure you want to delete all tasks?"
        )
        
        if confirm:
            # Clear tasks list
            self.tasks = []
            
            # Reset selected task
            self.selected_task_frame = None
            
            # Update UI
            self.refresh_tasks()
    
    def refresh_tasks(self):
        """Refresh the tasks display"""
        # Clear existing task frames
        for frame in self.task_frames:
            frame.destroy()
        
        self.task_frames = []
        
        # Recreate all task frames
        for i, task in enumerate(self.tasks):
            self.create_task_frame(task, i)
        
        # Update statistics
        self.update_statistics()
    
    def update_statistics(self):
        """Update statistics display"""
        total = len(self.tasks)
        completed = sum(1 for task in self.tasks if task["completed"])
        
        self.stats_label.configure(text=f"Tasks: {total} | Completed: {completed}")
    
    def save_tasks(self):
        """Save tasks to file"""
        try:
            with open(self.save_file, 'w') as f:
                json.dump(self.tasks, f)
        except Exception as e:
            messagebox.showerror("Error", f"Could not save tasks: {e}")
    
    def load_tasks(self):
        """Load tasks from file"""
        if not os.path.exists(self.save_file):
            return
        
        try:
            with open(self.save_file, 'r') as f:
                self.tasks = json.load(f)
            
            # Rebuild the UI with loaded tasks
            self.refresh_tasks()
        except Exception as e:
            messagebox.showerror("Error", f"Could not load tasks: {e}")
    
    def on_close(self):
        """Handle application close"""
        self.save_tasks()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = TodoApp(root)
    root.mainloop()