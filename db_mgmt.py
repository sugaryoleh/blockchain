import xlrd
from app.models import *
from app.transactions import TransactionManager

_default_accounts_number = 4
_max_accounts_number = 20
_min_accounts_number = 2
_default_transaction_equivalent = 5
_max_default_transaction_equivalent = 20
_min_default_transaction_equivalent = 1
_extra_balance = 500
_nominal_balance = _max_accounts_number + _extra_balance
_transaction_amount = 1

BRUTE_FORCE_MODE = "BRUTE_FORCE_MODE"
BY_EQUIVALENCY = "BY_EQUIVALENCY"


def _clean_blockchain() -> None:
    bc = Blockchain.objects.first()
    bc.total = 0
    bc.save()


def clean_db() -> None:
    Block.objects.all().delete()
    Transaction.objects.all().delete()
    Account.objects.all().delete()
    KeyPair.objects.all().delete()
    User.objects.exclude(username="admin").delete()
    _clean_blockchain()


def _check_transaction_data(accounts_numer: int = _default_accounts_number,
                            transaction_equivalent: int = _default_transaction_equivalent):
    if accounts_numer < _min_accounts_number:
        raise Exception("Min number of users is {}".format(_min_accounts_number))

    if accounts_numer > _max_accounts_number:
        raise Exception("Max number of users is {}".format(_max_accounts_number))

    if transaction_equivalent < _min_default_transaction_equivalent:
        raise Exception("Min number of users is {}".format(_min_default_transaction_equivalent))

    if transaction_equivalent > _max_default_transaction_equivalent:
        raise Exception("Max number of users is {}".format(_max_default_transaction_equivalent))


def _import_account_data(file_name: str = "account_data.xlsx"):
    """
    Importing file must have .xlsx extension
    First row is header, which is skipped
    Must contain 3 columns: user first name, last name and email
    """
    workbook = xlrd.open_workbook(file_name)
    worksheet = workbook.sheet_by_index(0)
    users = []
    for i in range(1, 5):
        user = {
            'first_name': worksheet.cell_value(i, 0),
            'last_name': worksheet.cell_value(i, 1),
            'email': worksheet.cell_value(i, 2),
            'phone': worksheet.cell_value(i, 3)
        }
        users.append(user)
    return users


def _generate_password(account_info: dict) -> str:
    password = account_info['first_name'][0] + account_info['last_name']
    return password


def _generate_username(account_info: dict) -> str:
    username = account_info['first_name'][0] + account_info['last_name']
    return username


def _populate_accounts(accounts_number: int, nominal_balance: int, log: bool = True):
    account_data = _import_account_data()
    for i in range(0, accounts_number):
        user = User.objects.create_user(username=_generate_username(account_data[i]),
                                        password=_generate_password(account_data[i]),
                                        first_name=account_data[i]['first_name'],
                                        last_name=account_data[i]['last_name'],
                                        email=account_data[i]['email'])
        account = Account.objects.get(user=user)
        account.phone = account_data[i]['phone']
        account.save()
        TransactionManager.replenish(account, nominal_balance, TransactionManager._admin_credentials)
        if log:
            print("User {} created".format(user))
            print("Account {} created".format(account))
            print("Keys for {} generated".format(account))


def _populate_transactions_brute_force(log: bool):
    accounts = Account.objects.all()
    for sender in accounts:
        for recipient in accounts:
            actual_sender = Account.objects.get(user=sender.user)   # refreshing sender object as object in db was affected
            actual_recipient = Account.objects.get(user=recipient.user) # refreshing recipient object as object in db was affected
            if not sender == recipient:
                transaction = TransactionManager.transfer(actual_sender, actual_recipient, _transaction_amount)
                if log:
                    print(transaction.__repr__())


def _populate_transactions_by_equivalency(transaction_equivalent, log):
    raise NotImplemented("Use brute force mode ")


def _populate_transactions(transaction_population_mode, transaction_equivalent, log):
    if transaction_population_mode == BRUTE_FORCE_MODE:
        _populate_transactions_brute_force(log)
    elif transaction_population_mode == BY_EQUIVALENCY:
        _populate_transactions_by_equivalency(transaction_equivalent, log)
    else:
        raise Exception("Please user BRUTE_FORCE_MODE or BY_EQUIVALENCY to populate transactions table")


def _populate(accounts, nominal_balance, transaction_population_mode, transaction_equivalent, log):
    _populate_accounts(accounts, nominal_balance, log)
    _populate_transactions(transaction_population_mode, transaction_equivalent, log)


def repopulate(accounts_number=_default_accounts_number,
               nominal_balance=_nominal_balance,
               transaction_population_mode=BRUTE_FORCE_MODE,
               transaction_equivalent=_default_transaction_equivalent,
               log=True):
    _check_transaction_data(accounts_number, transaction_equivalent)
    clean_db()
    try:
        _populate(_default_accounts_number, nominal_balance, transaction_population_mode, transaction_equivalent, log)
    except Exception as e:
        print("Next error occured:\n", e, "\nCleaning database")
        clean_db()

