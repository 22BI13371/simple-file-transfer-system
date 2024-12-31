import socket
import threading
import random
import struct
import hashlib
import os
import sys
from server_backend import get_arg_parser, receive_command

# changing dir to access modules
sys.path.insert(1, os.path.join(sys.path[0], ".."))

from utils import send_msg, recv_msg

HEADER = 64  # Number of bytes to specify the message actual length
PORT = 5000
HOST = socket.gethostbyname(
    socket.gethostname()
)  # Get the IP address of the local computer
ADDR = (HOST, PORT)

# Global parameters (public, known to both parties)
g = 999999999999999999  # Generator
m = 1019  # Prime modulus


def awake():
    print("THE SERVER IS AWAKENING...")
    server.listen()
    parser = get_arg_parser()
    args = vars(parser.parse_args())
    i = 0

    while True:
        i += 1
        sess = {}
        conn, addr = server.accept()
        thread = threading.Thread(
            target=handle_client, args=(conn, addr)
        )  # Thread so not to block other clients while connected
        thread.daemon = (
            True  # Set thread to be daemon so it does not block the main thread to exit
        )
        thread.start()
        # handle_client(conn, addr)


def authenticate(conn):
    """Generate a private key and a public key"""
    d = random.randint(1, m - 1)  # Private key
    e = pow(g, d, m)
    print(f"SERVER PUBLIC KEY: {e}")

    # Receive client's public key
    client_e = struct.unpack("!I", conn.recv(4))[0]
    print(f"CLIENT PUBLIC KEY RECEIVED: {client_e}")

    # Send server's public key
    conn.sendall(struct.pack("!I", e))
    print(f"SERVER PUBLIC KEY SENT: {e}")

    # Calculate shared key
    shared_key = pow(client_e, d, m)
    print(f"Shared key: {shared_key}")

    # Authenticate
    h = hashlib.sha256()
    h.update(f"{shared_key}".encode())
    auth_hash = h.digest()
    conn.sendall(auth_hash)
    print("AUTHENTICATION HASH SENT")

    # Receive client's authentication hash
    client_auth_hash = conn.recv(32)
    if client_auth_hash == auth_hash:
        print("CLIENT ACCEPTED")
        # conn.sendall(b"PRAISE TO THE OMNISSIAH")
        return True
    else:
        print("HERESY DETECTED, SIGNING CLIENT'S DEATH WARRANT")
        # conn.sendall(b"TERMINATE")
        return False


def handle_client(conn: socket, addr):
    print(f"NEW CLIENT CONNECTION: {addr}")
    connected = True
    connected = authenticate(conn)

    # with conn:
    #     client_args = receive_command(conn)

    #     result = client_args["function"](conn, client_args)

    #     final_client_resp = recv_msg(conn)
    #     if final_client_resp in [r"200"]:
    #         print("Transaction successfull")
    #     else:
    #         print("Something went wrong, transaction unsuccessfull")

    while connected:
        msg_length = conn.recv(HEADER).decode()
        if not msg_length:
            continue
        msg_length = int(msg_length)
        msg = conn.recv(msg_length).decode()
        if msg == "quit":
            connected = False
        print(f"MESSAGE RECEIVED GRACEFULLY: {msg}")
    conn.close()


if __name__ == "__main__":
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.bind(ADDR)
        server.setsockopt(
            socket.SOL_SOCKET, socket.SO_REUSEADDR, 1
        )  # Set to be reusable socket bc there is a TIME_WAIT before you can use the socket again

        try:
            awake()
        except KeyboardInterrupt:
            print("!!!SHUTTING DOWN SERVER!!!")
            server.shutdown(socket.SHUT_RDWR)
            server.close()
            exit(0)
