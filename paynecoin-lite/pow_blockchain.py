"""Proof of Work Blockchain Simulation

Creates a sample blockchain with proof-of-work mining for each block.
Each block's hash must have at least 5 leading zeros.
"""

from blockchain import Blockchain
from utils import (
    generate_keys,
    create_transaction,
    public_key_to_string,
)
import time
from hashlib import sha256
import json


class PoWBlockchain(Blockchain):
    def mine_block(self, previous_hash=None):
        """Create a new Block in the Blockchain with proof of work
        
        :param previous_hash: Hash of previous Block
        :return: New Block, time taken to mine
        """
        if previous_hash is None:
            previous_hash = self.hash(self.chain[-1])
            
        # Create block template (nonce will be adjusted)
        block = {
            "nonce": 0,
            "index": len(self.chain),
            "timestamp": time.time(),
            "transactions": self.current_transactions,
            "previous_hash": previous_hash
        }
        
        # Mine the block (find nonce that gives enough leading zeros)
        start_time = time.time()
        while True:
            block_hash = self.hash(block)
            if block_hash.startswith("00000"):
                mining_time = time.time() - start_time
                # Reset the current list of transactions
                self.current_transactions = []
                self.chain.append(block)
                return block, mining_time
            block["nonce"] += 1


def build_pow_blockchain():
    """Create a sample blockchain with proof-of-work for each block"""
    
    # Generate keys for participants
    key_dict = {}
    for name in ["You", "Alice", "Bob"]:
        private_key, public_key = generate_keys()
        key_dict[name] = {"private_key": private_key, "public_key": public_key}
    
    # Initial transaction giving you 100 tokens
    tx0 = create_transaction(
        private_key=key_dict["You"]["private_key"],
        public_key=public_key_to_string(key_dict["You"]["public_key"]),
        receiver=public_key_to_string(key_dict["You"]["public_key"]),
        amount=100,
    )
    
    # Initialize blockchain
    ledger = PoWBlockchain(starting_transactions=[tx0])
    
    # Helper to create valid transactions
    def make_tx(sender_name, receiver_name, amount):
        sender = key_dict[sender_name]
        receiver = key_dict[receiver_name]
        tx = create_transaction(
            private_key=sender["private_key"],
            public_key=public_key_to_string(sender["public_key"]),
            receiver=public_key_to_string(receiver["public_key"]),
            amount=amount,
        )
        return tx
    
    # List of transactions to create (sender, receiver, amount)
    planned_txs = [
        ("You", "Alice", 30),
        ("You", "Bob", 20),
        ("Alice", "Bob", 10),
        ("You", "Alice", 25),
        ("Bob", "Alice", 5),
        ("You", "Bob", 15),
        ("Alice", "You", 8),
        ("Bob", "You", 12),
        ("You", "Alice", 10),
        ("Bob", "Alice", 7),
    ]
    
    # Create blocks with these transactions (2 tx per block)
    total_mining_time = 0
    for i in range(0, len(planned_txs), 2):
        block_txs = planned_txs[i:i+2]
        print(f"\nCreating block {len(ledger.chain)} with transactions:")
        for sender, receiver, amount in block_txs:
            print(f"  {sender} -> {receiver}: {amount} tokens")
            try:
                tx = make_tx(sender, receiver, amount)
                ledger.add_transaction(tx)
            except ValueError as e:
                print(f"  Skipped: {e}")
        
        # Mine the block
        block, mining_time = ledger.mine_block()
        total_mining_time += mining_time
        print(f"Mined block with nonce {block['nonce']} in {mining_time:.2f}s")
        print(f"Block hash: {PoWBlockchain.hash(block)}")
    
    print(f"\nTotal time spent mining: {total_mining_time:.2f}s")
    return ledger, key_dict


def main():
    print("Building proof-of-work blockchain (this may take a while)...")
    print("Each block must have a hash with 5 leading zeros\n")
    
    start_time = time.time()
    ledger, key_dict = build_pow_blockchain()
    total_time = time.time() - start_time
    
    print(f"\nBlockchain built in {total_time:.2f}s")
    print(f"Number of blocks: {len(ledger.chain)}")
    print(f"Chain valid: {ledger.valid_chain(ledger.chain)}")
    
    # Print final balances
    balances = ledger.get_balances()
    print("\nFinal balances:")
    for name, keys in key_dict.items():
        pub = public_key_to_string(keys["public_key"])
        print(f"{name}: {balances.get(pub, 0)} tokens")


if __name__ == "__main__":
    main()
