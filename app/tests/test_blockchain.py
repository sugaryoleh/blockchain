from django.test import TestCase

import db_mgmt
from ..blockchain import BlockchainManager
from ..models import Block, Blockchain, Transaction, Account
from ..transactions import TransactionManager


def set_up():
    Blockchain.objects.create()
    db_mgmt.repopulate(log=False)


class IsBlockchainValidWithCorrectDataTestCase(TestCase):
    def setUp(self):
        set_up()

    def test_is_block_chain_valid_with_correct_data(self):
        bc = list(Block.objects.all())
        self.assertTrue(BlockchainManager.is_blockchain_valid(bc))


class IsBlockchainValidWithReplacedTransactionTestCase(TestCase):
    def setUp(self):
        set_up()

    def test_is_block_chain_valid_with_replaced_transaction(self):
        fake_transaction = Transaction.objects.first()
        fake_transaction.amount = fake_transaction.amount + 1
        bc = list(Block.objects.all())
        bc[0].transaction = fake_transaction
        self.assertFalse(BlockchainManager.is_blockchain_valid(bc))


class IsBlockchainTotalValidAfterPopulatingTestCase(TestCase):
    def setUp(self):
        set_up()

    def test_blockchain_total(self):
        target = db_mgmt._default_accounts_number*(db_mgmt._max_accounts_number+db_mgmt._extra_balance)
        actual = Blockchain.objects.first().total
        self.assertEqual(actual, target)


class IsBlockchainTotalValidAfterReplenishTestCase(TestCase):
    def setUp(self):
        set_up()

    def test_blockchain_total(self):
        account = Account.objects.first()
        replenish_amount = 5
        target = Blockchain.objects.first().total + replenish_amount
        TransactionManager.replenish(account, replenish_amount, TransactionManager._admin_credentials)
        actual = Blockchain.objects.first().total
        self.assertEqual(actual, target)

