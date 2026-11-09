import socket
import threading
import sys
import bcrypt

key = bcrypt.kdf(
    password = b"password1234",
    salt = b"salt1234",
    desired_key_bytes = 32,
    rounds = 100
)

def receive(socket, 
            signal):
    while signal:
        try:
            data = socket.recv(32)
            print(str(data.decode("utf-8")))
        
        except:
            print("Disconnected from server")
            signal = False
            break

host = input("Host ID: ")
port = int(input("Port ID: "))

try:
    sock = socket.socket(socket.AF_INET, 
                         socket.SOCK_STREAM)
    sock.connect((host, port))

except:
    print("Failed server connection")
    input("Press ENTER to quit")
    sys.exit(0)

receiveThread = threading.Thread(target = receive, 
                                 args = (sock, True))
receiveThread.start()

while True:
    message = input()
    sock.sendall(str.encode(message))