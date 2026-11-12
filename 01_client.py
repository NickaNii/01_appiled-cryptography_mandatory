# imports
import socket, threading, sys, bcrypt, datetime, base64
from cryptography.fernet import Fernet

client_kdf = None

# bcrypt kdf setup
def kdf_gen(password, salt):
    return bcrypt.kdf(
        password=password,
        salt=salt,
        desired_key_bytes=32,
        rounds=100,
    )

# receive message function
def receive(socket, signal):
    global client_kdf
    # First recieve for client_id for use in KDF generation
    try:
        client_id = socket.recv(16)
        print("client_id: ", client_id)
        
        salt = datetime.date.today().isoformat().encode()  # b'2026-11-12'
        client_kdf = kdf_gen(client_id,salt)
    except:
        print("error")
    while signal:
        try:
            data = socket.recv(32)
            print(str(data.decode("utf-8")))
        except:
            print("Disconnected from server")
            signal = False
            break

# define host and port ID
#host = input("Host ID: ")
#port = int(input("Port ID: "))

port = 8082
host = 'localhost'

try:
    sock = socket.socket(
        socket.AF_INET, 
        socket.SOCK_STREAM)
    sock.connect((host, port))

except:
    print("Failed server connection")
    input("Press ENTER to quit")
    sys.exit(0)

receiveThread = threading.Thread(
    target = receive, 
    args = (sock, True))
receiveThread.start()

while True:
    msg = input()
    fernet_key = Fernet(base64.urlsafe_b64encode(client_kdf))
    encrypted_msg = fernet_key.encrypt(msg.encode())
    
    sock.sendall(encrypted_msg)