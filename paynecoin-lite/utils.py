import json
from time import time
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives import serialization
from cryptography.exceptions import InvalidSignature


# public/private key generation
def generate_keys():
    """Generate a public/private key pair.py

    Note that these keys are instances of specific python classes"""
    private_key = Ed25519PrivateKey.generate()
    public_key = private_key.public_key()
    return private_key, public_key


def private_key_to_string(private_key):
    """Convert a private key to a string"""
    return private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    ).decode("latin1")


def public_key_to_string(public_key):
    """Convert a public key to a string"""
    return public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    ).decode("latin1")


def string_to_public_key(public_key_string):
    """Convert a string to a public key"""
    return serialization.load_pem_public_key(public_key_string.encode("latin1"))


def create_transaction(
    private_key, public_key: str, receiver: str, amount: int
) -> dict:
    """
    Creates a transaction from a sender's public key to a receiver's public key

    In essence, adds a timestamp and signature to a transaction
    :param private_key: The Sender's private key
    :param public_key: The Sender's public key, as a string
    :param receiver: The Receiver's public key, as a string
    :param amount: The amount in tokens
    :return: <dict> The transaction dict
    """

    tx = {
        "sender": public_key,
        "receiver": receiver,
        "amount": amount,
        "timestamp": int(time()),
    }

    # Create a canonical message for signing (exclude signature)
    message = json.dumps(
        {
            "sender": tx["sender"],
            "receiver": tx["receiver"],
            "amount": tx["amount"],
            "timestamp": tx["timestamp"],
        },
        sort_keys=True,
    ).encode()

    # Sign the message with the sender's private key (Ed25519)
    signature_bytes = private_key.sign(message)

    # Store signature as hex string for easy serialization
    tx["signature"] = signature_bytes.hex()

    return tx


def is_from_sender(tx: dict) -> bool:
    """
    Verifies that a given transaction was sent from the sender
    :param tx: The transaction dict
    :return: <bool>
    """

    # Verify signature exists
    sig_hex = tx.get("signature")
    if not sig_hex:
        return False

    try:
        signature = bytes.fromhex(sig_hex)
    except Exception:
        return False

    # Recreate the canonical message that was signed
    try:
        message = json.dumps(
            {
                "sender": tx["sender"],
                "receiver": tx["receiver"],
                "amount": tx["amount"],
                "timestamp": tx["timestamp"],
            },
            sort_keys=True,
        ).encode()
    except Exception:
        return False

    # Load the public key object and verify signature
    try:
        public_key_obj = string_to_public_key(tx["sender"])
        public_key_obj.verify(signature, message)
        return True
    except InvalidSignature:
        return False
    except Exception:
        return False
