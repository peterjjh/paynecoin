"""Test what happens when someone tries to spend someone else's tokens fraudulently"""

from blockchain import Blockchain
from utils import (
    generate_keys,
    create_transaction,
    is_from_sender,
    public_key_to_string,
)

def test_fraudulent_spend():
    # Generate keys for Alice and Bob
    alice_private, alice_public = generate_keys()
    bob_private, bob_public = generate_keys()
    
    # Create genesis transaction giving Alice 100 tokens
    tx0 = create_transaction(
        private_key=alice_private,
        public_key=public_key_to_string(alice_public),
        receiver=public_key_to_string(alice_public),
        amount=100,
    )
    
    # Initialize blockchain 
    ledger = Blockchain(starting_transactions=[tx0])
    
    # Bob tries to spend Alice's tokens by using her public key as sender
    # but signing with his private key (which won't work)
    fraudulent_tx = create_transaction(
        private_key=bob_private,  # Bob's private key
        public_key=public_key_to_string(alice_public),  # Pretending to be Alice
        receiver=public_key_to_string(bob_public),
        amount=50,
    )
    
    # Check if transaction passes signature verification
    is_valid = is_from_sender(fraudulent_tx)
    print(f"Fraudulent transaction passes signature check: {is_valid}")
    
    # Try to add it to blockchain (should raise error)
    try:
        ledger.add_transaction(fraudulent_tx)
        print("WARNING: Fraudulent transaction was accepted!")
    except Exception as e:
        print(f"Fraudulent transaction was rejected as expected: {str(e)}")

if __name__ == "__main__":
    test_fraudulent_spend()