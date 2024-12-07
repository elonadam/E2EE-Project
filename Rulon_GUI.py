import customtkinter as ctk
from tkinter import messagebox
from db_manager import DatabaseManager

# -------------------- Settings --------------------
ctk.set_appearance_mode("dark")  # "light" or "dark"
ctk.set_default_color_theme("blue")  # The built-in theme

# Color scheme based on the request
COLOR_BG = "#0C0C0C"  # obsidian black
COLOR_ENTRY = "#A9ACB6"  # aluminum gray
COLOR_BUTTON = "#A9ACB6"  # aluminum gray
COLOR_BUTTON_HOVER = "#001F3F"  # deep blue


# Mock auth token functions -- replace with real logic
def print_auth_token(phone):
    # print token to terminal (for testing)
    print(f"Auth token for {phone}: 123456")


def validate_auth_token(phone, token):
    # Mock validation
    return token == "123456"


class StartWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("E2EE Messaging - Start")
        self.geometry("300x200")
        self.configure(bg=COLOR_BG)

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

        phone_label = ctk.CTkLabel(self, text="Enter phone number:", text_color="white", fg_color=COLOR_BG,
                                   corner_radius=15)
        phone_label.pack(pady=5)
        self.phone_entry = ctk.CTkEntry(self, text_color="black", textvariable=self.phone_var, fg_color=COLOR_ENTRY,
                                        corner_radius=15)
        self.phone_entry.pack(pady=5)

        get_token_button = ctk.CTkButton(self, text="Get Auth Token", fg_color=COLOR_BUTTON, corner_radius=15,
                                         text_color="black", hover_color=COLOR_BUTTON_HOVER, command=self.get_token)
        get_token_button.pack(pady=5)

        token_label = ctk.CTkLabel(self, text="Enter Auth Token:", text_color="white", fg_color=COLOR_BG,
                                   corner_radius=15)
        token_label.pack(pady=5)
        self.token_entry = ctk.CTkEntry(self, textvariable=self.token_var, fg_color=COLOR_ENTRY,text_color="black",
                                        corner_radius=15)
        self.token_entry.pack(pady=5)

        validate_token_button = ctk.CTkButton(self, text="Validate Token", fg_color=COLOR_BUTTON, text_color="black",
                                              hover_color=COLOR_BUTTON_HOVER, command=self.validate_token,
                                              corner_radius=15)
        validate_token_button.pack(pady=5)

        self.password_label = ctk.CTkLabel(self, text="Create Password:", text_color="white", fg_color=COLOR_BG)
        self.password_entry = ctk.CTkEntry(self, textvariable=self.password_var, fg_color=COLOR_ENTRY, show="*")
        self.set_pw_button = ctk.CTkButton(self, text="Set Password", fg_color=COLOR_BUTTON,
                                           hover_color=COLOR_BUTTON_HOVER, command=self.set_password)

    def get_token(self):
        phone = self.phone_var.get()
        if not phone:
            messagebox.showerror("Error", "Please enter a phone number.")  # entered null
            return

        db = DatabaseManager()
        if db.check_user_exists(phone):
            messagebox.showerror("Error", "This phone number is already registered.")
            return

        # If not exists, proceed with token
        print_auth_token(phone)
        messagebox.showinfo("Token Sent",
                            "Shhhh...Auth token sent securely to terminal. Please enter it below.")

    def validate_token(self):
        phone = self.phone_var.get()
        token = self.token_var.get()
        if validate_auth_token(phone, token):
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
            # For now we don't have user_name from GUI, we can set a default or prompt for it
            # You can add a username field if needed
            db.add_user(user_phone=phone, user_name="", user_pw=password)
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
        self.geometry("600x400")
        self.configure(bg=COLOR_BG)

        self.phone = phone
        db = DatabaseManager()
        messages = db.fetch_messages_for_user(phone)  # This method you add to db_manager.py

        title_label = ctk.CTkLabel(self, text="Your Messages", text_color="white", fg_color=COLOR_BG,
                                   font=("Arial", 20))
        title_label.pack(pady=10)

        frame = ctk.CTkFrame(self, fg_color=COLOR_BG)
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        for msg in messages:
            sender, subject, content, date = msg
            msg_frame = ctk.CTkFrame(frame, fg_color="#1C1C1C")
            msg_frame.pack(fill="x", pady=5)

            sender_label = ctk.CTkLabel(msg_frame, text=f"From: {sender}", text_color="white", fg_color="#1C1C1C",
                                        anchor="w")
            sender_label.pack(fill="x", padx=5)
            subject_label = ctk.CTkLabel(msg_frame, text=f"Subject: {subject}", text_color="white", fg_color="#1C1C1C",
                                         anchor="w")
            subject_label.pack(fill="x", padx=5)
            date_label = ctk.CTkLabel(msg_frame, text=f"Date: {date}", text_color="white", fg_color="#1C1C1C",
                                      anchor="w")
            date_label.pack(fill="x", padx=5)
            content_label = ctk.CTkLabel(msg_frame, text=f"Content: {content}", text_color="white", fg_color="#1C1C1C",
                                         anchor="w")
            content_label.pack(fill="x", padx=5)

        back_button = ctk.CTkButton(self, text="Logout", fg_color=COLOR_BUTTON, hover_color=COLOR_BUTTON_HOVER,
                                    command=self.back_to_start)
        back_button.pack(pady=10)

    def back_to_start(self):
        self.destroy()
        start_win = StartWindow()
        start_win.mainloop()

#
# if __name__ == "__main__":
#     start = StartWindow()
#     start.mainloop()
