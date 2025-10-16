"""Simulation: create a sample blockchain with You, Alice, and Bob.

This script:
- Generates Ed25519 keypairs for You, Alice, and Bob
- Creates a genesis transaction giving You 100 tokens
- Builds 6 blocks, each with >=2 transactions among the three parties
- Validates the blockchain using `valid_chain()`
- Plots balances over time for the three participants

Run interactively (it will open a matplotlib window) or from a notebook.
"""

from blockchain import Blockchain
from utils import (
    generate_keys,
    create_transaction,
    is_from_sender,
    public_key_to_string,
)

import matplotlib.pyplot as plt


def build_sample_blockchain():
    # Generate keys
    key_dict = {}
    for name in ["You", "Alice", "Bob"]:
        private_key, public_key = generate_keys()
        key_dict[name] = {"private_key": private_key, "public_key": public_key}

    # Genesis transaction: You receive 100 tokens
    tx0 = create_transaction(
        private_key=key_dict["You"]["private_key"],
        public_key=public_key_to_string(key_dict["You"]["public_key"]),
        receiver=public_key_to_string(key_dict["You"]["public_key"]),
        amount=100,
    )
    assert is_from_sender(tx0)

    # Initialize blockchain with genesis transactions list
    ledger = Blockchain(starting_transactions=[tx0])

    # Helper to make and add a transaction (and validate signature)
    def make_tx(sender_name, receiver_name, amount):
        sender = key_dict[sender_name]
        receiver = key_dict[receiver_name]
        tx = create_transaction(
            private_key=sender["private_key"],
            public_key=public_key_to_string(sender["public_key"]),
            receiver=public_key_to_string(receiver["public_key"]),
            amount=amount,
        )
        if not is_from_sender(tx):
            raise ValueError("Created transaction failed signature verification")
        return tx

    # We'll construct 6 blocks (including genesis already created), so add 5 more
    # For each block, create exactly 2 transactions among You, Alice, Bob
    import random

    # Create blocks with deterministic transactions to prevent negative balances
    # Format: (sender, receiver, amount)
    planned_transactions = [
        # Block 1 (You have 100 tokens initially)
        ("You", "Alice", 30),  
        ("You", "Bob", 20),    
        
        # Block 2
        ("Alice", "Bob", 10),  
        ("You", "Alice", 25),    
        
        # Block 3
        ("Bob", "Alice", 5),  
        ("You", "Bob", 15),  
        
        # Block 4
        ("Alice", "You", 8),  
        ("Bob", "You", 12),    
        
        # Block 5
        ("You", "Alice", 10),  
        ("Bob", "Alice", 7),    
    ]

    # Process transactions two at a time to create blocks
    for i in range(0, len(planned_transactions), 2):
        block_txs = planned_transactions[i:i+2]
        for sender, receiver, amount in block_txs:
            tx = make_tx(sender, receiver, amount)
            ledger.add_transaction(tx)

        # Close the block using previous hash
        prev_hash = Blockchain.hash(ledger.chain[-1])
        ledger.new_block(previous_hash=prev_hash)

    return ledger, key_dict


def balances_over_time(ledger, key_dict):
    # For each block, compute balances incrementally
    pub_strings = {name: public_key_to_string(key_dict[name]["public_key"]) for name in key_dict}
    
    # Initialize balances tracking
    names = ["You", "Alice", "Bob"]
    balances_time = {name: [] for name in names}
    # Initialize balances (You starts with 100 from genesis block)
    balances = {pub_strings[name]: 100 if name == "You" else 0 for name in names}
    
    # Process blocks one at a time
    for block in ledger.chain:
        # Apply all transactions in this block
        for tx in block["transactions"]:
            sender = tx["sender"]
            receiver = tx["receiver"]
            amount = tx["amount"]
            balances[sender] -= amount
            balances[receiver] += amount
            
        # Record everyone's balance after this block
        for name in names:
            pub = pub_strings[name]
            balances_time[name].append(balances[pub])

    return balances_time


def plot_balances(balances_time):
    import matplotlib.pyplot as plt

    names = list(balances_time.keys())
    xs = list(range(len(next(iter(balances_time.values())))))
    plt.figure(figsize=(8, 4))
    for name in names:
        plt.plot(xs, balances_time[name], marker="o", label=name)
    plt.xlabel("Block index (0 = genesis)")
    plt.ylabel("Balance")
    plt.title("Balances over time")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()


def main():
    ledger, key_dict = build_sample_blockchain()

    # Validate chain
    is_valid = ledger.valid_chain(ledger.chain)
    print("Valid chain:", is_valid)

    # Compute balances over time and plot
    balances_time = balances_over_time(ledger, key_dict)
    print("Balances over time:")
    for name, vals in balances_time.items():
        print(f"  {name}: {vals}")

    plot_balances(balances_time)


if __name__ == "__main__":
    main()
