import base64
from Crypto.Cipher import AES
from Crypto.Hash import SHA256
from Crypto import Random
from bleach import clean
import markdown
from argon2 import PasswordHasher

possible_tags = ['h1', 'h2', 'h3', 'h4', 'h5', 'img', 'a', 'em', 'p', 'strong', 'br']
possible_attributes = {'img': ['src', 'alt'], 'a': ['href', 'title']}

ph = PasswordHasher(time_cost = 200)

hash_rounds = 500000

def encrypt(key, source):
    for i in range(hash_rounds):
        key = SHA256.new(key).digest()
    IV = Random.new().read(AES.block_size)
    encryptor = AES.new(key, AES.MODE_CBC, IV)
    padding = AES.block_size - len(source) % AES.block_size 
    source += bytes([padding]) * padding 
    data = IV + encryptor.encrypt(source) 
    return base64.b64encode(data).decode("latin-1")

def decrypt(key, source):
    source = base64.b64decode(source.encode("latin-1"))
    for i in range(hash_rounds):
        key = SHA256.new(key).digest()
    IV = source[:AES.block_size]
    decryptor = AES.new(key, AES.MODE_CBC, IV)
    data = decryptor.decrypt(source[AES.block_size:])
    padding = data[-1]
    if data[-padding:] != bytes([padding]) * padding:
        raise ValueError("Invalid padding...")
    return data[:-padding]

def clean_note(note):
    return clean(markdown.markdown(note), possible_tags, possible_attributes)