from Crypto.Hash import SHA256
from Crypto.Signature import PKCS1_v1_5
from Crypto.PublicKey.RSA import RsaKey
import json as _json
import hashlib as _hashlib


class SignatureManager:
    @staticmethod
    def hash(obj):
        hash_data = obj.collect_hash_data()
        encoded_transaction = _json.dumps(hash_data, sort_keys=True).encode()
        return _hashlib.sha256(encoded_transaction).hexdigest()

    @staticmethod
    def sign(private_key: RsaKey, transaction) -> bytes:
        digest = SHA256.new()
        digest.update(SignatureManager.hash(transaction).encode('utf-8'))
        signer = PKCS1_v1_5.new(private_key)
        signature = signer.sign(digest)
        return signature

    @staticmethod
    def verify(signature: bytes, public_key: RsaKey, transaction):
        digest = SHA256.new()
        digest.update(SignatureManager.hash(transaction).encode('utf-8'))
        verifier = PKCS1_v1_5.new(public_key)
        verified = verifier.verify(digest, signature)
        return verified
