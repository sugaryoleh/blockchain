from .models import Blockchain, Block, Transaction, Account


class BlockchainManager:

    @staticmethod
    def is_blockchain_valid(chain: list) -> bool:
        difficulty = Blockchain.objects.first().difficulty
        for i in range(1, len(chain)):
            _previous = chain[i].previous_hash
            _current = chain[i-1].hash()
            if _previous != _current:
                return False
            elif _current[:difficulty] != '0' * difficulty:
                return False
            return True

    @staticmethod
    def check_sum() -> bool:
        accounts = Account.objects.all()
        balance = 0
        for obj in accounts:
            balance += obj.balance

        if balance != Blockchain.objects.first().total:
            return False

        return True


