import argparse
import socket
import subprocess
import json
import secrets
import pprint

import os, sys

# changing dir to access modules
sys.path.insert(1, os.path.join(sys.path[0], ".."))

from byte_utils import _string_to_bytes, _bytes_to_string
from utils import recv_msg, send_msg, path_leaf
from encryption import CipherLib

PORT = 5000
HOST = socket.gethostbyname(socket.gethostname())

# 256 bits = 32 bytes
# b'faa2a773b80091c287e43deb36b4621dd172309239e99c5922ca9f8bb88253eb'
DEFAULT_KEY = _bytes_to_string(
    b"\xfa\xa2\xa7\x73\xb8\x00\x91\xc2\x87\xe4\x3d\xeb\x36\xb4\x62\x1d\xd1\x72\x30\x92\x39\xe9\x9c\x59\x22\xca\x9f\x8b\xb8\x82\x53\xeb"
)


def get_arg_parser():
    parser = argparse.ArgumentParser("Server side")
    parser.add_argument("--port", default=PORT, type=int)
    parser.add_argument("--host", default=HOST, type=str)

    return parser


def parse_command_json(command_json):
    client_args = {  # extend default
        "auth": True,
        "key": DEFAULT_KEY,
        "cipher": "none",
        "filename": "",
        "function": lambda x: None,
        "iv": None,
    }

    client_args.update(json.loads(command_json))
    # print(client_args)

    client_args["cipherfunc"] = getattr(CipherLib, client_args["cipher"])
    client_args["iv"] = _string_to_bytes(client_args["iv"])
    client_args["function"] = eval(client_args["function"])

    # printing client args
    pp = pprint.PrettyPrinter(indent=4)
    print("client args")
    pp.pprint(client_args)

    return client_args


def receive_command(conn: socket, client_parser=None):
    """
    waits for a command by the client, and returns the parsed args,
    responds to the client with 202 and data on success

    :param conn: socket connection
    :return: client command arguments, or None if invalid command
    """
    command_json = _bytes_to_string(recv_msg(conn))
    print("recieve command debug:", command_json)

    client_args = parse_command_json(command_json)
    print("client args debug:", client_args)

    server_resp = _string_to_bytes(
        json.dumps(
            {
                "readystate": 202,
            }
        )
    )
    send_msg(conn, server_resp)
    # print(client_args)
    return client_args


def get(conn: socket, args=None):
    # sending files to client

    iv = secrets.token_bytes(16)
    print("iv: ", iv)

    filename = os.path.join("server_files", path_leaf(args["filename"]))
    with open(filename, "rb") as f:
        plaintxt = f.read()
        ciphertxt = args["cipherfunc"](data=plaintxt, key=args["key"], iv=iv)

    print(f'Done reading file "{filename}", {len(ciphertxt)}B')

    return send_msg(
        conn,
        _string_to_bytes(
            json.dumps(
                {
                    "filename": filename,
                    "data": _bytes_to_string(ciphertxt),
                    "iv": _bytes_to_string(iv),
                }
            )
        ),
    )


def put(conn: socket, args=None):
    # recv file from client and write to file
    print("receiving file...")
    client_data = json.loads(_bytes_to_string(recv_msg(conn)))

    args["filename"] = os.path.join("server_files", args["filename"])

    data = client_data["data"]
    if data is None:
        print("Problem: data received is None")
    print("got the file data!: {}Bytes".format(len(data)))

    if not os.path.isdir("./server_files"):
        os.mkdir("./server_files")

    filename = os.path.join("server_files", path_leaf(args["filename"]))

    print("iv=", client_data["iv"])

    with open(filename, "wb+") as f:
        plaintext = args["cipherfunc"](
            data=data, key=args["key"], decrypt=True, iv=client_data["iv"]
        )
        f.write(plaintext)

    print("recieved file:", args["filename"])

    # if os.path.isfile(filename):
    #     subprocess.Popen(r'explorer /select,"{}"'.format(args["filename"]))


def ls(conn: socket, args=None):
    # send list of files
    filelist = os.listdir("server_files/")
    filelist_json = json.dumps(filelist)
    send_msg(conn, _string_to_bytes(filelist_json))
