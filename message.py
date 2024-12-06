from datetime import datetime


class Message:
    """
    represent a single message
    """

    def __init__(self, sender_id, recipient_id, subject, content, date, blue_v):

        # validate numbers, will get 54 along with 054, cant check 05X because octal base
        # I can add this line if really want to check for 05, and str(sender_id).startswith("05")
        if not (isinstance(sender_id, int) and 500000000 <= sender_id <= 599999999):
            raise ValueError("sender_id must be a positive 10-digit number starting with '05'")
        if not (isinstance(recipient_id, int) and 500000000 <= recipient_id <= 599999999):
            raise ValueError("recipient_id must be a positive 10-digit number starting with '05'")

        # for value, name in [(sender_id, "sender_id"), (recipient_id, "recipient_id")]:
        #     if not (isinstance(value, int) and 500000000 <= value <= 599999999):
        #         raise ValueError(f"{name} must be a positive 10-digit number starting with '05'")
        # its do the same, but does it looks better ?

        self.sender_id = int(sender_id)
        self.recipient_id = int(recipient_id)
        self.subject = subject
        self.content = content or ""  # can send only subject
        self.date = datetime.now()
        self.blue_v = False
