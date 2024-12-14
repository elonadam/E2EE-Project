from datetime import datetime


class Message:
    """
    represent a single message
    """

    def __init__(self, sender_phone, recipient_phone, subject, content, date, blue_v):

        self.sender_phone = int(sender_phone)
        self.recipient_phone = int(recipient_phone)
        self.subject = subject
        self.content = content or ""  # can send only subject
        self.date = ""
        self.blue_v = False
        """
                message_index INTEGER PRIMARY KEY AUTOINCREMENT,
                sender_phone INTEGER,
                recipient_phone INTEGER,
                encrypted_aes_key TEXT,
                ciphertext TEXT,
                iv TEXT,
                date TEXT,
                blue_v BOOLEAN
        """
