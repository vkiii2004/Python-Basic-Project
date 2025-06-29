from datetime import time
import tkinter as tk
from tkinter import ttk, messagebox, Frame, Toplevel, filedialog
import os
import csv
import shutil
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Custom styles and colors
BG_COLOR = "#f5f5f5"
PRIMARY_COLOR = "#4a6fa5"
SECONDARY_COLOR = "#166088"
ACCENT_COLOR = "#4fc3f7"
TEXT_COLOR = "#333333"
ERROR_COLOR = "#d32f2f"
SUCCESS_COLOR = "#388e3c"

class QuizApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Quiz Master Pro")
        self.root.geometry("1000x700")
        self.root.configure(bg=BG_COLOR)
        
        # Configure ttk styles
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Configure styles
        self.style.configure('TFrame', background=BG_COLOR)
        self.style.configure('TLabel', background=BG_COLOR, foreground=TEXT_COLOR, font=('Segoe UI', 11))
        self.style.configure('Header.TLabel', font=('Segoe UI', 20, 'bold'), foreground=PRIMARY_COLOR)
        self.style.configure('TButton', font=('Segoe UI', 11), background=PRIMARY_COLOR, foreground='white')
        self.style.map('TButton', 
                      background=[('active', SECONDARY_COLOR), ('pressed', SECONDARY_COLOR)],
                      foreground=[('active', 'white'), ('pressed', 'white')])
        self.style.configure('Secondary.TButton', background=SECONDARY_COLOR)
        self.style.configure('Accent.TButton', background=ACCENT_COLOR)
        self.style.configure('TRadiobutton', background=BG_COLOR, font=('Segoe UI', 11))
        self.style.configure('TEntry', font=('Segoe UI', 11), padding=5)
        
        self.username = ""
        self.timer_label = None
        self.completed_quizzes = set()
        self.submit_button = True
        self.selected_answers = []
        self.questions = []
        self.current_question_index = 0

        self.choose_subject()
        self.create_login_screen()
        
    def create_login_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        
        self.login_frame = ttk.Frame(self.root, padding=20)
        self.login_frame.pack(expand=True, fill='both')
        
        # Theme setting variable
        self.theme_var = tk.StringVar(value="light")  # Default to light theme
        
        # Load saved theme preference if exists
        try:
            with open("theme_settings.txt", "r") as f:
                saved_theme = f.read().strip()
                if saved_theme in ["light", "dark"]:
                    self.theme_var.set(saved_theme)
        except FileNotFoundError:
            pass
        
        # Apply the theme immediately
        self.apply_theme()
        
        ttk.Label(self.login_frame, text="Welcome to Quiz Master", style='Header.TLabel').grid(row=0, column=0, columnspan=2, pady=(0, 30))
        
        ttk.Label(self.login_frame, text="Username").grid(row=1, column=0, pady=5, sticky="e")
        self.username_entry = ttk.Entry(self.login_frame)
        self.username_entry.grid(row=1, column=1, pady=5, padx=10, sticky="ew")
        
        ttk.Label(self.login_frame, text="Password").grid(row=2, column=0, pady=5, sticky="e")
        self.password_entry = ttk.Entry(self.login_frame, show="•")
        self.password_entry.grid(row=2, column=1, pady=5, padx=10, sticky="ew")
        
        # Theme selection
        theme_frame = ttk.Frame(self.login_frame)
        theme_frame.grid(row=3, column=0, columnspan=2, pady=10)
        ttk.Label(theme_frame, text="Theme:").pack(side='left')
        ttk.Radiobutton(theme_frame, text="Light", variable=self.theme_var, 
                    value="light", command=self.apply_theme).pack(side='left', padx=5)
        ttk.Radiobutton(theme_frame, text="Dark", variable=self.theme_var, 
                    value="dark", command=self.apply_theme).pack(side='left', padx=5)
        
        self.login_btn = ttk.Button(self.login_frame, text="Login", command=self.login, style='TButton')
        self.login_btn.grid(row=4, column=0, columnspan=2, pady=20, ipady=5, sticky="ew")
        
        # Configure grid weights
        self.login_frame.grid_columnconfigure(0, weight=1)
        self.login_frame.grid_columnconfigure(1, weight=2)

    def apply_theme(self):
        """Apply the selected theme (light/dark)"""
        theme = self.theme_var.get()
        
        # Save theme preference
        with open("theme_settings.txt", "w") as f:
            f.write(theme)
        
        # Define colors for each theme
        if theme == "dark":
            bg_color = "#2d2d2d"
            fg_color = "#ffffff"
            entry_bg = "#3d3d3d"
            button_bg = "#4a6fa5"
        else:  # light
            bg_color = "#f5f5f5"
            fg_color = "#333333"
            entry_bg = "#ffffff"
            button_bg = "#4a6fa5"
        
        # Update all widget styles
        self.style.configure('.', background=bg_color, foreground=fg_color)
        self.style.configure('TFrame', background=bg_color)
        self.style.configure('TLabel', background=bg_color, foreground=fg_color)
        self.style.configure('TEntry', fieldbackground=entry_bg, foreground=fg_color)
        self.style.configure('TButton', background=button_bg, foreground='white')
        self.style.configure('TRadiobutton', background=bg_color, foreground=fg_color)
        
        # Update specific widgets that need different styling
        self.style.configure('Header.TLabel', foreground=button_bg if theme == "light" else "#4fc3f7")
        
        # Update root window background
        self.root.configure(bg=bg_color)
        
        # Force update all widgets
        for widget in self.root.winfo_children():
            widget.update()

    def login(self):
        self.username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        if self.username == "admin" and password == "admin":
            self.create_admin_panel()
            return

        if not self.username or not password:
            messagebox.showerror("Error", "Please enter both username and password.")
            return

        if not os.path.exists("student_info.csv"):
            messagebox.showerror("Error", "Student database not found. Please upload student CSV.")
            return

        with open("student_info.csv", "r", newline="") as file:
            reader = csv.reader(file)
            for row in reader:
                if len(row) >= 2 and row[0] == self.username and row[1] == password:
                    self.create_quiz_section()
                    return

        messagebox.showerror("Error", "Invalid Username or Password")

    def create_admin_panel(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Main container
        main_container = ttk.Frame(self.root)
        main_container.pack(fill='both', expand=True)
        
        # Sidebar
        self.admin_sidebar = ttk.Frame(main_container, width=200, style='TFrame')
        self.admin_sidebar.pack(side="left", fill="y")
        
        # Menu button with modern icon
        self.menu_button = ttk.Button(self.admin_sidebar, text="☰", command=self.toggle_admin_sidebar, 
                                    style='Secondary.TButton', width=3)
        self.menu_button.pack(pady=10, padx=5, fill='x')
        
        # Admin buttons - Add "Set Quiz Timer" option here
        self.admin_buttons = []
        options = [
            ("Manage Quizzes", self.manage_quizzes),
            ("Add Quizzes", self.manage_quizzes),
            ("Student Info", self.student_info),
            ("Set Quiz Timer", self.set_quiz_timer),  # New option added here
            ("Return", self.create_login_screen)
            
        ]
        
        for text, command in options:
            btn = ttk.Button(self.admin_sidebar, text=text, command=command, style='TButton')
            btn.pack(pady=5, padx=5, fill='x')
            btn.pack_forget()
            self.admin_buttons.append(btn)
        
        # Main content area
        self.admin_frame = ttk.Frame(main_container, padding=20)
        self.admin_frame.pack(expand=True, fill="both")
        
        # Admin panel watermark
        self.watermark_label = ttk.Label(
            self.admin_frame, text="ADMIN PANEL", style='Header.TLabel'
        )
        self.watermark_label.place(relx=0.5, rely=0.5, anchor="center")

    def set_quiz_timer(self):
        """Create interface to set quiz timer in minutes"""
        for widget in self.admin_frame.winfo_children():
            widget.destroy()

        container = ttk.Frame(self.admin_frame, padding=20)
        container.pack(expand=True)

        ttk.Label(container, text="Set Quiz Timer Duration", style='Header.TLabel').pack(pady=(0, 20))

        # Input frame
        input_frame = ttk.Frame(container)
        input_frame.pack(pady=20)

        ttk.Label(input_frame, text="Duration (minutes):").pack(side='left')
        
        # Entry for minutes with validation
        vcmd = (self.root.register(self.validate_minutes), '%P')
        self.timer_entry = ttk.Entry(input_frame, validate='key', validatecommand=vcmd, width=10)
        self.timer_entry.pack(side='left', padx=10)
        
        # Load existing timer value if available
        try:
            with open("timer_settings.txt", "r") as f:
                total_seconds = int(f.read())
                minutes = total_seconds // 60
                self.timer_entry.insert(0, str(minutes))
        except (FileNotFoundError, ValueError):
            self.timer_entry.insert(0, "5")  # Default value

        # Button frame
        btn_frame = ttk.Frame(container)
        btn_frame.pack(pady=20)

        ttk.Button(btn_frame, text="Save", command=self.save_quiz_timer, 
                style='TButton').pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Cancel", command=self.create_admin_panel, 
                style='Secondary.TButton').pack(side='right', padx=5)

    def validate_minutes(self, new_value):
        """Validate that the input is a positive integer"""
        if new_value == "":
            return True
        try:
            return int(new_value) > 0
        except ValueError:
            return False

    def save_quiz_timer(self):
        """Save the timer settings to file"""
        minutes_str = self.timer_entry.get()
        if not minutes_str:
            messagebox.showerror("Error", "Please enter a duration")
            return
        
        try:
            minutes = int(minutes_str)
            if minutes <= 0:
                raise ValueError("Time must be positive")
                
            # Convert minutes to seconds
            total_seconds = minutes * 60
            
            with open("timer_settings.txt", "w") as f:
                f.write(str(total_seconds))
                
            messagebox.showinfo("Success", f"Quiz timer set to {minutes} minutes")
            self.create_admin_panel()
            
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid positive number")
            self.timer_entry.focus()
        
    def toggle_admin_sidebar(self):
        for btn in self.admin_buttons:
            if btn.winfo_ismapped():
                btn.pack_forget()
            else:
                btn.pack(pady=5, padx=5, fill='x')
        
    def student_performance(self):
        for widget in self.admin_frame.winfo_children():
            widget.destroy()
        
        ttk.Label(self.admin_frame, text="Student Performance", style='Header.TLabel').pack(pady=20)
        ttk.Label(self.admin_frame, text="List of past quizzes with total student entries").pack()
        ttk.Button(self.admin_frame, text="Back", command=self.create_admin_panel, style='TButton').pack(pady=10)
        
    def student_info(self):
        for widget in self.admin_frame.winfo_children():
            widget.destroy()
            
        container = ttk.Frame(self.admin_frame)
        container.pack(expand=True, pady=20)
        
        ttk.Label(container, text="Student Information", style='Header.TLabel').pack(pady=(0, 20))
        
        btn_frame = ttk.Frame(container)
        btn_frame.pack()
        
        ttk.Button(btn_frame, text="Upload Student CSV", command=self.upload_student_csv, 
                 style='TButton').pack(pady=10, fill='x')
        ttk.Button(btn_frame, text="View Student CSV", command=self.view_student_csv, 
                 style='TButton').pack(pady=10, fill='x')
        ttk.Button(btn_frame, text="Add Student Manually", command=self.add_student_manually, 
                 style='TButton').pack(pady=10, fill='x')
        ttk.Button(btn_frame, text="Back", command=self.create_admin_panel, 
                 style='Secondary.TButton').pack(pady=20, fill='x')
        ttk.Button(btn_frame, text="Add Student CSV", command=self.upload_student_csv, 
                 style='TButton').pack(pady=10, fill='x')
        
    def view_student_csv(self):
        file_path = "student_info.csv"
        if os.path.exists(file_path):
            os.startfile(file_path)
        else:
            messagebox.showerror("Error", "No student CSV file found.")
    
    def upload_student_csv(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if file_path:
            try:
                with open(file_path, "r") as file:
                    reader = csv.reader(file)
                    for row in reader:
                        print(f"Username: {row[0]}, Password: {row[1]}")
                messagebox.showinfo("Success", "Student data uploaded successfully.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to upload file: {str(e)}")
    
    def add_student_manually(self):
        top = Toplevel(self.root)
        top.title("Add Student")
        top.geometry("400x250")
        top.resizable(False, False)
        
        main_frame = ttk.Frame(top, padding=20)
        main_frame.pack(expand=True, fill='both')
        
        ttk.Label(main_frame, text="Add New Student", style='Header.TLabel').pack(pady=(0, 20))
        
        ttk.Label(main_frame, text="Username").pack(pady=5)
        username_entry = ttk.Entry(main_frame)
        username_entry.pack(pady=5, fill='x')
        
        ttk.Label(main_frame, text="Password").pack(pady=5)
        password_entry = ttk.Entry(main_frame, show="•")
        password_entry.pack(pady=5, fill='x')
        
        def save_student():
            username = username_entry.get().strip()
            password = password_entry.get().strip()
            
            if username and password:
                try:
                    with open("student_info.csv", "r", newline="") as file:
                        existing_data = list(csv.reader(file))
                except FileNotFoundError:
                    existing_data = []
                
                with open("student_info.csv", "a", newline="") as file:
                    writer = csv.writer(file)
                    if [username, password] not in existing_data:
                        writer.writerow([username, password])
                        messagebox.showinfo("Success", "Student added successfully.")
                    else:
                        messagebox.showerror("Error", "Username already exists.")
                    
                top.destroy()
            else:
                messagebox.showerror("Error", "Please enter valid details.")
            
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(pady=10, fill='x')
        
        ttk.Button(btn_frame, text="Save", command=save_student, style='TButton').pack(side='left', padx=5, expand=True)
        ttk.Button(btn_frame, text="Cancel", command=top.destroy, style='Secondary.TButton').pack(side='right', padx=5, expand=True)
        
    def manage_quizzes(self):
        for widget in self.admin_frame.winfo_children():
            widget.destroy()
            
        container = ttk.Frame(self.admin_frame, padding=20)
        container.pack(expand=True, fill='both')
        
        ttk.Label(container, text="Manage Quizzes", style='Header.TLabel').pack(pady=(0, 20))
        
        btn_frame = ttk.Frame(container)
        btn_frame.pack()
        
        ttk.Button(btn_frame, text="Upload Quiz CSV", command=self.upload_quiz_csv, 
             style='TButton', width=20).pack(pady=10, fill='x')
        ttk.Button(btn_frame, text="Generate New Question", command=self.generate_question, 
                style='TButton', width=20).pack(pady=10, fill='x')
        ttk.Button(btn_frame, text="Set Quiz Timer", command=self.set_quiz_timer,
                style='TButton', width=20).pack(pady=10, fill='x')
        ttk.Button(btn_frame, text="Refresh Quiz List", command=self.refresh_quiz_list, 
                style='Secondary.TButton', width=20).pack(pady=10, fill='x')
        ttk.Button(btn_frame, text="Back", command=self.create_admin_panel, 
                style='Secondary.TButton', width=20).pack(pady=10, fill='x')
        
        self.refresh_quiz_list()
        
    def upload_quiz_csv(self):
        subject_popup = Toplevel(self.root)
        subject_popup.title("Select Subject")
        subject_popup.geometry("400x300")
        subject_popup.resizable(False, False)

        main_frame = ttk.Frame(subject_popup, padding=20)
        main_frame.pack(expand=True, fill='both')
        
        ttk.Label(main_frame, text="Choose Subject", style='Header.TLabel').pack(pady=(0, 20))

        subjects = [
            "Power Device and Circuit",
            "Advance Java Programming",
            "Project Management",
            "Cellular Network"
        ]

        selected_subject = tk.StringVar()
        
        for subject in subjects:
            ttk.Radiobutton(main_frame, text=subject, variable=selected_subject, 
                          value=subject).pack(anchor="w", padx=20, pady=5)

        def confirm_subject():
            subject_name = selected_subject.get().strip()

            if not subject_name:
                messagebox.showerror("Error", "Please select a subject first!")
                return
            
            file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
            
            if file_path:
                filename = subject_name.replace(" ", "_") + ".csv"
                try:
                    shutil.copy(file_path, filename)
                    messagebox.showinfo("Success", f"Quiz file uploaded for '{subject_name}' successfully!")
                    self.refresh_quiz_list()
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to upload file: {str(e)}")

            subject_popup.destroy()
        
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(pady=20, fill='x')
        
        ttk.Button(btn_frame, text="OK", command=confirm_subject, style='TButton').pack(side='left', padx=5, expand=True)
        ttk.Button(btn_frame, text="Cancel", command=subject_popup.destroy, style='Secondary.TButton').pack(side='right', padx=5, expand=True)
            
    def refresh_quiz_list(self):
        try:
            with open("quiz_questions.csv", "r") as file:
                reader = csv.reader(file)
                self.quiz_questions = list(reader)
            messagebox.showinfo("Success", "Quiz list refreshed successfully!")
        except FileNotFoundError:
            messagebox.showerror("Error", "No quiz file found. Please upload a quiz CSV.")
  
    def generate_question(self):
        for widget in self.admin_frame.winfo_children():
            widget.destroy()

        container = ttk.Frame(self.admin_frame, padding=20)
        container.pack(expand=True, fill='both')
        
        ttk.Label(container, text="Enter Question Details", style='Header.TLabel').pack(pady=(0, 20))

        fields = ["Question", "Option A", "Option B", "Option C", "Option D", "Correct Option (A/B/C/D)"]
        self.entries = {}

        for field in fields:
            ttk.Label(container, text=field).pack(pady=2)
            entry = ttk.Entry(container, width=60)
            entry.pack(pady=5)
            self.entries[field] = entry

        btn_frame = ttk.Frame(container)
        btn_frame.pack(pady=20, fill='x')
        
        ttk.Button(btn_frame, text="Save Question", command=self.save_question, 
                 style='TButton').pack(side='left', padx=5, expand=True)
        ttk.Button(btn_frame, text="Back", command=self.manage_quizzes, 
                 style='Secondary.TButton').pack(side='right', padx=5, expand=True)
        
    def save_question(self):
        data = [
            self.entries["Question"].get().strip(),
            self.entries["Option A"].get().strip(),
            self.entries["Option B"].get().strip(),
            self.entries["Option C"].get().strip(),
            self.entries["Option D"].get().strip(),
            self.entries["Correct Option (A/B/C/D)"].get().strip().upper()
        ]

        if "" in data or data[-1] not in ["A", "B", "C", "D"]:
            messagebox.showerror("Error", "Please fill all fields correctly.")
            return

        try:
            file_name = "quiz_questions.csv"
            with open(file_name, "a", newline="") as file:
                writer = csv.writer(file)
                writer.writerow(data)
            messagebox.showinfo("Success", "Question saved successfully.")
            self.manage_quizzes()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save question: {str(e)}")
            
    def set_quiz_timer(self):
        """Admin panel function to set quiz timer duration"""
        for widget in self.admin_frame.winfo_children():
            widget.destroy()

        container = ttk.Frame(self.admin_frame, padding=20)
        container.pack(expand=True)

        ttk.Label(container, text="Set Quiz Timer", style='Header.TLabel').pack(pady=(0, 20))

        # Minutes entry
        ttk.Label(container, text="Minutes:").pack()
        self.minutes_entry = ttk.Entry(container)
        self.minutes_entry.pack(pady=5)
        self.minutes_entry.insert(0, "5")  # Default value

        # Seconds entry
        ttk.Label(container, text="Seconds:").pack()
        self.seconds_entry = ttk.Entry(container)
        self.seconds_entry.pack(pady=5)
        self.seconds_entry.insert(0, "0")  # Default value

        # Button frame
        btn_frame = ttk.Frame(container)
        btn_frame.pack(pady=20)

        ttk.Button(btn_frame, text="Save Timer", command=self.save_timer_settings, 
                style='TButton').pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Back", command=self.manage_quizzes, 
                style='Secondary.TButton').pack(side='right', padx=5)

    def save_timer_settings(self):
        """Save the timer settings to a file"""
        try:
            minutes = int(self.minutes_entry.get())
            seconds = int(self.seconds_entry.get())
            
            if minutes < 0 or seconds < 0 or seconds >= 60:
                raise ValueError("Invalid time values")
                
            total_seconds = minutes * 60 + seconds
            
            with open("timer_settings.txt", "w") as f:
                f.write(str(total_seconds))
                
            messagebox.showinfo("Success", "Timer settings saved successfully!")
            self.manage_quizzes()
            
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers (0-59 for seconds)")
            
    def create_quiz_section(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Main container
        main_container = ttk.Frame(self.root)
        main_container.pack(fill='both', expand=True)
        
        # Sidebar
        self.sidebar = ttk.Frame(main_container, width=200, style='TFrame')
        self.sidebar.pack(side="left", fill="y")
        
        # Menu button
        self.menu_button = ttk.Button(self.sidebar, text="☰", command=self.toggle_sidebar, 
                                    style='Secondary.TButton', width=3)
        self.menu_button.pack(pady=10, padx=5, fill='x')
        
        # Sidebar buttons
        self.sidebar_buttons = []
        options = [
            ("Choose Subject", self.choose_subject),
            ("Performance", self.show_performance),
            ("Back", self.create_login_screen)
        ]
        for text, command in options:
            btn = ttk.Button(self.sidebar, text=text, command=command, style='TButton')
            btn.pack(pady=5, padx=5, fill='x')
            btn.pack_forget()
            self.sidebar_buttons.append(btn)
        
        # Quiz area
        self.quiz_frame = ttk.Frame(main_container, padding=20)
        self.quiz_frame.pack(expand=True, fill="both")
        
        # Welcome message
        self.watermark_label = ttk.Label(
            self.quiz_frame, text="Welcome to the Quiz", style='Header.TLabel'
        )
        self.watermark_label.place(relx=0.5, rely=0.35, anchor="center")
        
        self.watermark_label2 = ttk.Label(
            self.quiz_frame, text=self.username, font=('Segoe UI', 25, 'bold'), 
            foreground=SECONDARY_COLOR, background=BG_COLOR
        )
        self.watermark_label2.place(relx=0.5, rely=0.45, anchor="center")
        
    def toggle_sidebar(self):
        for btn in self.sidebar_buttons:
            if btn.winfo_ismapped():
                btn.pack_forget()
            else:
                btn.pack(pady=5, padx=5, fill='x')
        
    def choose_subject(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        
        self.subject_frame = ttk.Frame(self.root, padding=20)
        self.subject_frame.pack(expand=True, fill='both')
        
        ttk.Label(self.subject_frame, text="Select a Subject", style='Header.TLabel').pack(pady=(0, 30))
        
        subjects = [
            "Power Device and Circuit",
            "Advance Java Programming",
            "Project Management",
            "Cellular Network"
        ]
        
        self.selected_subject = tk.StringVar()
        
        # Create a frame for radio buttons
        radio_frame = ttk.Frame(self.subject_frame)
        radio_frame.pack()
        
        for subject in subjects:
            ttk.Radiobutton(radio_frame, text=subject, variable=self.selected_subject, 
                          value=subject).pack(anchor="w", pady=5, padx=20)
        
        # Button frame
        btn_frame = ttk.Frame(self.subject_frame)
        btn_frame.pack(pady=20)
        
        ttk.Button(btn_frame, text="OK", command=self.open_subject_options, 
                 style='TButton').pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Back", command=self.create_quiz_section, 
                 style='Secondary.TButton').pack(side='right', padx=5)
    
    def open_subject_options(self):
        for widget in self.root.winfo_children():
            widget.destroy()
            
        subject = self.selected_subject.get()
        if not subject:
            messagebox.showerror("Error", "Please select a subject.")
            return

        container = ttk.Frame(self.root, padding=20)
        container.pack(expand=True, fill='both')
        
        ttk.Label(container, text=f"{subject} Options", style='Header.TLabel').pack(pady=(0, 30))
        
        btn_frame = ttk.Frame(container)
        btn_frame.pack()
        
        ttk.Button(btn_frame, text="Start Quiz", command=self.start_quiz, 
                 style='TButton', width=15).pack(pady=10, fill='x')
        ttk.Button(btn_frame, text="Previous Quiz", command=self.review_answers, 
                 style='TButton', width=15).pack(pady=10, fill='x')
        ttk.Button(btn_frame, text="Back", command=self.create_quiz_section, 
                 style='Secondary.TButton', width=15).pack(pady=10, fill='x')
        
    def show_score_and_review_option(self):
        correct_answers = [q[5] for q in self.questions]
        score = sum(1 for i, answer in enumerate(self.selected_answers) if answer == correct_answers[i])
        total_questions = len(self.questions)

        message = f"Your score: {score} / {total_questions}\n\n"
        if score == total_questions:
            message += "Excellent work! You got all answers correct!"
        elif score > total_questions * 0.7:
            message += "Great job! Keep up the good work!"
        else:
            message += "Good effort! Keep practicing to improve your score."

        messagebox.showinfo("Quiz Finished", message)

        review_button = ttk.Button(self.root, text="Review Questions & Answers", 
                                command=self.review_answers, style='Accent.TButton')
        review_button.pack(pady=20)
        
    def review_answers(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        container = ttk.Frame(self.root, padding=20)
        container.pack(expand=True, fill='both')
        
        # Create a canvas and scrollbar for the review content
        canvas = tk.Canvas(container, bg=BG_COLOR, highlightthickness=0)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
        ))
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Display each question with answers
        for i, question_data in enumerate(self.questions):
            question_text = question_data[0]
            correct_answer = question_data[5]
            selected_answer = self.selected_answers[i]
            
            # Question frame
            q_frame = ttk.Frame(scrollable_frame, padding=10, style='TFrame')
            q_frame.pack(fill='x', pady=5, padx=5)
            
            # Question label
            ttk.Label(q_frame, text=f"Q{i + 1}: {question_text}", 
                     font=('Segoe UI', 12, 'bold')).pack(anchor='w')
            
            # User's answer
            user_frame = ttk.Frame(q_frame)
            user_frame.pack(fill='x', pady=2)
            ttk.Label(user_frame, text="Your Answer:", font=('Segoe UI', 10)).pack(side='left')
            ttk.Label(user_frame, text=selected_answer, font=('Segoe UI', 10, 'bold'),
                    foreground=ERROR_COLOR if selected_answer != correct_answer else SUCCESS_COLOR).pack(side='left', padx=5)
            
            # Correct answer
            correct_frame = ttk.Frame(q_frame)
            correct_frame.pack(fill='x', pady=2)
            ttk.Label(correct_frame, text="Correct Answer:", font=('Segoe UI', 10)).pack(side='left')
            ttk.Label(correct_frame, text=correct_answer, font=('Segoe UI', 10, 'bold'),
                    foreground=SUCCESS_COLOR).pack(side='left', padx=5)
            
            # Separator
            ttk.Separator(q_frame).pack(fill='x', pady=5)
        
        # Back button
        ttk.Button(container, text="Back", command=self.choose_subject, 
                 style='Secondary.TButton').pack(pady=20)
        
    def start_quiz(self):
        subject = self.selected_subject.get()
        if not subject:
            messagebox.showerror("Error", "Please select a subject.")
            return
        
        if subject in self.completed_quizzes:
            messagebox.showinfo("Quiz Already Taken", "You have already completed this quiz.")
            return

        # Load timer settings
        try:
            with open("timer_settings.txt", "r") as f:
                self.countdown_seconds = int(f.read())
        except (FileNotFoundError, ValueError):
            # Default to 5 minutes if no settings exist
            self.countdown_seconds = 300  # 5 minutes in seconds

        for widget in self.root.winfo_children():
            widget.destroy()

        self.load_questions(subject)
        if not self.questions:
            messagebox.showerror("Error", "No questions available for this subject.")
            return
        
        self.completed_quizzes.add(subject) 
        self.current_question_index = 0
        self.selected_answers = []
        
        # Main quiz container
        self.quiz_container = ttk.Frame(self.root)
        self.quiz_container.pack(fill='both', expand=True)
        
        # Timer display at top
        timer_frame = ttk.Frame(self.quiz_container)
        timer_frame.pack(fill='x', padx=20, pady=10)
        
        ttk.Label(timer_frame, text="Time Remaining:", font=('Segoe UI', 12)).pack(side='left')
        self.timer_label = ttk.Label(timer_frame, text="", font=('Segoe UI', 12, 'bold'))
        self.timer_label.pack(side='left', padx=5)
        
        # Start the timer
        self.update_timer()
        
        # Question area
        self.quiz_frame = ttk.Frame(self.quiz_container, padding=20)
        self.quiz_frame.pack(fill='both', expand=True)
        
        # Display first question
        self.display_question()
        
        # Submit button at bottom
        self.submit_button = ttk.Button(self.quiz_container, text="Submit Quiz", 
                                    command=self.submit_quiz, 
                                    state="disabled",
                                    style='Accent.TButton')
        self.submit_button.pack(side='bottom', fill='x', pady=10, padx=20, ipady=10)

    def load_questions(self, subject):
        subject_files = {
            "Power Device and Circuit": "power_device_and_circuit_questions.csv",
            "Advance Java Programming": "advance_java_programming_questions.csv",
            "Project Management": "project_management_questions.csv",
            "Cellular Network": "cellular_network_questions.csv"
        }
        
        file_name = subject_files.get(subject)
        
        if not file_name:
            messagebox.showerror("Error", "Invalid subject selected.")
            return False
        
        try:
            with open(file_name, "r") as file:
                reader = csv.reader(file)
                self.questions = [row for row in reader if row]
        except FileNotFoundError:
            messagebox.showerror("Error", f"Quiz file for {subject} not found.")
            return False
        
        if not self.questions:
            messagebox.showwarning("Warning", "No questions found in the quiz file.")
            return False
        
        return True
            
    def display_question(self):
        if self.current_question_index >= len(self.questions):
            messagebox.showinfo("Quiz Completed", "You have completed the quiz!")
            self.submit_quiz()
            return

        question_data = self.questions[self.current_question_index]
        question_text = question_data[0]

        # Clear previous question widgets
        for widget in self.quiz_frame.winfo_children():
            widget.destroy()

        # Display the question
        ttk.Label(self.quiz_frame, text=question_text, 
                 font=('Segoe UI', 14, 'bold'), wraplength=700).pack(pady=20)

        # Options frame
        options_frame = ttk.Frame(self.quiz_frame)
        options_frame.pack(fill='x', padx=20)
        
        # Define the options and initialize the selected_option
        self.selected_option = tk.StringVar()
        
        options = [question_data[1], question_data[2], question_data[3], question_data[4]]
        for i, option in enumerate(options):
            ttk.Radiobutton(options_frame, text=option, variable=self.selected_option, 
                          value=chr(65 + i)).pack(anchor='w', pady=5, padx=20)

        # Navigation buttons
        nav_frame = ttk.Frame(self.quiz_frame)
        nav_frame.pack(pady=20)
        
        self.next_button = ttk.Button(nav_frame, text="Next", command=self.next_question, 
                                    style='TButton')
        self.next_button.pack(ipady=5, padx=10)
        
        # Enable submit button if this is the last question
        if self.current_question_index == len(self.questions) - 1:
            self.submit_button.config(state="normal")
        
    def update_timer(self):
        mins, secs = divmod(self.countdown_seconds, 60)
        time_format = f'{mins:02d}:{secs:02d}'
        self.timer_label.config(text=time_format)

        if self.countdown_seconds > 0:
            self.countdown_seconds -= 1
            self.root.after(1000, self.update_timer)
        else:
            messagebox.showinfo("Time's Up!", "The time for the quiz has expired!")
            self.submit_quiz()
        
    def submit_quiz(self):
        if hasattr(self, 'timer_label'):
         self.root.after_cancel(self.update_timer)
        
        if self.submit_button['state'] == 'normal':
            self.submit_button.config(state="disabled")

        self.calculate_score()
        with open("completed_quizzes.txt", "a") as file:
            file.write(f"{self.selected_subject.get()}\n")
            
        self.show_score_and_review_option()
        
    def load_completed_quizzes(self):
        if os.path.exists("completed_quizzes.txt"):
            with open("completed_quizzes.txt", "r") as file:
                quizzes = file.readlines()
                self.completed_quizzes = {quiz.strip() for quiz in quizzes}
        
    def calculate_score(self):
        if len(self.selected_answers) != len(self.questions):
            messagebox.showwarning("Warning", "Not all questions were answered!")
        
        correct_answers = [q[5] for q in self.questions]
        self.score = 0
        
        for i in range(min(len(self.selected_answers), len(self.questions))):
            if self.selected_answers[i] == correct_answers[i]:
                self.score += 1
        
        self.total_questions = len(self.questions)

    def next_question(self):
        if not self.selected_option.get():
            messagebox.showwarning("No Option", "Please select an answer.")
            return
        
        self.selected_answers.append(self.selected_option.get())
        self.current_question_index += 1
        
        if self.current_question_index < len(self.questions):
            self.display_question()
        else:
            self.submit_quiz()

    def finish_quiz(self):
        messagebox.showinfo("Quiz Finished", "Your quiz is finished!")
          
    def show_performance(self):
        for widget in self.root.winfo_children():
            widget.destroy()
                
        subjects = ["PD", "JAVA", "PM", "CN"]
        scores = [75, 85, 90, 70]
                
        fig, ax = plt.subplots(figsize=(8, 6))
        bars = ax.bar(subjects, scores, color=[PRIMARY_COLOR, SECONDARY_COLOR, ACCENT_COLOR, '#9c27b0'])
        ax.set_xlabel("Subjects")
        ax.set_ylabel("Scores")
        ax.set_title("Subject Wise Performance")
        ax.set_xticklabels(subjects, rotation=45, ha="right")
        
        avg_score = sum(scores) / len(scores)

        for bar, score in zip(bars, scores):
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 1, str(score), ha='center', fontsize=10)

        ax.axhline(y=avg_score, color='orange', linestyle='--', linewidth=2, label=f'Average Score: {avg_score:.2f}')
        ax.legend(loc='upper left')

        canvas = FigureCanvasTkAgg(fig, master=self.root)
        canvas.draw()
        canvas.get_tk_widget().pack()

        avg_label = ttk.Label(self.root, text=f"Average Score: {avg_score:.2f}", 
                            font=('Segoe UI', 16), style='Header.TLabel')
        avg_label.pack(pady=20)

        ttk.Button(self.root, text="Back", command=self.create_quiz_section, 
                 style='Secondary.TButton').pack(pady=20)

if __name__ == "__main__":
    root = tk.Tk()
    app = QuizApp(root)
    root.mainloop()