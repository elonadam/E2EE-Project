import customtkinter as ctk
from tkinter import messagebox
from db_manager import DatabaseManager
from random import randint

# -------------------- Settings --------------------
ctk.set_appearance_mode("dark")  # "light" or "dark"
ctk.set_default_color_theme("blue")  # The built-in theme

# Color scheme based on the request
COLOR_BG = "#0C0C0C"  # obsidian black
COLOR_ENTRY = "#A9ACB6"  # aluminum gray
COLOR_BUTTON = "#A9ACB6"  # aluminum gray
COLOR_BUTTON_HOVER = "#001F3F"  # deep blue

user_token_num = ()  # tuple for validation


def print_auth_token(phone):
    # print token to terminal (for testing)
    token = randint(100000, 999999)
    print(f"Auth token for {phone}: {token}")
    return (token, phone)


class StartWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("E2EE Messaging - Start")
        self.geometry("300x200")
        self.configure(bg=COLOR_BG)

        self.phone_var = ctk.StringVar()
        self.token_var = ctk.StringVar()
        self.password_var = ctk.StringVar()

        title_label = ctk.CTkLabel(self, text="E2EE Server", text_color="white", fg_color=COLOR_BG, corner_radius=15)
        title_label.pack(pady=20)

        login_button = ctk.CTkButton(self, text="Login", fg_color=COLOR_BUTTON, text_color="black",
                                     hover_color=COLOR_BUTTON_HOVER,
                                     corner_radius=15, command=self.open_login)
        login_button.pack(pady=10)

        register_button = ctk.CTkButton(self, text="Register", fg_color=COLOR_BUTTON, text_color="black",
                                        hover_color=COLOR_BUTTON_HOVER,
                                        corner_radius=15, command=self.open_register)
        register_button.pack(pady=10)

    def open_login(self):
        self.destroy()
        login_win = LoginWindow()
        login_win.mainloop()

    def open_register(self):
        self.destroy()
        reg_win = RegisterWindow()
        reg_win.mainloop()


class RegisterWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("E2EE Messaging - Register")
        self.geometry("350x250")
        self.configure(bg=COLOR_BG)

        self.phone_var = ctk.StringVar()
        self.token_var = ctk.StringVar()
        self.password_var = ctk.StringVar()

        # These will store the generated token and phone for validation
        self.stored_token = None
        self.stored_phone = None

        # Placeholder text
        self.phone_placeholder = "Enter phone number"
        self.token_placeholder = "Enter auth token"
        self.placeholder_color = "gray50"
        self.normal_text_color = "black"

        # Initialize the vars with placeholders
        self.phone_var.set(self.phone_placeholder)
        self.token_var.set(self.token_placeholder)

        # Create Entry with placeholder
        self.phone_entry = ctk.CTkEntry(self, textvariable=self.phone_var,
                                        fg_color=COLOR_ENTRY, corner_radius=15,
                                        text_color=self.placeholder_color)
        self.phone_entry.pack(pady=10)

        # Bind focus events
        self.phone_entry.bind("<FocusIn>", self.clear_phone_placeholder)
        self.phone_entry.bind("<FocusOut>", self.add_phone_placeholder)

        get_token_button = ctk.CTkButton(self, text="Get Auth Token", fg_color=COLOR_BUTTON, corner_radius=15,
                                         text_color="black", hover_color=COLOR_BUTTON_HOVER, command=self.get_token)
        get_token_button.pack(pady=5)

        # Create Entry with placeholder
        self.token_entry = ctk.CTkEntry(self, textvariable=self.token_var,
                                        fg_color=COLOR_ENTRY, corner_radius=15,
                                        text_color=self.placeholder_color)
        self.token_entry.pack(pady=10)

        # Bind focus events
        self.token_entry.bind("<FocusIn>", self.clear_token_placeholder)
        self.token_entry.bind("<FocusOut>", self.add_token_placeholder)

        validate_token_button = ctk.CTkButton(self, text="Validate Token", fg_color=COLOR_BUTTON, text_color="black",
                                              hover_color=COLOR_BUTTON_HOVER, command=self.validate_token,
                                              corner_radius=15)
        validate_token_button.pack(pady=5)

        self.password_label = ctk.CTkLabel(self, text="Create Password:", text_color="white", fg_color=COLOR_BG)
        self.password_entry = ctk.CTkEntry(self, textvariable=self.password_var, fg_color=COLOR_ENTRY, show="*")
        self.set_pw_button = ctk.CTkButton(self, text="Set Password", fg_color=COLOR_BUTTON,
                                           hover_color=COLOR_BUTTON_HOVER, command=self.set_password)

    def clear_phone_placeholder(self, event):
        current_text = self.phone_entry.get()
        if current_text == self.phone_placeholder:
            self.phone_entry.delete(0, "end")
            self.phone_entry.configure(text_color=self.normal_text_color)

    def add_phone_placeholder(self, event):
        current_text = self.phone_entry.get()
        if not current_text:
            self.phone_entry.insert(0, self.phone_placeholder)
            self.phone_entry.configure(text_color=self.placeholder_color)

    def clear_token_placeholder(self, event):
        current_text = self.token_entry.get()
        if current_text == self.token_placeholder:
            self.token_entry.delete(0, "end")
            self.token_entry.configure(text_color=self.normal_text_color)

    def add_token_placeholder(self, event):
        current_text = self.token_entry.get()
        if not current_text:
            self.token_entry.insert(0, self.token_placeholder)
            self.token_entry.configure(text_color=self.placeholder_color)

    def get_token(self):
        """
        generate and store token and phone as instance vars, self.stored_token, self.stored_phone
        """
        phone = self.phone_var.get()
        if not phone.startswith("5"):
            messagebox.showerror("Error", "Please enter a phone number.")  # entered null
            return

        db = DatabaseManager()
        if db.check_user_exists(phone):
            messagebox.showerror("Error", "This phone number is already registered.")
            return

        # Generate and store token
        token, returned_phone = print_auth_token(phone)
        self.stored_token = token
        self.stored_phone = returned_phone

        messagebox.showinfo("Token Sent",
                            "Shhhh...Auth token sent securely to terminal. Please enter it below.")

    def validate_token(self):
        """
        compare entered cardinals with the stored values
        """
        phone = self.phone_var.get()
        entered_token = self.token_var.get()

        # Check if we have a stored token and phone
        if self.stored_token is None or self.stored_phone is None:
            messagebox.showerror("Error", "No token generated. Please click 'Get Auth Token' first.")
            return

        # Compare entered token and phone to the stored ones
        if phone == self.stored_phone and entered_token == str(self.stored_token):
            messagebox.showinfo("Success", "Token validated. Please create your password.")
            self.geometry("350x400")
            self.password_label.pack(pady=5)
            self.password_entry.pack(pady=5)
            self.set_pw_button.pack(pady=5)
        else:
            messagebox.showerror("Error", "Invalid token.")

    def set_password(self):
        phone = self.phone_var.get()
        password = self.password_var.get()
        if password:
            # Register user in DB using DatabaseManager
            db = DatabaseManager()
            # TODO 1 encrypt the password b4 storing it
            db.add_user(user_phone=phone, public_key="", user_pw=password)
            messagebox.showinfo("Registered", "Registration successful! You can now login.")
            self.destroy()
            start_win = StartWindow()
            start_win.mainloop()
        else:
            messagebox.showerror("Error", "Please enter a password.")


class LoginWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("E2EE Messaging - Login")
        self.geometry("300x200")
        self.configure(bg=COLOR_BG)

        self.attempt_count = 0  # track login attempts

        self.phone_var = ctk.StringVar()
        self.password_var = ctk.StringVar()

        phone_label = ctk.CTkLabel(self, text="Phone number:", text_color="white", fg_color=COLOR_BG, corner_radius=10)
        phone_label.pack(pady=5)
        self.phone_entry = ctk.CTkEntry(self, textvariable=self.phone_var, fg_color=COLOR_ENTRY, text_color="black")
        self.phone_entry.pack(pady=5)

        password_label = ctk.CTkLabel(self, text="Password:", text_color="white", fg_color=COLOR_BG, corner_radius=10)
        password_label.pack(pady=5)
        self.password_entry = ctk.CTkEntry(self, textvariable=self.password_var, fg_color=COLOR_ENTRY,
                                           text_color="black", show="*")
        self.password_entry.pack(pady=5)

        login_button = ctk.CTkButton(self, text="Login", fg_color=COLOR_BUTTON, hover_color=COLOR_BUTTON_HOVER,
                                     text_color="black", command=self.login_action)
        login_button.pack(pady=10)

    def login_action(self):
        phone = self.phone_var.get()
        password = self.password_var.get()
        db = DatabaseManager()
        if db.verify_user_credentials(phone, password):  # This method you add to db_manager.py
            messagebox.showinfo("Login", "Login successful!")
            self.destroy()
            msg_window = MessagesWindow(phone)
            msg_window.mainloop()
        else:
            self.attempt_count += 1
            if self.attempt_count < 3:
                messagebox.showerror("Error", f"Invalid credentials. Attempt {self.attempt_count}/3.")
            else:
                messagebox.showerror("Error", "Too many failed attempts. Closing application.")
                self.destroy()


class MessagesWindow(ctk.CTk):
    def __init__(self, phone):
        super().__init__()
        self.title("E2EE Messaging - Inbox")
        self.geometry("600x700")
        self.configure(bg=COLOR_BG)

        self.phone = phone

        title_label = ctk.CTkLabel(self, text="Your Messages", text_color="white",
                                   fg_color=COLOR_BG, font=("Arial", 20))
        title_label.pack(pady=10)

        # Frame for messages display
        self.messages_frame = ctk.CTkFrame(self, fg_color=COLOR_BG)
        self.messages_frame.pack(fill="both", expand=True, padx=20, pady=(20, 10))

        # Display messages initially
        self.display_messages()

        # Frame for sending messages
        send_frame = ctk.CTkFrame(self, fg_color="#1C1C1C")
        send_frame.pack(fill="x", padx=20, pady=10)

        send_label = ctk.CTkLabel(send_frame, text="Send a New Message", text_color="white", fg_color="#1C1C1C",
                                  font=("Arial", 16))
        send_label.pack(pady=5)

        # Recipient Entry
        recipient_label = ctk.CTkLabel(send_frame, text="Recipient Phone:", text_color="white", fg_color="#1C1C1C")
        recipient_label.pack(pady=5)
        self.recipient_var = ctk.StringVar()
        recipient_entry = ctk.CTkEntry(send_frame, textvariable=self.recipient_var, fg_color=COLOR_ENTRY)
        recipient_entry.pack(pady=5)

        # Subject Entry
        subject_label = ctk.CTkLabel(send_frame, text="Subject:", text_color="white", fg_color="#1C1C1C")
        subject_label.pack(pady=5)
        self.subject_var = ctk.StringVar()
        subject_entry = ctk.CTkEntry(send_frame, textvariable=self.subject_var, fg_color=COLOR_ENTRY)
        subject_entry.pack(pady=5)

        # Content Entry (use a Textbox for multiple lines if needed, here just single line for simplicity)
        content_label = ctk.CTkLabel(send_frame, text="Content:", text_color="white", fg_color="#1C1C1C")
        content_label.pack(pady=5)
        self.content_var = ctk.StringVar()
        content_entry = ctk.CTkEntry(send_frame, textvariable=self.content_var, fg_color=COLOR_ENTRY, width=400)
        content_entry.pack(pady=5)

        send_button = ctk.CTkButton(send_frame, text="Send Message", fg_color=COLOR_BUTTON,
                                    hover_color=COLOR_BUTTON_HOVER, text_color="black", command=self.send_message)
        send_button.pack(pady=10)

        # Logout/Back button at the bottom
        back_button = ctk.CTkButton(self, text="Logout", fg_color=COLOR_BUTTON,
                                    hover_color=COLOR_BUTTON_HOVER, command=self.back_to_start)
        back_button.pack(pady=10)

    def display_messages(self):
        # Clear previous message frames if any
        for widget in self.messages_frame.winfo_children():
            widget.destroy()

        db = DatabaseManager()
        messages = db.fetch_messages_for_user(self.phone)
        for msg in messages:
            sender, subject, content, date = msg
            msg_frame = ctk.CTkFrame(self.messages_frame, fg_color="#1C1C1C")
            msg_frame.pack(fill="x", pady=5)

            sender_label = ctk.CTkLabel(msg_frame, text=f"From: {sender}", text_color="white",
                                        fg_color="#1C1C1C", anchor="w")
            sender_label.pack(fill="x", padx=5)
            subject_label = ctk.CTkLabel(msg_frame, text=f"Subject: {subject}", text_color="white",
                                         fg_color="#1C1C1C", anchor="w")
            subject_label.pack(fill="x", padx=5)
            date_label = ctk.CTkLabel(msg_frame, text=f"Date: {date}", text_color="white",
                                      fg_color="#1C1C1C", anchor="w")
            date_label.pack(fill="x", padx=5)
            content_label = ctk.CTkLabel(msg_frame, text=f"Content: {content}", text_color="white",
                                         fg_color="#1C1C1C", anchor="w")
            content_label.pack(fill="x", padx=5)

    def send_message(self):
        recipient = self.recipient_var.get()
        subject = self.subject_var.get()
        content = self.content_var.get()

        # Validate inputs
        if not recipient:
            messagebox.showerror("Error", "Please enter a recipient phone number.")
            return
        if not subject:
            messagebox.showerror("Error", "Please enter a subject.")
            return
        if not content:
            messagebox.showerror("Error", "Please enter message content.")
            return

        # Send the message
        db = DatabaseManager()
        try:
            db.add_message(sender_num=self.phone, recipient_num=recipient, subject=subject, content=content)
            messagebox.showinfo("Success", "Message sent successfully!")
            # Optionally refresh the message list. If the user sends a message to themselves, they will see it.
            self.display_messages()

            # Clear the fields after sending
            self.recipient_var.set("")
            self.subject_var.set("")
            self.content_var.set("")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to send message: {e}")

    def back_to_start(self):
        self.destroy()
        start_win = StartWindow()
        start_win.mainloop()
