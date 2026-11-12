import socket, threading, bcrypt, os, itertools, datetime, base64
from cryptography.fernet import Fernet


server_port = 8082
host = 'localhost'
session_key = ''
connected_clients = []

user_id_counter = itertools.count(1)

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
        return str(self.client_id) + " " + str(self.client_addr)

    # Server checking if client has sent a message
    def run(self):
        self.client_socket.sendall(self.client_id)
        
        while self.client_status:
            try:
                packet = self.client_socket.recv(2048)
                msg = packet.decode("utf-8")
            except Exception as e:
                print("Something went wrong: ", e)
                break
            if not packet:
                connected_clients.remove(self)
                break
        
            print("User ID:", self.client_id, "says:", msg)
            
            fernet_key = Fernet(base64.urlsafe_b64encode(self.client_kdf))
            
            encrypted_msg = fernet_key.encrypt(msg.encode())
            
            decrypted_msg = fernet_key.decrypt(encrypted_msg).decode()
            #print("encrypted_msg: ", encrypted_msg)
            #print("decrypted_msg: ", decrypted_msg)
            
        #for c in connected_clients:
        #    print(c.client_addr, c.client_status, c.client_kdf)        
        
        self.client_socket.close()

def derive(password, salt):
    return bcrypt.kdf(
        password=password,
        salt=salt,
        desired_key_bytes=32,
        rounds=100,
    )


def clientConnect(server_socket):
    while True:
        client_socket, client_addr = server_socket.accept()
        
        client_id = os.urandom(16)
        salt = datetime.date.today().isoformat().encode()  # b'2026-11-12'
        client_kdf = derive(client_id,salt)
        
        print("client KDF: ", client_kdf)
        
        connecting_client = Client(client_socket, client_addr,client_id,True,client_kdf)
        connected_clients.append(connecting_client)
        connecting_client.start()


def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((host, server_port))
    server_socket.listen(10) #TODO edit and set correct listen count

    newConnectionsThread = threading.Thread(target = clientConnect, args = (server_socket,))
    newConnectionsThread.start()

main()