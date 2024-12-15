from datetime import datetime


class Message:
    """
    represent a single message
    """

    def __init__ (self, sender_num, recipient_num, encrypted_aes_key, ciphertext, iv, date, blue_v):
         

        self.sender_num = int(sender_num)
        self.recipient_num = int(recipient_num)
        self.encrypted_aes_key = encrypted_aes_key
        self.ciphertext = ciphertext 
        self.date = date
        self.iv = iv
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
