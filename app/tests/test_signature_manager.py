from django.contrib.auth.models import User
from django.test import TestCase

from app.models import Transaction, Account, Blockchain, KeyPair
from app.signatures import SignatureManager
from app.transactions import TransactionManager


def set_up():
    Blockchain.objects.create()
    balance = 10
    amount = 1
    sender_username = 'sender'
    sender = User.objects.create_user(username=sender_username, password="sender")
    recipient = User.objects.create_user(username="recipient", password="recipient")
    sender_acc = Account.objects.get(user=sender)
    recipient_acc = Account.objects.get(user=recipient)
    TransactionManager.replenish(sender_acc, balance, TransactionManager._admin_credentials)
    transaction = TransactionManager.transfer(sender_acc, recipient_acc, amount)
    return transaction


class VerifyTransactionWithCorrectDataTestCase(TestCase):
    def setUp(self):
        self.transaction = set_up()

    def test_verifying_transaction_with_correct_date(self):
        signature = self.transaction.signature
        public_key = self.transaction.sender.key_pair.import_public_key()
        self.assertTrue(SignatureManager.verify(signature, public_key, self.transaction))


class VerifyTransactionWithFakeSignatureTestCase(TestCase):
    def setUp(self):
        self.transaction = set_up()
        self.fake_key_pair = KeyPair.objects.create()

    def test_verifying_transaction_with_fake_signature(self):
        signature = SignatureManager.sign(self.fake_key_pair.import_private_key(), self.transaction)
        public_key = self.transaction.sender.key_pair.import_public_key()
        self.assertFalse(SignatureManager.verify(signature, public_key, self.transaction))


class VerifyTransactionWithFakePublicKey(TestCase):
    def setUp(self):
        self.transaction = set_up()
        self.fake_key_pair = KeyPair.objects.create()

    def test_verifying_transaction_with_fake_public_key(self):
        signature = self.transaction.signature
        public_key = self.fake_key_pair.import_public_key()
        self.assertFalse(SignatureManager.verify(signature, public_key, self.transaction))


class VerifyTransactionWithFakeTransaction(TestCase):
    def setUp(self):
        self.transaction = set_up()
        fake_sender = User.objects.create_user(username="fake_sender", password="fake_sender")
        self.fake_sender_account = Account.objects.get(user=fake_sender)

    def test_verifying_transaction_with_fake_transaction(self):
        signature = self.transaction.signature
        public_key = self.transaction.sender.key_pair.import_public_key()
        self.transaction.sender = self.fake_sender_account
        self.assertFalse(SignatureManager.verify(signature, public_key, self.transaction))

