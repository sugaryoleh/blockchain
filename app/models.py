from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from django.contrib.auth.models import User
from Crypto.PublicKey.RSA import RsaKey
from Crypto.PublicKey import RSA
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils import timezone

from app.hashing import _hash
from app.signatures import SignatureManager


class Blockchain(models.Model):
    difficulty = models.IntegerField(blank=False, null=False, editable=False, default=4)
    total = models.IntegerField(blank=False, null=False, editable=False, default=0)

    def save(self, *args, **kwargs):
        if Blockchain.objects.exists() and not self.pk:
            return Blockchain.objects.first()
        super(Blockchain, self).save(*args, **kwargs)


class KeyPair(models.Model):
    public_key = models.BinaryField()
    private_key = models.BinaryField()

    def save(self, *args, **kwargs):
        private_key, public_key = self.generate_keys()
        private_key, public_key = self.export_keys(private_key=private_key, public_key=public_key)
        self.private_key = private_key
        self.public_key = public_key
        super(KeyPair, self).save(*args, **kwargs)

    @staticmethod
    def generate_keys() -> tuple[private_key: RsaKey, public_key: RsaKey]:
        key = RSA.generate(2048)
        return key, key.public_key()

    @staticmethod
    def export_keys(private_key: RsaKey, public_key: RsaKey) -> tuple[private_key: bytes, public_key: bytes]:
        return private_key.exportKey(), public_key.exportKey()

    def import_keys(self) -> tuple[private_key: RsaKey, public_key: RsaKey]:
        private_key = RSA.importKey(self.private_key)
        public_key = RSA.importKey(self.public_key)
        return private_key, public_key

    def import_private_key(self) -> RsaKey:
        return RSA.importKey(self.private_key)

    def import_public_key(self) -> RsaKey:
        return RSA.importKey(self.public_key)


class Account(models.Model):
    user = models.OneToOneField(to=User, on_delete=models.CASCADE, related_name='user')
    balance = models.IntegerField(null=False, blank=False, default=0)
    key_pair = models.OneToOneField(to=KeyPair, on_delete=models.CASCADE, related_name='keys')
    phone = PhoneNumberField(null=False, blank=False, unique=False)
    sms_notifications = models.BooleanField(default=False)
    profile_image = models.ImageField(null=True, blank=True, upload_to="images/")

    def __str__(self):
        return '{}'.format(self.user)

    def receive(self, amount):
        self.balance = int(self.balance) + amount
        self.save()

    def send(self, amount):
        self.balance = int(self.balance) - amount
        self.save()


@receiver(post_save, sender=User)
def create_account(sender, instance, created, **kwargs):
    if created:
        key_pair = KeyPair.objects.create()
        Account.objects.create(user=instance, balance=0, key_pair=key_pair)


@receiver(post_delete, sender=Account)
def delete_account(sender, instance, **kwargs):
    instance.key_pair.delete()


class Transaction(models.Model):
    sender = models.ForeignKey(to=Account, on_delete=models.PROTECT, related_name='sender_account',
                               blank=False, null=False)
    recipient = models.ForeignKey(to=Account, on_delete=models.PROTECT, related_name='recipient_account', blank=False, null=False)
    amount = models.IntegerField(blank=False, null=False, default=0)
    timestamp = models.DateTimeField(editable=False, blank=False, null=False)
    signature = models.BinaryField()

    def save(self, *args, **kwargs):
        if not self.id:
            self.timestamp = timezone.now()
            key_pair = self.sender.key_pair
            private_key = key_pair.import_private_key()
            self.signature = SignatureManager.sign(private_key=private_key, transaction=self)
        return super(Transaction, self).save(*args, **kwargs)

    def __repr__(self):
        return "{} --> {} [{}] @ {}".format(self.sender, self.recipient, self.amount, self.timestamp)

    def collect_hash_data(self) -> dict:
        return {
            'sender': self.sender.__str__(),
            'recipient': self.recipient.__str__(),
            'amount': self.amount.__str__(),
            'timestamp': self.timestamp.__str__(),
        }


class Block(models.Model):
    index = models.BigAutoField(primary_key=True)
    transaction = models.OneToOneField(to=Transaction, on_delete=models.PROTECT)
    previous_hash = models.CharField(max_length=5000)
    nonce = models.PositiveIntegerField()

    def hash(self):
        return _hash(self.transaction.__repr__(), self.nonce)


@receiver(post_save, sender=Transaction)
def mine(sender, instance, created, **kwargs):
    if created:
        difficulty = Blockchain.objects.first().difficulty
        block = Block(transaction=instance, nonce=0)
        try:
            last_block = Block.objects.order_by("pk").reverse()[0]
            block.previous_hash = last_block.hash()
        except IndexError:
            block.previous_hash = '0' * 64

        while True:
            if block.hash()[:difficulty] == '0' * difficulty:
                block.save()
                break
            else:
                block.nonce += 1
