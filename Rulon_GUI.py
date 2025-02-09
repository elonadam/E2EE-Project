import customtkinter as ctk
from db_manager import DatabaseManager
from random import randint
from encryption_funcs import *  # hash_password, verify_password

# -------------------- Settings --------------------
ctk.set_appearance_mode("dark")  # "light" or "dark"
ctk.set_default_color_theme("blue")  # The built-in theme

# Color scheme based on the request
COLOR_BG = "#0C0C0C"  # obsidian black
COLOR_ENTRY = "#A9ACB6"  # aluminum gray
COLOR_BUTTON = "#A9ACB6"  # aluminum gray
COLOR_BUTTON_HOVER = "#800020"  # burgundy
TEXT_COLOR = "#FFFFFF"


def print_auth_token(phone):
    # print token to terminal (for testing)
    token = randint(100000, 999999)
    print(f"Auth token for {phone}: {token}")
    return (token, phone)


def print_encryption_steps(flag):
    global log_str  # Access the global log_st
    if flag:
        print(f"\033[1mEncryption steps for message:\033[0m")
    else:
        print(f"\033[1mRegistration steps for user:\033[0m")
    print(log_str + "\n")  # Print the log_str and close the code block
    log_str = ""  # Reset the log_str to an empty string
    print(f"\033[1mEnd of steps.\033[0m")


def get_center_position(screen_width, screen_height, window_width, window_height):
    # Calculate the (x, y) position to center a window on the screen.
    x = int((screen_width - window_width) / 2)
    y = int((screen_height - window_height) / 2)
    return x, y


class StartWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("E2EE Messaging - Start")
        x, y = get_center_position(self.winfo_screenwidth(), self.winfo_screenheight(), 300, 200)
        self.geometry(f"300x200+{x}+{y}")
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
        x, y = get_center_position(self.winfo_screenwidth(), self.winfo_screenheight(), 350, 250)
        self.geometry(f"350x250+{x}+{y}")
        self.configure(bg=COLOR_BG)

        # Initialize timer attributes
        self.timer_running = False
        self.time_left = 0

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
                                         text_color="black", hover_color=COLOR_BUTTON_HOVER,
                                         command=self.SendBySecureChannel)
        get_token_button.pack(pady=5)

        # Create Entry with placeholder
        self.token_entry = ctk.CTkEntry(self, textvariable=self.token_var,
                                        fg_color=COLOR_ENTRY, corner_radius=15,
                                        text_color=self.placeholder_color)
        self.token_entry.pack(pady=10)

        # Bind focus events
        self.token_entry.bind("<FocusIn>", self.clear_token_placeholder)
        self.token_entry.bind("<FocusOut>", self.add_token_placeholder)

        self.validate_token_button = ctk.CTkButton(self, text="Validate Token", fg_color=COLOR_BUTTON,
                                                   text_color="black",
                                                   hover_color=COLOR_BUTTON_HOVER, command=self.validate_token,
                                                   corner_radius=15)
        self.validate_token_button.pack(pady=5)

        # Timer label, used to display some text first, later will be timer
        self.timer_label = ctk.CTkLabel(self, text="Phone number should start with '5'", text_color="white",
                                        fg_color=COLOR_BG, corner_radius=15)
        self.timer_label.pack(pady=10)

        self.password_label = ctk.CTkLabel(self, text="Create Password:", text_color="white", fg_color=COLOR_BG,
                                           corner_radius=15)
        self.password_entry = ctk.CTkEntry(self, textvariable=self.password_var, fg_color=COLOR_ENTRY, show="*")
        self.set_pw_button = ctk.CTkButton(self, text="Set Password", fg_color=COLOR_BUTTON,
                                           hover_color=COLOR_BUTTON_HOVER, corner_radius=15, command=self.set_password)

    def update_timer(self):
        if self.time_left > 0:
            self.timer_label.configure(text=f"Time remaining: {self.time_left} seconds")
            self.time_left -= 1
            # Schedule the next update after 1 second
            self.after(1000, self.update_timer)
        else:
            # Timer expired
            self.timer_running = False
            self.token_entry.configure(state="disabled")
            self.validate_token_button.configure(state="disabled")
            self.timer_label.configure(text="Time expired! Request a new token.")

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

    def SendBySecureChannel(self):
        """
            Generate and store an authentication token and phone number as instance variables:
            - `self.stored_token`
            - `self.stored_phone`

            Ensures that the phone number entered is valid (starts with '5') and not already registered in the database.
            If valid, a token is generated and sent securely, and a timer for input is initiated.
        """
        phone = self.phone_var.get()
        self.token_entry.configure(state="normal")
        self.validate_token_button.configure(state="normal")
        if not phone.startswith("5") or len(phone) > 10 or not phone.isdigit():
            messagebox.showerror("Error", "Please enter a phone number starting with 5 and less then 11 digits.")
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

        if not self.timer_running:
            self.timer_running = True
            self.time_left = 30
            self.update_timer()

    def validate_token(self):
        """
        compare entered cardinals with the stored values, within time range
        """
        # If time is up, reject token validation
        if not self.timer_running and self.time_left == 0:
            messagebox.showerror("Error", "Token expired! Please request a new token.")
            return
        phone = self.phone_var.get()
        entered_token = self.token_var.get()

        # Check if we have a stored token and phone
        if self.stored_token is None or self.stored_phone is None:
            messagebox.showerror("Error", "No token generated. Please click 'Get Auth Token' first.")
            return

        # Compare entered token and phone to the stored ones
        if phone == self.stored_phone and entered_token == str(self.stored_token):
            messagebox.showinfo("Success", "Token validated. Please create your password.")
            self.geometry("350x320")
            self.password_label.pack(pady=5)
            self.password_entry.pack(pady=5)
            self.set_pw_button.pack(pady=5)
            self.timer_label.pack_forget()  # hide counter after validation of token
        else:
            messagebox.showerror("Error", "Invalid token.")

    def set_password(self):
        global log_str
        phone = self.phone_var.get()
        password = self.password_var.get()
        if password:
            # Register user in DB using DatabaseManager
            db = DatabaseManager()

            private_key_pem, public_key_pem = generate_rsa_key_pair()
            save_private_key(private_key_pem, phone)
            hashed_pw = hash_password_bcrypt(password)  # Hash password using bcrypt

            # Log password hashing
            log_str += f"\033[1mPassword for {phone} before hashing:\033[0m {password}\n" \
                       f"\033[1mHashed password:\033[0m {hashed_pw}\n"

            # Print RSA key pair and password to terminal
            str = f"\033[1mGenerated RSA key pair for phone: {phone}\033[0m\n" \
                  f"Private Key:\n{private_key_pem.decode()}\nPublic Key:\n{public_key_pem.decode()}\n"
            print(str)
            log_str += str

            # Note: hashed_pw is bytes. We'll store it as a string in the DB.
            db.add_user(user_phone=phone, public_key=public_key_pem, user_pw=hashed_pw.decode())
            messagebox.showinfo("Registered", "Registration successful! You can now login.")
            if log_str:
                print_encryption_steps(False)
            self.destroy()
            start_win = StartWindow()
            start_win.mainloop()
        else:
            messagebox.showerror("Error", "Please enter a password.")


class LoginWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("E2EE Messaging - Login")
        x, y = get_center_position(self.winfo_screenwidth(), self.winfo_screenheight(), 300, 200)
        self.geometry(f"300x200+{x}+{y}")
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
        user = db.get_user(phone)
        if not user:
            self.invalid_credentials()
            return

        stored_hashed_pw = user[2].encode()  # Convert back to bytes
        if verify_password_bcrypt(password, stored_hashed_pw):
            messagebox.showinfo("Login", "Login successful!")
            self.destroy()
            msg_window = MessagesWindow(phone)
            msg_window.mainloop()
        else:
            self.invalid_credentials()

    def invalid_credentials(self):
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
        x, y = get_center_position(self.winfo_screenwidth(), self.winfo_screenheight(), 600, 700)
        self.geometry(f"600x700+{x}+{y}")
        self.configure(bg=COLOR_BG)

        self.phone = phone

        title_label = ctk.CTkLabel(self, text="Your Messages", text_color="white",
                                   fg_color=COLOR_BG, corner_radius=15, font=("Arial", 20))
        title_label.pack(pady=10)

        # Frame for messages display
        self.messages_frame = ctk.CTkFrame(self, fg_color=COLOR_BG)
        self.scrollable_frame = self.create_scrollable_frame(self.messages_frame)
        self.messages_frame.pack(fill="both", expand=True, padx=20, pady=(20, 10))

        # Display messages initially
        self.display_messages()

        # ~~~~~~~~~~~~~~~~~~~~~~~~

        self.seen_noti_popup()

        # Frame for sending messages
        send_frame = ctk.CTkFrame(self, fg_color="#1C1C1C")
        send_frame.pack(fill="x", padx=20, pady=10)

        send_label = ctk.CTkLabel(send_frame, text="Send a New Message", text_color="white", fg_color="#1C1C1C",
                                  font=("Arial", 16))
        send_label.pack(pady=5, padx=5, anchor='w')

        # Recipient Entry
        recipient_label = ctk.CTkLabel(send_frame, text="Recipient Phone:", text_color="white", fg_color="#1C1C1C")
        recipient_label.pack(pady=5, padx=5, anchor='w')
        self.recipient_var = ctk.StringVar()
        recipient_entry = ctk.CTkEntry(send_frame, textvariable=self.recipient_var, text_color=COLOR_BG,
                                       fg_color=COLOR_ENTRY)
        recipient_entry.pack(pady=5, padx=5, anchor='w')

        # Subject Entry
        subject_label = ctk.CTkLabel(send_frame, text="Subject:", text_color="white", fg_color="#1C1C1C")
        subject_label.pack(pady=5, padx=5, anchor='w')
        self.subject_var = ctk.StringVar()
        subject_entry = ctk.CTkEntry(send_frame, textvariable=self.subject_var, text_color=COLOR_BG,
                                     fg_color=COLOR_ENTRY)
        subject_entry.pack(pady=5, padx=5, anchor='w')

        # Content Entry just single line for simplicity
        content_label = ctk.CTkLabel(send_frame, text="Content:", text_color="white", fg_color="#1C1C1C")
        content_label.pack(pady=5, padx=5, anchor='w')
        self.content_var = ctk.StringVar()
        content_entry = ctk.CTkEntry(send_frame, textvariable=self.content_var, fg_color=COLOR_ENTRY,
                                     text_color=COLOR_BG, width=400)
        content_entry.pack(pady=5, padx=5, anchor='w')

        send_button = ctk.CTkButton(send_frame, text="Send Message", fg_color=COLOR_BUTTON,
                                    hover_color=COLOR_BUTTON_HOVER, text_color="black", command=self.send_message)
        send_button.pack(pady=10, padx=5, anchor='w')

        # Logout/Back button at the bottom
        back_button = ctk.CTkButton(self, text="Logout", fg_color=COLOR_BUTTON,
                                    hover_color=COLOR_BUTTON_HOVER, command=self.back_to_start)
        back_button.pack(pady=10, padx=5, anchor='e')

    def seen_noti_popup(self):
        db = DatabaseManager()
        send_messages = db.seen_notification_sender(
            self.phone)  # This returns a list of (message_index, recipient_phone)

        for message_index, recipient_phone in send_messages:  # Unpack message_index and recipient_phone
            print(f"Message Index: {message_index}, Recipient Phone: {recipient_phone}")
            messagebox.showinfo(title="Message was read!", message=f"Message to {recipient_phone} was read")

    def display_messages(self):
        global log_str
        # Clear existing widgets in the scrollable frame
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        db = DatabaseManager()
        messages = db.fetch_messages_for_user(self.phone)
        for msg in messages:
            sender, self.phone, enc_aes_key, nonce, ciphertext, date, received_flag = msg

            # Print the AES key, nonce, and ciphertext before decryption
            str = f"\033[1mAES key, nonce, and ciphertext before decryption:\033[0m\n" \
                  f"Encrypted AES key: {enc_aes_key} \nNonce: {nonce} \nCiphertext: {ciphertext}\n"
            print(str)
            log_str += str

            # Decrypt AES key using our private key
            aes_key = rsa_decrypt_aes_key(enc_aes_key, self.phone)

            # Decrypt message
            plaintext_bytes = decrypt_message_with_aes(aes_key, nonce, ciphertext)
            content = plaintext_bytes.decode('utf-8')

            # Print the AES key, nonce, and ciphertext after decryption
            str = f"\033[1mAES key, nonce, and ciphertext after decryption:\033[0m" \
                  f"\nDecrypted AES key: {aes_key}\nNonce: {nonce}\nSubject: {content}\n"
            print(str)
            log_str += str

            # Display as before
            # Create a frame INSIDE the scrollable frame
            msg_frame = ctk.CTkFrame(self.scrollable_frame, fg_color="#1C1C1C")
            msg_frame.pack(fill="x", pady=5, padx=5)

            sender_label = ctk.CTkLabel(msg_frame, text=f"From: {sender}", text_color=TEXT_COLOR, fg_color="#1C1C1C",
                                        anchor="w")
            sender_label.pack(fill="x", padx=5)

            date_label = ctk.CTkLabel(msg_frame, text=f"Date: {date}", text_color=COLOR_ENTRY, fg_color="#1C1C1C",
                                      anchor="w")
            date_label.pack(fill="x", padx=5)
            content_label = ctk.CTkLabel(msg_frame, text=f"Subject: {content}", text_color=TEXT_COLOR,
                                         fg_color="#1C1C1C",
                                         anchor="w")
            content_label.pack(fill="x", padx=5)

            # Print the encryption steps
            if log_str:
                print_encryption_steps(True)

    def send_message(self):
        global log_str
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
        plain_text = subject + "\nContent: " + content
        print(f"Subject is {subject}, content is {content}")
        recipient_public_key_pem = db.get_user_public_key(recipient)
        aes_key = os.urandom(32)  # for aes-256

        # Print the AES key and message before encryption
        str = f"\033[1mAES key and message before encryption:\033[0m\n" \
              f"Generated AES key: {aes_key}\nSubject: {plain_text}"
        print(str)
        log_str += str

        nonce, ciphertext = encrypt_message_with_aes(aes_key, plain_text)
        enc_aes_key = rsa_encrypt_aes_key(aes_key, recipient_public_key_pem)

        # Print the AES key, nonce, and ciphertext before sending after encryption
        str = f"\n\033[1mAES key, nonce, and ciphertext before sending after encryption:\033[0m\n" \
              f"Encrypted AES key: {enc_aes_key}\nNonce: {nonce}\nCiphertext: {ciphertext}\n"
        print(str)
        log_str += str

        try:
            if enc_aes_key is None:
                return None
            db.add_message(sender_num=self.phone, recipient_num=recipient, encrypted_aes_key=enc_aes_key,
                           ciphertext=ciphertext, iv=nonce)
            messagebox.showinfo("Success", "Message sent successfully!")
            # Optionally refresh the message list. If the user sends a message to themselves, they will see it.
            self.display_messages()

            # Clear the fields after sending
            self.recipient_var.set("")
            self.subject_var.set("")
            self.content_var.set("")
            if log_str:
                print_encryption_steps(True)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to send message: {e}")
            return None

    def create_scrollable_frame(self, parent):
        """
        Creates a scrollable frame inside 'parent' using CTkScrollableFrame.
        """
        scrollable_frame = ctk.CTkScrollableFrame(parent, label_text="")
        scrollable_frame.pack(fill="both", expand=True, padx=10, pady=10)
        return scrollable_frame

    def back_to_start(self):
        self.destroy()
        start_win = StartWindow()
        start_win.mainloop()
