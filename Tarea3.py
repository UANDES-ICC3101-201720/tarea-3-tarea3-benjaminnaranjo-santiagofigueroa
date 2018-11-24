import threading
import socket

class Server:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    connections = []
    def __init__(self):
        self.sock.bind(('0.0.0.0', 10000))
        self.sock.listen(1)
        print ("Server started")
    
    def handler(self, conn, addr):
        while True:
            data = conn.recv(1024)
            for connection in self.connections:
                connection.send(data)
            if not data:
                self.connections.remove(conn)
                print ("{}:{} disconnected".format(addr[0],addr[1]))
                conn.close()
                break

    def run(self):
        while True:
            conn, addr = self.sock.accept()
            cThread = threading.Thread(target=self.handler, args=(conn, addr))
            cThread.daemon = True
            cThread.start()
            self.connections.append(conn)
            print(socket.getaddrinfo(addr))
            print ("{}:{} connected".format(addr[0],addr[1]))

class Client:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def sendMsg(self):
        self.sock.send(bytes(input(""), 'utf-8'))

    def __init__(self, address):
        self.sock.connect((address, 10000))

        iThread = threading.Thread(target=self.sendMsg)
        iThread.daemon = True
        iThread.start()

        while True:
            data = self.sock.recv(1024)
            if not data:
                break
            print (data)




if __name__ == "__main__":
    login = input("Login as server or client: ")
    while login not in ["server", "client"]:
        login = input("Login as server or client: ")
    if login == "server":
        server = Server()
        server.run()
    else:
        addr = input("Enter the client address: ")
        client = Client(addr)
