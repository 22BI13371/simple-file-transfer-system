import pyaes

from byte_utils import _string_to_bytes, ensure_bytes


class CipherLib:
    def __init__(self):
        raise Exception("Cannot instantiate this class" + self.__class__.__name__)

    @staticmethod
    def none(data, decrypt=False, key=None, **kwargs) -> bytes:
        if isinstance(data, str):
            data = _string_to_bytes(data)

        return data

    @staticmethod
    def aes(data, decrypt=False, key=None, **kwarks) -> bytes:
        """
        :param data: data as string or bytes
        :param decrypt: decrypt or encrypt?
        :param key: A 256 bit (32 byte) key
        :param kwargs:
        :return:

        ```
        aes(data, decrypt=False, iv='intializationVec')
        ```
        """

        if key is None:
            print("No AES key is given", key)
            return data

        iv_128 = kwarks.get("iv", None)

        key = ensure_bytes(key)
        data = ensure_bytes(data)
        iv_128 = ensure_bytes(iv_128)

        aes = pyaes.AESModeOfOperationCBC(key, iv=iv_128)

        operation = aes.decrypt if decrypt else aes.encrypt

        chunks = pad_and_slice(data, block_size=16)

        new_data = b"".join((map(operation, chunks)))

        return new_data


def pad_and_slice(data: bytes, block_size: int = 16) -> list[bytes]:
    """
    pad the data to multiple of 16 and split into chunks to be encrypted
    """
    # padding for multiple of 16
    remainder = len(data)
    padding = bytes((block_size - remainder) % block_size)
    padded_data = b"".join([data, padding])

    # split data in to chunks of size 16
    n_blocks = len(padded_data) // block_size
    chunks = [
        padded_data[i * block_size : (i + 1) * block_size] for i in range(n_blocks)
    ]

    return chunks
