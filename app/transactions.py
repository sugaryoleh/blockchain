from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist

from .blockchain import BlockchainManager
from .models import Transaction, Account, Blockchain


class TransactionManager:
    _admin_credentials = '123'

    @staticmethod
    def _are_funds_sufficient(sender_balance: float, amount: float) -> bool:
        if sender_balance < amount:
            return False

        return True

    @staticmethod
    def _user_exists(recipient: str) -> bool:
        try:
            User.objects.get(username=recipient)
            return True
        except ObjectDoesNotExist:
            return False

    @staticmethod
    def _is_self_transfer(sender: Account, recipient: Account) -> bool:
        if sender == recipient:
            return True
        return False

    @staticmethod
    def _is_amount_greater_than_0(amount: float) -> bool:
        if amount == 0:
            return False
        return True

    @staticmethod
    def _create_transaction(sender: Account, recipient: Account, amount: float) -> Transaction:
        return Transaction.objects.create(sender=sender, recipient=recipient, amount=amount)

    @staticmethod
    def _perform_transaction(transaction: Transaction) -> None:
        transaction.sender.send(transaction.amount)
        transaction.recipient.receive(transaction.amount)

    @staticmethod
    def transfer(sender: Account, recipient: str, amount) -> Transaction:
        if not TransactionManager._user_exists(recipient):
            raise Exception("Recipient does not exist")
        if not TransactionManager._is_amount_greater_than_0(float(amount)):
            raise Exception("Amount must be greater than 0")
        if not TransactionManager._are_funds_sufficient(float(sender.balance), amount):
            raise Exception("Insufficient funds")

        recipient_user = User.objects.get(username=recipient)
        recipient_account = Account.objects.get(user=recipient_user)

        if TransactionManager._is_self_transfer(sender, recipient_account):
            raise Exception("Cannot transfer money to yourself")

        transaction = TransactionManager._create_transaction(sender, recipient_account, amount)
        TransactionManager._perform_transaction(transaction)

        print(BlockchainManager.check_sum())

        return transaction

    # @staticmethod
    # def is_authorized(credentials: dict) -> bool:
    #     if credentials["card number"] == "1111 2222 3333 4444" and credentials["date"] == "11/23" and credentials["CVV"] == "123":
    #         return True
    #
    #     return False

    @staticmethod
    def _is_authorized(credentials: str) -> bool:
        if credentials == TransactionManager._admin_credentials:
            return True

        return False

    @staticmethod
    def replenish(account, amount, credentials) -> None:
        if not TransactionManager._is_amount_greater_than_0(amount):
            raise Exception("Amount must be greater than 0")
        elif TransactionManager._is_authorized(credentials):
            bc = Blockchain.objects.first()
            bc.total = float(bc.total) + amount
            bc.save()
            account.receive(amount)

            print(BlockchainManager.check_sum())

        else:
            raise Exception("Oops. something went wrong. Please check card info or make sure you have enough funds.")

