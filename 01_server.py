import socket, threading


server_port = 8082
host = 'localhost'

class Client(threading.Thread):
    
    # Python constructor
    def __init__(self, client_socket, client_addr,client_id,client_status):
        threading.Thread.__init__(self)
        self.client_socket = client_socket
        self.client_addr = client_addr
        self.client_id = client_id
        self.client_status = client_status
    
    # Python toString()
    def __str__(self):
        return str(self.client_id) + " " + str(self.client_addr)

    # Server checking if client has sent a message
    def run(self):
        while self.client_status:
            try:
                msg = self.client_socket.recv(2048)                
            except Exception as e:
                print("Something went wrong: ", e)
                break
            print("User ID: ", str(self.client_id), "says: ", str(msg))

def clientConnect(server_socket):
    while True:
        client_socket, client_addr = server_socket.accept()
        Client(client_socket, client_addr,"client id",True).start()
        

def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((host, server_port))
    server_socket.listen(10)

    newConnectionsThread = threading.Thread(target = clientConnect, args = (server_socket,))
    newConnectionsThread.start()

main()