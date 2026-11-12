import socket, threading, bcrypt, os, datetime, base64
from cryptography.fernet import Fernet

# Hardcoded server port and host for testing purpose
server_port = 8082
host = 'localhost'
connected_clients = []

class Client(threading.Thread):
    # Python constructor
    def __init__(self, client_socket, client_addr,client_id,client_status,client_kdf):
        threading.Thread.__init__(self)
        self.client_socket = client_socket
        self.client_addr = client_addr
        self.client_id = client_id
        self.client_status = client_status
        self.client_kdf = client_kdf
    
    # Python toString()
    def __str__(self):
        return str(self.client_id), " ", str(self.client_addr)

    # Server checking if client has sent a message
    def run(self):
        self.client_socket.sendall(self.client_id)
        try:
            while self.client_status:
                packet = self.client_socket.recv(2048)
                if not packet:
                    break
                send_messages(packet, self)
        except Exception as e:
            print("Something went wrong: ", e)
        finally:
            if self in connected_clients:
                print("Client:" + self.client_id.hex()[:4] + "has disconnected.")
                connected_clients.remove(self)
            self.client_socket.close()

# bcrypt kdf setup
def kdf_gen(password, salt):
    return bcrypt.kdf(
        password=password,
        salt=salt,
        desired_key_bytes=32,
        rounds=100,
    )

# clients connecting and generating kdf with datetime and client_id
def client_connect(server_socket):
    while True:
        client_socket, client_addr = server_socket.accept()
        
        client_id = os.urandom(16)
        salt = datetime.date.today().isoformat().encode()  # b'2026-11-12'
        client_kdf = kdf_gen(client_id,salt)
        
        print("Client KDF set for Client ID:", client_id.hex()[:4])
        
        connecting_client = Client(client_socket, client_addr,client_id,True,client_kdf)
        connected_clients.append(connecting_client)
        connecting_client.start()

# sending messages to all connected clients, encrypted with each of their own keys
def send_messages(msg, client_sender):
    fernet_key_sender = Fernet(base64.urlsafe_b64encode(client_sender.client_kdf))
    decrypted_msg = client_sender.client_id.hex()[:4] + ' says: ' + fernet_key_sender.decrypt(msg).decode()
    print("User ID:", decrypted_msg)
    for c in list(connected_clients):
        if c.client_kdf == client_sender.client_kdf:
            continue
        try:
            fernet_key_reciever = Fernet(base64.urlsafe_b64encode(c.client_kdf))
            # sending cyphertext
            c.client_socket.sendall(fernet_key_reciever.encrypt(decrypted_msg.encode()))
            print("Sending message to Client ID:", c.client_id.hex()[:4])
        except Exception as e:
            print("Could not send to", c.client_id.hex()[:4], e)

# main method for instansiating sockets and starting threading for the client_connect
def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((host, server_port))
    server_socket.listen(5)

    newConnectionsThread = threading.Thread(target = client_connect, args = (server_socket,))
    newConnectionsThread.start()

main()