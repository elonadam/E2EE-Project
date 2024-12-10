from datetime import datetime


class Message:
    """
    represent a single message
    """

    def __init__(self, sender_id, recipient_id, subject, content, date, blue_v):

        self.sender_id = int(sender_id)
        self.recipient_id = int(recipient_id)
        self.subject = subject
        self.content = content or ""  # can send only subject
        self.date = ""
        self.blue_v = False
