import json
import os
import subprocess
import sys
import argparse
import socket
import shlex
import types
import secrets
from copy import deepcopy

# changing dir to access modules
sys.path.insert(1, os.path.join(sys.path[0], ".."))

from byte_utils import _string_to_bytes, _bytes_to_string
from utils import send_msg, recv_msg, path_leaf
from encryption import CipherLib

# 256 bits = 32 bytes
# b'faa2a773b80091c287e43deb36b4621dd172309239e99c5922ca9f8bb88253eb'
DEFAULT_KEY = _bytes_to_string(
    b"\xfa\xa2\xa7\x73\xb8\x00\x91\xc2\x87\xe4\x3d\xeb\x36\xb4\x62\x1d\xd1\x72\x30\x92\x39\xe9\x9c\x59\x22\xca\x9f\x8b\xb8\x82\x53\xeb"
)


def send_command(args, callback=lambda sock: print("Connected", sock)):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        print("send cmd args", args)
        print("Connecting to server...", end="")
        s.connect((args["host"], args["port"]))
        print("Connection established")

        args["auth"] = False
        args["iv"] = secrets.token_bytes(16)
        request_json = args_to_json(args)
        send_msg(s, _string_to_bytes(request_json))

        resp = recv_msg(s)
        resp_json = json.load(_bytes_to_string(resp))
        if resp_json["readystate"] in [202]:
            res = callback(s)

            send_msg(s, b"200")
            print("\nTransaction complete")
            return res


def args_to_json(args: dict) -> str:
    s_args = deepcopy(args)
    for k, v in s_args.items():
        if isinstance(v, types.FunctionType):
            s_args[k] = v.__name__
        elif isinstance(v, bytes):
            s_args[k] = _bytes_to_string(v)

    s_args["cipher"] = s_args.get("cipherfunc", "none")
    del s_args["key"]

    request_json = json.dumps(s_args)

    return request_json


def get_user_commands(parser: argparse.ArgumentParser, args=None):
    command = ""

    if not args:
        args = vars(parser.parse_args())

    if not command:
        done = False
        while not done:
            command = input("$ ")
            print()

            try:
                args = vars(parser.parse_args(shlex.split(command)))
                print(args)
                done = True
            except Exception as e:
                print("Exception", e)

    args["_command"] = command
    print("get user cmds", args)

    return args


def exec_function(args: dict):
    if "function" in args:
        return args["function"](args)


def get_arg_parser():
    """
    creating command parser object
    """
    parser = argparse.ArgumentParser()

    parser.add_argument("--port", default=5000, type=int)
    parser.add_argument("--host", default="127.0.0.1", type=str)
    parser.add_argument("--auth", default=True, action="store_true")
    parser.add_argument("-k", "--key", default=DEFAULT_KEY)

    subparsers = parser.add_subparsers()

    parser_quit = subparsers.add_parser("quit", aliases=["q", "exit"])
    parser_quit.set_defaults(function=quit)

    parser_get = subparsers.add_parser("get", aliases=[])
    parser_get.add_argument("filename", type=str)
    parser_get.set_defaults(function=get)

    parser_put = subparsers.add_parser("put", aliases=[])
    parser_put.add_argument("filename", type=str)
    parser_put.set_defaults(function=put)

    parser_ls = subparsers.add_parser("ls", aliases=[])
    parser_ls.set_defaults(function=ls)

    # https://docs.python.org/2/library/argparse.html#action-classes
    # class argparse.Action(option_strings, dest, nargs=None, const=None, default=None, type=None, choices=None, required=False, help=None, metavar=None)
    class ChooseCypherAction(argparse.Action):
        def __call__(self, parser, namespace, values, *args, **kwargs):
            """
            :param parser - The ArgumentParser object which contains this action.

            :param namespace - The Namespace object that will be returned by parse_args(). Most actions add an attribute to this object using setattr().

            :param values - The associated command-line arguments, with any type conversions applied. Type conversions are specified with the type keyword argument to add_argument().

            :param option_string - The option string that was used to invoke this action.
                The option_string argument is optional, and will be absent if the action is associated with a positional argument.

            :param args:
            :param kwargs:
            :return:
            """
            print("action args:")
            setattr(namespace, "cipherfunc", getattr(CipherLib, values))
            print(values)
            print(getattr(CipherLib, values))

    ciphers = list(
        filter(lambda s: not str(s).startswith("__"), CipherLib.__dict__.keys())
    )

    parser.add_argument(
        "-c",
        "--cipher",
        default="none",
        choices=ciphers,
        action=ChooseCypherAction,
        help="The encryption/decryption algorithm to use when receiving the file."
        'Applies to both "put" and "pull". Default: none',
    )

    return parser


# Client actions


def get(args: dict):
    def callback(conn: socket):
        resp = json.loads(_bytes_to_string(recv_msg(conn)))

        if not os.path.isdir("./client_files"):
            os.mkdir("./client_files")

        filename = os.path.join("client_files", path_leaf(args["filename"]))

        if os.path.isdir(filename):
            args["filename"] = os.path.join(args["filename"], resp["filename"])

        with open(filename, "wb+") as f:
            plaintxt = args["cipherfunc"](
                data=resp["data"], key=args["key"], decrypt=True, iv=resp["iv"]
            )
            f.write(plaintxt)

            if os.path.isfile(filename):
                subprocess.Popen(rf"explorer /select, \"{filename}\"")

    return send_command(args, callback)


def put():

    def callback(conn: socket):
        conn.sendall()

    return 0


def ls():

    return 0


def quit(args=None):
    exit(0)
