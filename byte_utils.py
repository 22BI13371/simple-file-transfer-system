import array
import json


def _string_to_bytes(text):
    if text is None:
        test = ""
    array_array = array.array("B", list(ord(c) for c in text))

    return bytes(array_array)


def _bytes_to_string(bin):
    if bin is None:
        bin = b""

    return "".join(chr(b) for b in bin)


def ensure_bytes(a):
    if isinstance(a, array.array):
        a = bytes(a)
    if isinstance(a, (str)):
        a = _string_to_bytes(a)

    return a


def _int_to_bytes(x: int) -> bytes:
    return x.to_bytes((x.bit_length() + 7) // 8, "big")


def _bytes_to_string(xbytes: bytes) -> bytes:
    return int.from_bytes(xbytes, "big")


def args_to_msg(args: dict) -> bytes:
    return _string_to_bytes(json.dumps(args))


def msg_to_json(args: bytearray) -> dict:
    return json.loads(_bytes_to_string(args))
