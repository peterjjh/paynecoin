"""Test overspending prevention in the blockchain"""

from blockchain import Blockchain
from utils import (
    generate_keys,
    create_transaction,
    public_key_to_string,
)


def test_overspending():
    # Generate keys for Alice and Bob
    alice_private, alice_public = generate_keys()
    bob_private, bob_public = generate_keys()
    
    # Convert public keys to strings for transactions
    alice_pub_str = public_key_to_string(alice_public)
    bob_pub_str = public_key_to_string(bob_public)
    
    # Genesis transaction: Alice starts with 100 tokens
    tx0 = create_transaction(
        private_key=alice_private,
        public_key=alice_pub_str,
        receiver=alice_pub_str,
        amount=100,
    )
    
    # Create blockchain with genesis
    ledger = Blockchain(starting_transactions=[tx0])
    print("\nInitial state:")
    print(f"Alice's balance: {ledger.get_balances().get(alice_pub_str, 0)}")
    print(f"Chain valid: {ledger.valid_chain(ledger.chain)}")
    
    # First try immediate prevention: attempt to add transaction that exceeds balance
    print("\nTrying to add transaction spending 150 tokens (more than Alice's 100)...")
    overspend_tx = create_transaction(
        private_key=alice_private,
        public_key=alice_pub_str,
        receiver=bob_pub_str,
        amount=150,
    )
    
    try:
        ledger.add_transaction(overspend_tx)
        print("WARNING: Overspending transaction was accepted!")
    except ValueError as e:
        print(f"Transaction rejected as expected: {str(e)}")
    
    # Now try to bypass add_transaction() by directly modifying the chain
    print("\nTrying to bypass by directly adding a block with overspending...")
    
    # First add a valid transaction: Alice sends 50 to Bob
    valid_tx = create_transaction(
        private_key=alice_private,
        public_key=alice_pub_str,
        receiver=bob_pub_str,
        amount=50,
    )
    ledger.add_transaction(valid_tx)
    ledger.new_block(previous_hash=Blockchain.hash(ledger.chain[-1]))
    
    # Now create an invalid block where Alice tries to send 80 more tokens
    # (she only has 50 left but tries to send 80)
    overspend_tx2 = create_transaction(
        private_key=alice_private,
        public_key=alice_pub_str,
        receiver=bob_pub_str,
        amount=80,
    )
    
    # Manually add the block to bypass add_transaction checks
    block = {
        "nonce": 0,
        "index": len(ledger.chain),
        "timestamp": 123456789,
        "transactions": [overspend_tx2],
        "previous_hash": Blockchain.hash(ledger.chain[-1])
    }
    ledger.chain.append(block)
    
    print("\nFinal state:")
    print("Block 0 (genesis): Alice gets 100 tokens")
    print("Block 1: Alice sends 50 to Bob (valid)")
    print("Block 2: Alice tries to send 80 to Bob (invalid - not enough funds)")
    print(f"\nExpected balances if overspending was allowed:")
    print(f"Alice: 100 - 50 - 80 = -30 tokens")
    print(f"Bob: 0 + 50 + 80 = 130 tokens")
    
    print(f"\nChain valid: {ledger.valid_chain(ledger.chain)}")
    print("\nWhy invalid? valid_chain() checks that all balances remain >= 0")
    print("The overspending in block 2 would make Alice's balance negative")


if __name__ == "__main__":
    test_overspending()