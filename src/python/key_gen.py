import hashlib
import secrets

def generate_random_key():
    # Generate random bytes (you can specify the desired length)
    random_bytes = secrets.token_bytes(32)  # 32 bytes for SHA-512
    sha512_hash = hashlib.sha512(random_bytes).hexdigest()     # Calculating SHA-512 hash from random bytes
    return sha512_hash

# random_key = generate_random_key()
# print("Generated random key SHA-512:", random_key)
# print("Generated random key SHA-512:", random_key[0:50:])