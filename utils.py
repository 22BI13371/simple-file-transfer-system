import argparse
import struct
import ntpath

# the bellow was taken from the answer here:
# https://stackoverflow.com/a/17668009/7771202


def send_msg(sock, msg):
    """Prefix each message with a 4-byte length (network byte order)"""
    msg = struct.pack(">I", len(msg)) + msg
    sock.sendall(msg)


def recv_msg(sock):
    """Read message length and unpack it into an integer"""
    raw_msglen = recvall(sock, 4)
    if not raw_msglen:
        return None
    msglen = struct.unpack(">I", raw_msglen)[0]
    # Read the message data
    return recvall(sock, msglen)


def recvall(sock, n):
    """Helper function to recv n bytes or return None if EOF is hit"""
    data = b""
    while len(data) < n:
        packet = sock.recv(n - len(data))
        if not packet:
            return None
        data += packet
    return data


def path_leaf(path):
    """
    get the string after the final slash in the bath
    """
    head, tail = ntpath.split(path)

    return tail or ntpath.basename(head)
