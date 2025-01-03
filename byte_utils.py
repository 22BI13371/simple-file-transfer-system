import array
from copy import deepcopy
import json
import types


def make_args_map(args: dict) -> dict:
    """
    prepares this args dict for being JSON serialized

    adds a '__map' attribute which maps each member to its type,
    so that we can do backward translation
    """

    if type(args) is not dict:
        raise Exception("args must be of type dict")

    if "__map" in args:
        raise Exception('make_args_map(): "args" already has a "__map":', args)

    args = deepcopy(args)

    __map = {}
    for k, v in args.items():
        if isinstance(v, types.FunctionType):  # functions get the name passed
            args[k] = v.__name__
            __map[k] = "function"
        elif isinstance(v, bytes):  # bytes get turned into strings
            args[k] = _bytes_to_string(v)
            __map[k] = "bytes"
        elif isinstance(v, dict):
            print("make_args_map(): dict type encountered:", v)
            make_args_map(args[k])

    args["__map"] = __map
    # print(args)
    return args


def apply_args_map(argsin: dict) -> dict:
    if type(argsin) is not dict:
        raise Exception("args must be of type dict")
    if "__map" not in argsin:
        raise Exception('apply_args_map(): "args" does not have "__map":', argsin)

    args = deepcopy(argsin)
    # print("apply args map degub", args)

    for k, arg_type in args["__map"].items():
        if arg_type == "function":
            args[k] = eval(args[k])
            pass
        elif arg_type == "bytes":
            args[k] = _string_to_bytes(args[k])
        elif arg_type == "dict":
            print("apply_args_map(): dict type encountered:", arg_type)
            apply_args_map(args[k])

    del args["__map"]
    return args


def _string_to_bytes(text):
    if text is None:
        text = ""
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


def _bytes_to_int(xbytes: bytes) -> bytes:
    return int.from_bytes(xbytes, "big")


def args_to_msg(args: dict) -> bytes:
    return _string_to_bytes(json.dumps(make_args_map(args)))


def msg_to_args(args: bytes) -> dict:
    return apply_args_map(json.loads(_bytes_to_string(args)))
