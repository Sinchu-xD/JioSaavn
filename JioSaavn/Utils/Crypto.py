import base64
import binascii

from pyDes import ECB, PAD_PKCS5, des

# NOTE: DES with this fixed key is JioSaavn's own encryption scheme for media URLs.
# We cannot change the algorithm — it must match what their servers emit.
# DES is a weak cipher (deprecated by NIST in 2005), but this is a read-only
# reverse-engineering context; the key is already publicly documented.
_CIPHER = des(b"38346591", ECB, b"\0\0\0\0\0\0\0\0", pad=None, padmode=PAD_PKCS5)


def decrypt(url: str) -> str | None:
    if not url or not url.strip():
        return None
    try:
        decoded = base64.b64decode(url.strip())
        decrypted: str = _CIPHER.decrypt(decoded, padmode=PAD_PKCS5).decode("utf-8")
        return decrypted.replace("_96.mp4", "_320.mp4")
    except (ValueError, binascii.Error, UnicodeDecodeError):
        return None
