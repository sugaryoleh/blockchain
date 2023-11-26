from twilio.rest import Client


class SMSManager:
    _instance = None

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(SMSManager, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        self.account_sid = 'ACcad6965fda69b920669963d3d01e6831'
        self.auth_token = '7d768a3c3dec8752386255af069c8aba'
        self.client = Client(self.account_sid, self.auth_token)

    def send_message(self, text: str, to: str) -> None:
        # message = self.client.messages.create(
        #     from_='+12676139604',
        #     body=text,
        #     to=to
        # )
        print("{} sent to {}".format(text, '+380502265769'))

    def create_new_account_message(self, account) -> None:
        message = "Welcome {}! Your account has been successfully created!".format(account.user.username)
        self.send_message(message, str(account.phone))

    def transfer_message(self, transaction) -> None:
        message = "Your received {} tokens from {}".format(transaction.amount, transaction.sender.user.username)
        self.send_message(message, str(transaction.recipient.phone))

    def replenish_message(self, account, amount) -> None:
        message = "{}, you successfully replenished account for {} tokens".format(account.user.username, amount)
        self.send_message(message, str(account.phone))
