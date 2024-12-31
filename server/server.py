import socket
import threading

HEADER = 64 # Number of bytes to specify the message actual length
PORT = 5000
HOST = socket.gethostbyname(socket.gethostname()) # Get the IP address of the local computer
ADDR = (HOST, PORT)

def awake():
    print("THE SERVER IS AWAKENING...")
    server.listen()
    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr)) # Thread so not to block other clients while connected
        thread.start()

def handle_client(conn, addr):
    print(f"NEW CLIENT CONNECTION: {addr}")
    connected = True
    while connected:
        msg_length = conn.recv(HEADER).decode()
        if not msg_length:
            continue
        msg_length = int(msg_length)
        msg = conn.recv(msg_length).decode()
        if msg == "quit":
            connected = False
        print(msg)
    conn.close()

if __name__ == "__main__":
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(ADDR)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # Set to be reusable socket bc there is a TIME_WAIT before you can use the socket again
    awake()