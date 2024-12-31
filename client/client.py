import socket
import struct
import hashlib
import random
from client_backend import get_arg_parser, get_user_commands, exec_function

HEADER = 64
PORT = 5000
HOST = socket.gethostbyname(
    socket.gethostname()
)  # Get the IP address of the local computer
ADDR = (HOST, PORT)

# Global parameters (public, known to both parties)
g = 999999999999999999  # Generator
m = 1019  # Prime modulus


def authenticate(conn):
    """Generate a private and public key."""
    d = random.randint(1, m - 1)
    e = pow(g, d, m)

    # Send client's public key
    print(f"Client public key: {e}")
    conn.sendall(struct.pack("!I", e))

    # Receive server's public key
    server_e = struct.unpack("!I", conn.recv(4))[0]
    print(f"Received server public key: {server_e}")

    # Calculate shared key
    shared_key = pow(server_e, d, m)
    print(f"Shared key: {shared_key}")

    # Authenticate
    h = hashlib.sha256()
    h.update(f"{shared_key}".encode())
    auth_hash = h.digest()
    conn.sendall(auth_hash)

    # Receive server's authentication hash
    server_auth_hash = conn.recv(32)
    if server_auth_hash == auth_hash:
        print("Authentication is successful")
        return True
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
    authedOnce = False
    i = 0

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(ADDR)
    connected = authenticate(client)

    while connected:
        i += 1
        args = get_user_commands(parser, args)
        print(args)

        msg = input("$ ")
        if msg != "":
            push_msg(client, msg)
        if msg == "quit" or KeyboardInterrupt:
            break

        # resp = exec_function(args)


if __name__ == "__main__":
    main()
