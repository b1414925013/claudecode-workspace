import base64
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from ksm_core.config import settings


def _get_key_iv() -> tuple[bytes, bytes]:
    key = settings.AES_SECRET_KEY.encode("utf-8")
    iv = settings.AES_SECRET_IV.encode("utf-8")
    key = key.ljust(32, b"\0")[:32]
    iv = iv.ljust(16, b"\0")[:16]
    return key, iv


def aes_encrypt(plain_text: str) -> str:
    key, iv = _get_key_iv()
    padder = padding.PKCS7(128).padder()
    data = plain_text.encode("utf-8")
    padded_data = padder.update(data) + padder.finalize()
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
    encryptor = cipher.encryptor()
    encrypted = encryptor.update(padded_data) + encryptor.finalize()
    return base64.b64encode(encrypted).decode("utf-8")


def aes_decrypt(encrypted_text: str) -> str:
    key, iv = _get_key_iv()
    encrypted = base64.b64decode(encrypted_text)
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
    decryptor = cipher.decryptor()
    padded_data = decryptor.update(encrypted) + decryptor.finalize()
    unpadder = padding.PKCS7(128).unpadder()
    data = unpadder.update(padded_data) + unpadder.finalize()
    return data.decode("utf-8")
