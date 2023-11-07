# server.py
import socket
import threading

class Server(threading.Thread):
    def __init__(self, host, port):
        super().__init__(daemon=True, target=self.listen)

        self.host = host
        self.port = port
        self.shutdown = False
        self.client_list = []
        self.nicknames = []

        # set up server socket
        try:
            self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server.bind((self.host, self.port))
            self.server.listen(10)
            self.start()
            print('type "quit" to close the server!')
            print("=" * 20)
            print(f"[*] listening as {self.host} : {self.port}")
            print("[*] waiting for client to connect")
        except Exception as e:
            print(f"[!] error: {e}")
        
    # method to connection
    def listen(self):
        while not self.shutdown:
            client, addr = self.server.accept()
            print(f"[+] {str(addr)} is connected!")
            
            if client not in self.client_list:
                # if there's a new client join
                self.client_list.append(client)
                client.send("login".encode('utf-8'))
                nickname = client.recv(1024).decode('utf-8')
                self.nicknames.append(nickname)

                self.broadcast(f"{nickname} has joined the chat!\n".encode('utf-8'))
                client.send("[*] connected to the server !".encode('utf-8'))

                # handle for any messages from clients
                threading.Thread(target=self.handle_client_messages, args=(client,)).start()            
    
    # broadcast method
    def broadcast(self, message):
        for client in self.client_list:
            try:
                client.send(message)
            except Exception as e:
                print(f"[!] error: {e}")
    
    # method for handle messages from clients
    def handle_client_messages(self, client):
        while True:
            try:
                message = client.recv(1024).decode('utf-8')
                if not message:
                    break

                self.broadcast(f"{self.nicknames[self.client_list.index(client)]}:\n{message}".encode('utf-8'))
            except Exception as e:
                print(f"[!] error: {e}")
                break
        self.remove_client(client)

    def remove_client(self, client):
        if client in self.client_list:
            index = self.client_list.index(client)
            nickname = self.nicknames[index]
            self.client_list.remove(client)
            self.nicknames.remove(nickname)
            self.broadcast(f"{nickname} has left the chat.\n".encode('utf-8'))
            client.close()

    def stop_server(self):
        self.shutdown = True
        print("[!] server disconnected!")
        self.server.close()            

host = '0.0.0.0'
port = 3000

server = Server(host=host, port=port)   

while True:
    msg = input()
    if msg == 'quit':
        server.stop_server()
        break
