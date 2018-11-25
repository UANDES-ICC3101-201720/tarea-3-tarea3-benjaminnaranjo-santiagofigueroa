import threading
import socket
import time
from random import randint
import sys

class Server:
    connections = [] #aqui se guardan las conexiones
    peers = [] #aqui se guardan los addr de los clientes

    def __init__(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Protocolo de envio confiable
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # esto es para que el socket se cierre cuando se cierra el programa
        sock.bind(('0.0.0.0', 10000))
        sock.listen(1)
        print ("Server started")

        while True:
            conn, addr = sock.accept()
            cThread = threading.Thread(target=self.handler, args=(conn, addr)) # al aceptar una conexion, crea un thread para escuchar al nuevo cliente
            cThread.daemon = True
            cThread.start()
            self.connections.append(conn)
            self.peers.append(addr[0])
            self.sendPeers()
            print ("{}:{} connected".format(addr[0],addr[1]))
    
    def handler(self, conn, addr):
        while True:
            data = conn.recv(1024)
            for connection in self.connections:
                connection.send(data)
            if not data:
                self.connections.remove(conn)
                self.peers.remove(addr[0])
                print ("{}:{} disconnected".format(addr[0],addr[1]))
                conn.close()
                self.sendPeers()
                break

    def sendPeers(self):
        p = ""
        for peer in self.peers:
            p = p + peer + ","

        for connection in self.connections:
            connection.send(b'\x11' + bytes(p, "utf-8"))
    
    def sendFile(self, filename, filesize, conn, addr):
        print("Beggining to send file")
        conn.send(bytes("FILE,"+filename+","+str(filesize),'utf-8'))
        with open(filename, 'rb') as file:
            data = file.read(1024)
            conn.send(data)
            while data != bytes(''.encode()):
                data = file.read(1024)
                conn.send(data)

            print(' File sent successfully.')
        

class Client:
    def Menu(self, sock):
        while True:
            print ("Main menu\n1. Send message\n2. Ask for file")
            opt = input("Enter a number: ")
            if opt == "1":
                print("Sending a message (mainly for testing who is listening)")
                self.sendMsg(sock)
            elif opt == "2":
                search_param = input("1. Search by full name\n2. Search by partial name\nEnter an option: ")
                while search_param not in ["1", "2"]:
                    print("Invalid input")
                    search_param = input("1. Search by full name\n2. Search by partial name")
                file_name = input("Enter the name of the file: ")
                sock.send(bytes(file_name+","+search_param, 'utf-8'))
                name, data = self.recvData(file_name, sock)
                if name!=None and data!=None:
                    new_file = File(name, data)
                    self.MyFiles.append(new_file)
                    print("File added to personal library")
                pass

    def sendMsg(self, sock):
        sock.send(bytes(input(""), 'utf-8'))

    def recvData(self, filename, sock):
        data = str(sock.recv(1024), 'utf-8')
        if data[:6] == "EXISTS":
            filesize = long(data[6:])
            message = input("File Exists, {} bytes. Download? Y/N > ".format(filesize))
            if message == 'Y':
                sock.send(bytes("OK",'utf-8'))
                newf_name = filename
                newf_data = sock.recv(1024)
                totalRecv = len(newf_data)
                while totalRecv < filesize:
                    newf_data = sock.recv(1024)
                    totalRecv += len(newf_data)
                print ("Download complete")
            return newf_name, newf_data
        else:
            print ("File doesn't exists")
            return None, None
    def updatePeers(self, peerData):
        p2p.peers = str(peerData, "utf-8").split(",")[:-1]

    def __init__(self, addr):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.connect((addr, 10000))
        print("Connected as client...")
        self.MyFiles = []

        iThread = threading.Thread(target=self.Menu, args=(sock,))
        iThread.daemon = True
        iThread.start()

        while True:
            data = sock.recv(1024)
            if not data:
                print("{}:{} > No data to read".format(addr[0],addr[1]))
                break
            if data[0:1] == b'\x11':
                self.updatePeers(data[1:])
            else:
                print ("[SERVER]"+str(data.decode()))

class p2p:
    peers = ['127.0.0.1']

class File:
    def __init__(self, name, data):
        self.Name = name
        self.Data = data


if __name__ == "__main__":
    while True:
        try:
            print("trying to connect...")
            time.sleep(randint(1, 5))
            for peer in p2p.peers:
                try:
                    client = Client(peer)
                except KeyboardInterrupt:
                    sys.exit(0)
                except:
                    pass
                
                try:
                    server = Server()
                except KeyboardInterrupt:
                    sys.exit(0)
                except:
                    print("Couldn't connect to server")
        except KeyboardInterrupt:
            sys.exit(0)