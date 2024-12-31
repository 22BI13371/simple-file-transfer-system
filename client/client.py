import socket

HEADER = 64
PORT = 5000
HOST = socket.gethostbyname(socket.gethostname()) # Get the IP address of the local computer
ADDR = (HOST, PORT)

def push_msg(msg):
    message = msg.encode()
    msg_length = len(message)
    send_legnth = str(msg_length).encode()
    send_legnth += b' ' * (HEADER - len(send_legnth)) # Added padded length to fit the header length
    client.send(send_legnth)
    client.send(message)

if __name__ == "__main__":
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(ADDR)

    while True:
        msg = input("$ ")
        if msg != "":
            push_msg(msg)
        
        if msg == "quit":
            break
        