from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist

from .models import Transaction, Account, Blockchain


class TransactionManager:

    @staticmethod
    def are_funds_sufficient(sender_balance: float, amount: float) -> bool:
        if sender_balance < amount:
            return False

        return True

    @staticmethod
    def create_transaction(sender: Account, recipient: Account, amount: float) -> Transaction:
        return Transaction.objects.create(sender=sender, recipient=recipient, amount=amount)

    @staticmethod
    def perform_transaction(transaction) -> None:
        transaction.sender.send(transaction.amount)
        transaction.recipient.receive(transaction.amount)

    @staticmethod
    def user_exists(recipient: str) -> bool:
        try:
            User.objects.get(username=recipient)
            return True
        except ObjectDoesNotExist:
            return False

    @staticmethod
    def transfer(sender: Account, recipient: str, amount):
        if not TransactionManager.user_exists(recipient):
            raise Exception("Recipient does not exist")
        if not TransactionManager.are_funds_sufficient(float(sender.balance), amount):
            raise Exception("Insufficient funds")

        recipient_user = User.objects.get(username=recipient)
        recipient_account = Account.objects.get(user=recipient_user)
        transaction = TransactionManager.create_transaction(sender, recipient_account, amount)
        TransactionManager.perform_transaction(transaction)


    # @staticmethod
    # def is_authorized(credentials: dict) -> bool:
    #     if credentials["card number"] == "1111 2222 3333 4444" and credentials["date"] == "11/23" and credentials["CVV"] == "123":
    #         return True
    #
    #     return False

    @staticmethod
    def is_authorized(credentials: str) -> bool:
        if credentials == '123':
            return True

        return False

    @staticmethod
    def top_up(account, amount, credentials) -> None:
        if TransactionManager.is_authorized(credentials):
            bc = Blockchain.objects.first()
            bc.total = float(bc.total) + amount

            account.receive(amount)

