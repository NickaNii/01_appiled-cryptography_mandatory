import socket
import threading
import sys

host = input("Host ID: ")
port = int(input("Port ID: "))

def receive(socket, signal):
    while signal:
        try:
            data = socket.recv(32)
            print(str(data.decode("utf-8")))

        except:
            print("Disconnected from server.")
            signal = False
            break

try:
    sock = socket.socket(
        socket.AF_INET, 
        socket.SOCK_STREAM)
except:
    print("Server connection failed.")
    input("Confirm with ENTER to quit application.")
    sys.exit(0)

receiveThread = threading.Thread(
    target = receive, 
    args = (sock, True))
receiveThread.start()

while True:
    message = input()
    sock.sendall(str.encode(message))