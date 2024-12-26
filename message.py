from datetime import datetime


class Message:
    """
    represent a single message
    """

    def __init__ (self, sender_num, recipient_num, encrypted_aes_key, ciphertext, iv, date, received_flag):
        self.sender_num = int(sender_num)
        self.recipient_num = int(recipient_num)
        self.encrypted_aes_key = encrypted_aes_key
        self.ciphertext = ciphertext 
        self.date = date # timestamp using date class
        self.iv = iv # used later in encryption
        self.received_flag = received_flag # if the message reached the user either online or not, equals true
