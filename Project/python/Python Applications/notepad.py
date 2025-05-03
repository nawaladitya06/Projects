import tkinter as tk
from tkinter import ttk
from tkinter import filedialog, messagebox, font
import os

class SimpleNotepad:
    def __init__(self, root):
        self.root = root
        self.root.title("Simple Notepad")
        self.root.geometry("800x600")
        
        # Set the file path to None initially (no file opened yet)
        self.file_path = None
        
        # Create the main menu
        self.menu_bar = tk.Menu(root)
        self.root.config(menu=self.menu_bar)
        
        # File Menu
        self.file_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="File", menu=self.file_menu)
        self.file_menu.add_command(label="New", command=self.new_file, accelerator="Ctrl+N")
        self.file_menu.add_command(label="Open", command=self.open_file, accelerator="Ctrl+O")
        self.file_menu.add_command(label="Save", command=self.save_file, accelerator="Ctrl+S")
        self.file_menu.add_command(label="Save As", command=self.save_as_file)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit", command=self.exit_app)
        
        # Edit Menu
        self.edit_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Edit", menu=self.edit_menu)
        self.edit_menu.add_command(label="Cut", command=self.cut_text, accelerator="Ctrl+X")
        self.edit_menu.add_command(label="Copy", command=self.copy_text, accelerator="Ctrl+C")
        self.edit_menu.add_command(label="Paste", command=self.paste_text, accelerator="Ctrl+V")
        self.edit_menu.add_separator()
        self.edit_menu.add_command(label="Undo", command=self.undo_text, accelerator="Ctrl+Z")
        self.edit_menu.add_command(label="Redo", command=self.redo_text, accelerator="Ctrl+Y")
        
        # Format Menu
        self.format_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Format", menu=self.format_menu)
        
        # Font submenu
        self.font_menu = tk.Menu(self.format_menu, tearoff=0)
        self.format_menu.add_cascade(label="Font", menu=self.font_menu)
        
        # Add some common fonts
        self.font_family = tk.StringVar()
        self.font_size = tk.IntVar()
        self.font_size.set(12)  # Default font size
        
        # Available fonts
        fonts = ["Arial", "Times New Roman", "Courier New", "Calibri", "Verdana"]
        for f in fonts:
            self.font_menu.add_radiobutton(label=f, variable=self.font_family, value=f, command=self.change_font)
        
        # Font size submenu
        self.size_menu = tk.Menu(self.format_menu, tearoff=0)
        self.format_menu.add_cascade(label="Font Size", menu=self.size_menu)
        
        # Add various font sizes
        sizes = [8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32]
        for s in sizes:
            self.size_menu.add_radiobutton(label=str(s), variable=self.font_size, value=s, command=self.change_font)
        
        # Help Menu
        self.help_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Help", menu=self.help_menu)
        self.help_menu.add_command(label="About", command=self.show_about)
        
        # Create a Frame for the status bar and line numbers
        self.status_frame = tk.Frame(root, height=25)
        self.status_frame.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Status Bar
        self.status_bar = tk.Label(self.status_frame, text="Ready", anchor=tk.W, padx=5)
        self.status_bar.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Line and column counter
        self.line_column_display = tk.Label(self.status_frame, text="Ln 1, Col 1", padx=5)
        self.line_column_display.pack(side=tk.RIGHT)
        
        # Create the main text area with a scrollbar
        self.text_frame = tk.Frame(root)
        self.text_frame.pack(fill=tk.BOTH, expand=True)
        
        # Add a vertical scrollbar
        self.text_scroll_y = tk.Scrollbar(self.text_frame)
        self.text_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Add a horizontal scrollbar
        self.text_scroll_x = tk.Scrollbar(self.text_frame, orient=tk.HORIZONTAL)
        self.text_scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Create the text widget
        self.text_area = tk.Text(self.text_frame, undo=True, wrap=tk.NONE, 
                              yscrollcommand=self.text_scroll_y.set,
                              xscrollcommand=self.text_scroll_x.set)
        self.text_area.pack(fill=tk.BOTH, expand=True)
        
        # Configure the scrollbars
        self.text_scroll_y.config(command=self.text_area.yview)
        self.text_scroll_x.config(command=self.text_area.xview)
        
        # Set up the default font
        self.font_family.set("Arial")
        self.change_font()
        
        # Bind keyboard shortcuts
        self.root.bind("<Control-n>", lambda event: self.new_file())
        self.root.bind("<Control-o>", lambda event: self.open_file())
        self.root.bind("<Control-s>", lambda event: self.save_file())
        self.text_area.bind("<KeyRelease>", self.update_line_column)
        self.text_area.bind("<Button-1>", self.update_line_column)
        
        # Bind text changes to update the modified indicator
        self.text_area.bind("<<Modified>>", self.on_text_modified)
        
        # Initialize the application state
        self.is_modified = False
        self.update_title()

    def change_font(self):
        """Change the font of the text area"""
        font_family = self.font_family.get()
        font_size = self.font_size.get()
        self.text_area.configure(font=(font_family, font_size))
    
    def new_file(self):
        """Create a new file"""
        # Check if current content needs to be saved
        if self.is_modified:
            response = messagebox.askyesnocancel("Unsaved Changes", 
                                               "Do you want to save changes to the current file?")
            if response is None:  # Cancel was pressed
                return
            elif response:  # Yes was pressed
                if not self.save_file():
                    return  # If save was cancelled, don't create new file
                
        # Clear the text area and reset file state
        self.text_area.delete(1.0, tk.END)
        self.file_path = None
        self.is_modified = False
        self.update_title()
        self.status_bar.config(text="New File")
    
    def open_file(self):
        """Open a file and load its contents"""
        # Check if current content needs to be saved
        if self.is_modified:
            response = messagebox.askyesnocancel("Unsaved Changes", 
                                               "Do you want to save changes to the current file?")
            if response is None:  # Cancel was pressed
                return
            elif response:  # Yes was pressed
                if not self.save_file():
                    return  # If save was cancelled, don't open new file
        
        # Open a file dialog to select a file
        file_path = filedialog.askopenfilename(
            filetypes=[("Text Files", "*.txt"), 
                       ("Python Files", "*.py"), 
                       ("All Files", "*.*")]
        )
        
        if file_path:
            try:
                # Read file contents
                with open(file_path, 'r') as file:
                    file_contents = file.read()
                
                # Update text area with file contents
                self.text_area.delete(1.0, tk.END)
                self.text_area.insert(1.0, file_contents)
                
                # Update file state
                self.file_path = file_path
                self.is_modified = False
                self.update_title()
                
                # Update status bar
                file_name = os.path.basename(file_path)
                self.status_bar.config(text=f"Opened: {file_name}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Could not open file: {e}")
    
    def save_file(self):
        """Save the current file"""
        if self.file_path:
            try:
                # Get text content
                text_content = self.text_area.get(1.0, tk.END)
                
                # Write to file
                with open(self.file_path, 'w') as file:
                    file.write(text_content)
                
                # Update file state
                self.is_modified = False
                self.update_title()
                
                # Update status bar
                file_name = os.path.basename(self.file_path)
                self.status_bar.config(text=f"Saved: {file_name}")
                return True
                
            except Exception as e:
                messagebox.showerror("Error", f"Could not save file: {e}")
                return False
        else:
            # If no file path exists, use Save As instead
            return self.save_as_file()
    
    def save_as_file(self):
        """Save the current file with a new name"""
        # Open a file dialog to select a save location
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text Files", "*.txt"), 
                       ("Python Files", "*.py"), 
                       ("All Files", "*.*")]
        )
        
        if file_path:
            # Update file path and save
            self.file_path = file_path
            return self.save_file()
        return False
    
    def exit_app(self):
        """Exit the application"""
        # Check if current content needs to be saved
        if self.is_modified:
            response = messagebox.askyesnocancel("Unsaved Changes", 
                                               "Do you want to save changes before exiting?")
            if response is None:  # Cancel was pressed
                return
            elif response:  # Yes was pressed
                if not self.save_file():
                    return  # If save was cancelled, don't exit
        
        self.root.destroy()
    
    def cut_text(self):
        """Cut selected text"""
        if self.text_area.tag_ranges(tk.SEL):
            self.copy_text()
            self.text_area.delete(tk.SEL_FIRST, tk.SEL_LAST)
    
    def copy_text(self):
        """Copy selected text"""
        if self.text_area.tag_ranges(tk.SEL):
            selected_text = self.text_area.get(tk.SEL_FIRST, tk.SEL_LAST)
            self.root.clipboard_clear()
            self.root.clipboard_append(selected_text)
    
    def paste_text(self):
        """Paste clipboard text"""
        try:
            text = self.root.clipboard_get()
            if self.text_area.tag_ranges(tk.SEL):
                self.text_area.delete(tk.SEL_FIRST, tk.SEL_LAST)
            self.text_area.insert(tk.INSERT, text)
        except tk.TclError:
            # Nothing in clipboard
            pass
    
    def undo_text(self):
        """Undo last action"""
        try:
            self.text_area.edit_undo()
        except tk.TclError:
            # Nothing to undo
            pass
    
    def redo_text(self):
        """Redo last undone action"""
        try:
            self.text_area.edit_redo()
        except tk.TclError:
            # Nothing to redo
            pass
    
    def update_line_column(self, event=None):
        """Update the line and column display"""
        position = self.text_area.index(tk.INSERT)
        line, column = position.split('.')
        self.line_column_display.config(text=f"Ln {line}, Col {int(column) + 1}")
    
    def on_text_modified(self, event=None):
        """Called when the text is modified"""
        if not self.is_modified:
            self.is_modified = True
            self.update_title()
        
        # Reset the modified flag for the widget (but keep our is_modified state)
        self.text_area.edit_modified(False)
    
    def update_title(self):
        """Update the window title to reflect the current file and modified state"""
        if self.file_path:
            file_name = os.path.basename(self.file_path)
            title = f"{file_name} - Simple Notepad"
        else:
            title = "Untitled - Simple Notepad"
        
        if self.is_modified:
            title = f"*{title}"
        
        self.root.title(title)
    
    def show_about(self):
        """Show information about the application"""
        messagebox.showinfo(
            "About Simple Notepad",
            "Simple Notepad\n\nA basic text editor created with Python and Tkinter."
        )

if __name__ == "__main__":
    root = tk.Tk()
    app = SimpleNotepad(root)
    root.mainloop()