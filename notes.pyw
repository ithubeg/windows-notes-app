import tkinter as tk
from tkinter import messagebox, simpledialog, Toplevel
from tkinter.colorchooser import askcolor
from datetime import datetime
import json
import os

class StickyNotesApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sticky Notes")

        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        app_width = int(screen_width * 0.23)  # 23% of the screen width

        self.root.geometry(f"{app_width}x{screen_height}+{screen_width - app_width}+0")
        self.root.overrideredirect(True)
        self.root.configure(bg="#ffe5cc")

        self.notes_list = []
        self.filtered_notes = None
        self.load_notes_from_file()
        self.create_widgets()

    def create_widgets(self):
        self.root.configure(bg="#ffd699")
		
        self.note_title = tk.Entry(self.root, width=20, font=("Arial", 12), bg="#fff0cc", relief=tk.FLAT)
        self.note_title.grid(row=1, column=0, padx=10, pady=(40, 0), columnspan=3, sticky="ew")

        self.note_description = tk.Text(self.root, width=20, height=5, font=("Arial", 12), wrap=tk.WORD, bg="#fff0cc", relief=tk.FLAT)
        self.note_description.grid(row=2, column=0, padx=10, pady=10, columnspan=3, sticky="ew")
        self.note_description.bind("<FocusOut>", self.hide_description)

        add_button = tk.Button(self.root, text="Add Note", command=self.add_note, bg="#99ccff", relief=tk.FLAT)
        add_button.grid(row=3, column=0, padx=10, pady=10, sticky="ew")

        remove_button = tk.Button(self.root, text="Remove Note", command=self.remove_note, bg="#ff9999", relief=tk.FLAT)
        remove_button.grid(row=3, column=1, padx=10, pady=10, sticky="ew")

        color_button = tk.Button(self.root, text="Change Color", command=self.change_note_color, bg="#ccffcc", relief=tk.FLAT)
        color_button.grid(row=3, column=2, padx=10, pady=10, sticky="ew")

        self.search_entry = tk.Entry(self.root, width=20, font=("Arial", 12), bg="#fff0cc", relief=tk.FLAT)
        self.search_entry.grid(row=4, column=0, padx=10, pady=10, columnspan=2, sticky="ew")

        search_button = tk.Button(self.root, text="Search", command=self.search_notes, bg="#ffff99", relief=tk.FLAT)
        search_button.grid(row=4, column=2, padx=10, pady=10, sticky="ew")

        self.notes_label = tk.Label(self.root, text="Notes:", font=("Arial", 14, "bold"), bg="#ffd699")
        self.notes_label.grid(row=5, column=0, columnspan=3, pady=10)

        self.notes_listbox = tk.Listbox(self.root, selectmode=tk.SINGLE, width=20, height=20, font=("Arial", 12),
                                        bg="#ffe5cc", relief=tk.FLAT)
        self.notes_listbox.grid(row=6, column=0, columnspan=3, padx=10, pady=10, sticky="nsew")
        self.notes_listbox.bind("<ButtonRelease-1>", self.show_full_note)

        close_button = tk.Button(self.root, text=" X ", command=self.close_app, bg="#ff9999", relief=tk.FLAT)
        close_button.grid(row=0, column=2, padx=(0, 10), pady=0, sticky="ne")

        self.update_notes_list()

    def add_note(self):
        title = self.note_title.get().strip()
        description = self.note_description.get("1.0", tk.END).strip()
        if title and description:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            note_data = {
                "timestamp": timestamp,
                "title": title,
                "description": description,
                "color": "#ffe5cc"
            }
            self.notes_list.append(note_data)
            self.update_notes_list()
            self.note_title.delete(0, tk.END)
            self.note_description.delete("1.0", tk.END)
            self.save_notes_to_file()
        else:
            messagebox.showwarning("Warning", "Please enter both title and description.")

    def remove_note(self):
        selected_index = self.notes_listbox.curselection()
        if selected_index:
            index = int(selected_index[0])
            self.notes_list.pop(index)
            self.update_notes_list()
            self.save_notes_to_file()

    def change_note_color(self):
        selected_index = self.notes_listbox.curselection()
        if selected_index:
            index = int(selected_index[0])
            color = askcolor(title="Choose Color", color="#ffe5cc")[1]
            self.notes_list[index]["color"] = color
            self.update_notes_list()
            self.save_notes_to_file()

    def search_notes(self):
        query = self.search_entry.get().strip().lower()
        if query:
            self.filtered_notes = [note for note in self.notes_list if query in note["title"].lower() or query in note["description"].lower()]
            self.display_search_results(self.filtered_notes)
        else:
            self.filtered_notes = None
            self.update_notes_list()

    def display_search_results(self, results):
        self.notes_listbox.delete(0, tk.END)
        for note in results:
            note_text = f"{note['title']} ({note['timestamp'].split()[1]})"
            self.notes_listbox.insert(tk.END, note_text)
            self.notes_listbox.itemconfig(tk.END, {'bg': note["color"]})

    def show_full_note(self, event):
        selected_index = self.notes_listbox.curselection()
        if selected_index:
            index = int(selected_index[0])
            if self.filtered_notes:
                full_note = self.filtered_notes[index]
            else:
                full_note = self.notes_list[index]
            self.show_full_note_popup(full_note)

    def show_full_note_popup(self, full_note):
        popup = Toplevel()
        popup.title("Full Note")
        popup.geometry("300x200")

        full_note_description = tk.Text(popup, wrap=tk.WORD, font=("Arial", 12), bg="#eee", padx=10, pady=10)
        full_note_description.insert(tk.END, full_note['description'])
        full_note_description.pack(expand=True, fill="both")

    def hide_description(self, event):
        self.note_description.lower()

    def update_notes_list(self):
        self.notes_listbox.delete(0, tk.END)
        notes_to_display = self.filtered_notes if self.filtered_notes else self.notes_list
        for note in notes_to_display:
            note_text = f"{note['title']} ({note['timestamp'].split()[1]})"
            self.notes_listbox.insert(tk.END, note_text)
            self.notes_listbox.itemconfig(tk.END, {'bg': note["color"]})

    def save_notes_to_file(self):
        try:
            file_path = os.path.join(os.path.dirname(__file__), "notes_data.json")
            with open(file_path, "w") as file:
                json.dump(self.notes_list, file)
        except Exception as e:
            messagebox.showerror("Error", f"Error saving notes to file: {str(e)}")

    def load_notes_from_file(self):
        try:
            file_path = os.path.join(os.path.dirname(__file__), "notes_data.json")
            with open(file_path, "r") as file:
                self.notes_list = json.load(file)
        except FileNotFoundError:
            self.notes_list = []
        except Exception as e:
            messagebox.showerror("Error", f"Error loading notes from file: {str(e)}")

    def close_app(self):
        if messagebox.askokcancel("Close Application", "Are you sure you want to close the application?"):
            self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = StickyNotesApp(root)
    app.load_notes_from_file()
    app.update_notes_list()
    root.mainloop()
