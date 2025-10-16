"""Test blockchain immutability by attempting to modify a past block"""

from blockchain import Blockchain
from utils import (
    generate_keys,
    create_transaction,
    public_key_to_string,
)
import json


def test_immutability():
    # First create a sample blockchain with a few blocks
    private_key, public_key = generate_keys()
    pub_str = public_key_to_string(public_key)
    
    # Genesis transaction giving 100 tokens
    tx0 = create_transaction(
        private_key=private_key,
        public_key=pub_str,
        receiver=pub_str,
        amount=100,
    )
    
    # Create blockchain and add a few blocks
    ledger = Blockchain(starting_transactions=[tx0])
    
    # Add two more blocks with simple self-transfers
    for i in range(2):
        tx = create_transaction(
            private_key=private_key,
            public_key=pub_str,
            receiver=pub_str,
            amount=10,
        )
        ledger.add_transaction(tx)
        ledger.new_block(previous_hash=Blockchain.hash(ledger.chain[-1]))
    
    # At this point we have 3 blocks: genesis + 2 more
    print("\nInitial blockchain state:")
    print(f"Number of blocks: {len(ledger.chain)}")
    print(f"Chain valid: {ledger.valid_chain(ledger.chain)}")
    
    # Print block 1's original state
    print("\nBlock 1 before modification:")
    print(json.dumps(ledger.chain[1], indent=2))
    
    # Try to modify block 1's transaction amount
    print("\nModifying block 1's transaction amount from 10 to 20...")
    ledger.chain[1]["transactions"][0]["amount"] = 20
    
    print("\nBlock 1 after modification:")
    print(json.dumps(ledger.chain[1], indent=2))
    
    # Check if chain is still valid
    print(f"\nChain valid after modification: {ledger.valid_chain(ledger.chain)}")
    
    # Explain why it's invalid
    print("\nWhy is it invalid?")
    print("1. Block 1's hash changed because we modified its contents")
    print("2. Block 2's previous_hash still points to Block 1's original hash")
    print("3. This hash mismatch breaks the chain of trust")
    
    # Show the hash mismatch
    block1_current_hash = Blockchain.hash(ledger.chain[1])
    block2_previous_hash = ledger.chain[2]["previous_hash"]
    print(f"\nBlock 1's current hash:     {block1_current_hash}")
    print(f"Block 2's previous_hash:    {block2_previous_hash}")


if __name__ == "__main__":
    test_immutability()