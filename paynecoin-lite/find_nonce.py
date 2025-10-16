"""Find a nonce that produces a hash with 5 leading zeros"""

from blockchain import Blockchain
import time

def find_nonce_with_leading_zeros():
    message = "The quick brown fox jumps over the lazy dog"
    target = "00000"  # 5 leading zeros
    nonce = 0
    attempts = 0
    start_time = time.time()
    
    while True:
        # Create the test string
        test_data = {"data": str(nonce) + message}
        # Get its hash using blockchain's method
        current_hash = Blockchain.hash(test_data)
        
        # Every million attempts, show progress
        attempts += 1
        if attempts % 1_000_000 == 0:
            elapsed = time.time() - start_time
            print(f"Tried {attempts:,} nonces in {elapsed:.1f}s")
            print(f"Current nonce: {nonce}")
            print(f"Current hash: {current_hash}")
            print()
            
        # Check if we found a solution
        if current_hash.startswith(target):
            elapsed = time.time() - start_time
            print(f"\nFound solution after {attempts:,} attempts and {elapsed:.1f} seconds!")
            print(f"Nonce: {nonce}")
            print(f"Hash: {current_hash}")
            
            # Verify our solution
            print("\nVerifying solution:")
            verification = Blockchain.hash({"data": str(nonce) + message})
            print(f"Verification hash: {verification}")
            print(f"Matches: {verification == current_hash}")
            return nonce
            
        nonce += 1

if __name__ == "__main__":
    print("Searching for nonce that produces hash with 5 leading zeros...")
    print("Message: 'The quick brown fox jumps over the lazy dog'")
    print("This may take a while...\n")
    
    nonce = find_nonce_with_leading_zeros()
    
    print("""
Why can't we use optimization algorithms to find the nonce?

1. Cryptographic Hash Properties:
   - The SHA-256 hash function is designed to be "chaotic" - tiny input changes cause 
     completely different outputs
   - There is no pattern or gradient to follow - changing the nonce by 1 gives a 
     completely unpredictable new hash
   
2. No Helpful Feedback:
   - Optimization algorithms need some way to know if they're getting "closer" to a solution
   - But with hashes, being "close" (like having 4 leading zeros) gives no information 
     about which nonce values might give 5 zeros
   - Each attempt is effectively random, regardless of previous attempts
   
3. No Shortcuts:
   - The only way to find a nonce is to try them one by one
   - This is intentional - it's the core idea behind Proof of Work in cryptocurrencies
   - The work cannot be shortcut with clever algorithms
   
4. Example:
   nonce = 123 → hash = "a5b7..."  (no leading zeros)
   nonce = 124 → hash = "f29c..."  (completely different, still no help)
   There's no way to use these results to make a better guess about which nonce to try next
   
This is why mining cryptocurrency requires raw computing power rather than algorithmic 
cleverness - you simply have to try nonces until you find one that works.""")