import hashlib
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from Crypto.Random import get_random_bytes

SBOX_PATH = 'path_to_sbox_file'

def load_sbox(filename):
    with open(filename, 'r') as file:
        lines = file.read().split()
        return lines

def fse512_substitution(data, sbox):
    hex_data = data.hex()
    return ''.join(sbox[int(hex_data[i:i+2], 16) % len(sbox)] for i in range(0, len(hex_data), 2))

def aes_encrypt(data, key, iv):
    cipher = AES.new(key, AES.MODE_CBC, iv)
    data_padded = pad(data, AES.block_size)
    return cipher.encrypt(data_padded)

def encrypt(data):
    sbox = load_sbox(SBOX_PATH)

    sha256_hash = hashlib.sha256(data.encode()).digest()
    sha3_hash = hashlib.sha3_256(sha256_hash).digest()
    aes_key = hashlib.sha256(b'secretkey').digest()
    iv = get_random_bytes(AES.block_size)  # Generate a random Initialization Vector (IV)

    aes_encrypted_data = aes_encrypt(sha3_hash, aes_key, iv)
    custom_encrypted_data = aes_encrypted_data  # No custom encryption for uniqueness
    extended_data = (custom_encrypted_data * (512 // len(custom_encrypted_data) + 1))[:512]
    encrypted_data = fse512_substitution(extended_data, sbox)

    return encrypted_data[:512].ljust(512, '0')
