import hashlib
import secrets

def generate_random_key():
    # Генерация случайных байтов (можно указать нужную длину)
    random_bytes = secrets.token_bytes(32)  # 32 байта для SHA-512

    # Вычисление SHA-512 хеша от случайных байтов
    sha512_hash = hashlib.sha512(random_bytes).hexdigest()

    return sha512_hash

# random_key = generate_random_key()
# print("Сгенерированный случайный ключ SHA-512:", random_key)
# print("Сгенерированный случайный ключ SHA-512:", random_key[0:50:])