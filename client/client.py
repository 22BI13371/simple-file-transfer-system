import json
import socket
import struct
import hashlib
import random
import os, sys
from client_backend import get_arg_parser, get_user_commands, exec_function, args_to_json

# changing dir to access modules
sys.path.insert(1, os.path.join(sys.path[0], ".."))

from byte_utils import _string_to_bytes, _bytes_to_string, args_to_msg, msg_to_args
from utils import send_msg, recv_msg

HEADER = 64
PORT = 5000
HOST = socket.gethostbyname(
    socket.gethostname()
)  # Get the IP address of the local computer
ADDR = (HOST, PORT)

# Global parameters (public, known to both parties)
g = 999999999999999999  # Generator
m = 1019  # Prime modulus


def authenticate(args, conn = None):
    """Generate a private and public key."""
    d = random.randint(1, m - 1)
    e = pow(g, d, m)

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as conn:
        print("Attempting to connect to the server...", end='')
        conn.connect((args['host'], args['port']))
        # conn.connect(ADDR)
        print("\nServer connected")

        # Send client's public key
        print(f"Client public key: {e}")
        args["client_e"] = e
        # conn.sendall(struct.pack("!I", e))
        # print(args)
        send_msg(conn, _string_to_bytes(args_to_json(args)))

        # OK 200 response
        resp = json.loads(_bytes_to_string(recv_msg(conn)))
        if resp['readystate'] in [200]:
            print("ERROR: server did not respond with OK 200, terminating session...")
            return

        # Receive server's public key
        # server_e = struct.unpack("!I", conn.recv(4))[0]
        args = msg_to_args(recv_msg(conn))
        server_e = args['server_e']
        print(f"Received server public key: {server_e}")

        # Calculate shared key
        shared_key = pow(server_e, d, m)
        print(f"Shared key: {shared_key}")

        # Authenticate
        h = hashlib.sha256()
        h.update(f"{shared_key}".encode())
        auth_hash = h.digest()
        
        auth_msg = {
            'client_auth_hash': auth_hash
        }
        print(auth_msg)
        send_msg(conn, args_to_msg(auth_msg))
        # conn.sendall(auth_hash)

        # Turn shared_key to bytes
        shared_key_bytes = f"{shared_key}".encode()

        # Receive server's authentication hash

        args = msg_to_args(recv_msg(conn))
        server_auth_hash = args["server_auth_hash"]
        # server_auth_hash = conn.recv(32)
        if server_auth_hash == auth_hash:
            print("Authentication is successful")
            return shared_key_bytes
        else:
            print("Authetication failed.")
            return False


def push_msg(sock: socket, msg):
    message = msg.encode()
    msg_length = len(message)
    send_legnth = str(msg_length).encode()
    send_legnth += b" " * (
        HEADER - len(send_legnth)
    )  # Added padded length to fit the header length

    sock.send(send_legnth)
    sock.send(message)


def main():
    parser = get_arg_parser()

    args = None
    authed = False
    i = 0

    # client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # client.connect(ADDR)
    # K = authenticate(args)

    while True:
        i += 1
        args = get_user_commands(parser, args)
        print("init args", args)

        if authed:
            args['auth'] = False

        if args['auth']:
            print("Authenticating server...")
            args['key'] = authenticate(args)
            # print("updating key", args)
            if args['key'] == False:
                exit(1)
            else:
                authed = True
                print("authed successful")
                continue
            
        args['auth'] = False
        print("after auth", args)
                

        # msg = input("$ ")
        # if msg != "":
        #     push_msg(client, msg)
        # if msg == "quit" or KeyboardInterrupt:
        #     break

        resp = exec_function(args)


if __name__ == "__main__":
    main()
