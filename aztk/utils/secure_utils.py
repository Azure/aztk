import random
import string

from Cryptodome.Cipher import AES, PKCS1_OAEP
from Cryptodome.PublicKey import RSA
from Cryptodome.Random import get_random_bytes


def encrypt_password(ssh_pub_key, password):
    if not password:
        return [None, None, None, None]
    recipient_key = RSA.import_key(ssh_pub_key)
    session_key = get_random_bytes(16)

    # Encrypt the session key with the public RSA key
    cipher_rsa = PKCS1_OAEP.new(recipient_key)
    encrypted_aes_session_key = cipher_rsa.encrypt(session_key)

    # Encrypt the data with the AES session key
    cipher_aes = AES.new(session_key, AES.MODE_EAX)
    ciphertext, tag = cipher_aes.encrypt_and_digest(password.encode())
    return [encrypted_aes_session_key, cipher_aes.nonce, tag, ciphertext]


def generate_random_string(charset=string.ascii_uppercase + string.ascii_lowercase, length=16):
    return "".join(random.SystemRandom().choice(charset) for _ in range(length))
