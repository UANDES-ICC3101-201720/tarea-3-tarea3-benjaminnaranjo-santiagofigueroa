import threading
import socket
import time
from random import randint
import sys
import pickle

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
    
    def handler(self, conn, addr):# maneja cada conexion. Revisa si piden un archivo o si lo estan enviando
        while True:
            time.sleep(5)
            data = conn.recv(1024)
            if data.decode() == "SEARCH":
                search_params = conn.recv(1024).decode().split(",")
                print ("Searching for '{}' with option {}".format(search_params[0], search_params[1]))
                print (self.connections)
                results = []
                for other_conns in self.connections:
                    if other_conns != conn:
                        other_conns.send("SEARCHING".encode())
                        time.sleep(0.5)
                        other_conns.send(bytes("{},{}".format(search_params[0],search_params[1]), 'utf-8'))
                        print ("Waiting answer from {}".format(other_conns))
                        answer = other_conns.recv(1024).decode()
                        print ("{}\nsaid {}".format(other_conns,answer))
                        if answer != "NORESULTS":
                            results.append((other_conns, answer))
                if len(results)>0:
                    conn.send("CLIENTSRESULTS".encode())
                    for owner,names in results:
                        conn.send(names.encode())
                    conn.send("CLIENTSRESULTSEND".encode())
                    chosen_file = int(conn.recv(1024).decode())
                    results[chosen_file][0].send("DOWNLOAD".encode())
                    time.sleep(0.5)
                    results[chosen_file][0].send(results[chosen_file][1].encode())
                    data = conn.recv(1024).decode()
                    if data[:4] == "FILE":
                        bFile = b''
                        fileSize = int(data[4:])
                        dataRecv = 0
                        while dataRecv<fileSize:
                            data = conn.recv(1024)
                            bFile += data
                            dataRecv = len(bFile)
                        self.SendFile(bFile, conn)
                else:
                    print ("no results")
                    conn.send("NORESULTS".encode())
            if not data:
                self.connections.remove(conn)
                self.peers.remove(addr[0])
                print ("{}:{} disconnected".format(addr[0],addr[1]))
                conn.close()
                self.sendPeers()
                break

    def sendPeers(self):# para enviar la lista de personas conectadas a los usuarios y mantenerlos al dia en caso de que aparezca uno nuevo o alguien se vaya
        p = ""
        for peer in self.peers:
            p = p + peer + ","

        for connection in self.connections:
            connection.send(b'\x11' + bytes(p, "utf-8"))

    def SendFile(self, binaryFile, conn):
        fileSize = len(binaryFile)
        conn.send(bytes("FILE"+str(fileSize), 'utf-8'))
        sendedData = 0
        while sendedData<fileSize:
            goal = sendedData+1024
            if sendedData+1024>fileSize:
                goal = fileSize
            dataPiece = binaryFile[sendedData:goal]
            conn.send(dataPiece)
            sendedData = goal
    
        

class Client:
    def Menu(self, sock):
        while True:
            print ("[MAIN MENU]\n 1. Create file\n 2. Ask for file\n 3. View file")
            opt = input(" Enter a number: ")
            if opt == "1": #enviar un mensaje a todo el mundo
                print("[Creating a new file]".upper())
                self.createFile()
            
            elif opt == "2":#pedir un archivo
                sock.send(bytes("SEARCH", 'utf-8'))
                search_param = input("1. Search by full name\n2. Search by partial name\nEnter an option: ")
                while search_param not in ["1", "2"]:
                    print("Invalid input")
                    search_param = input("1. Search by full name\n2. Search by partial name")
                file_name = input("Enter the name of the file: ")
                sock.send(bytes(file_name+","+search_param, 'utf-8'))#se envia el texto de busqueda y el tipo de busqueda, nombre completo o nombre parcial
                # TODO:recibe los resultados
                print("Waiting for server answer")
                searchResults = []
                server_msg = sock.recv(1024).decode()
                if server_msg == "CLIENTSRESULTS":
                    print("recieved client results")
                    ind = 1
                    opts = []
                    names = []
                    while True:
                        owner_results = sock.recv(1024).decode()
                        if owner_results == "CLIENTSRESULTSEND":
                            break
                        owner_results = owner_results.split(";")
                        for r in owner_results:
                            r = r.split(',')
                            print ("{}. {} - {} bytes".format(ind, r[0], r[1]))
                            opts.append(str(ind))
                            names.append(r[0])
                            ind+=1
                        searchResults.append(owner_results)
                        #print("Result recieved")
                    print("No more results")
                    select = input("Chose the file to download")
                    while select not in opts:
                        select = input("Chose the file to download")
                    sock.send(bytes(select, 'utf-8'))
                    self.recvData(sock, names[int(select)])
                    #TODO: seguir con la seleccion del archivo
                elif server_msg == "NORESULTS":
                    print("No results for the search of {}".format(file_name))
            
            elif opt == "3":
                print ("[View a file]".upper())
                print (" Available files:")
                ind = 1
                options = []
                if len(self.MyFiles)>0:
                    for file in self.MyFiles:
                        print(" {}. {} | {} bytes".format(ind, file.Name, len(bytes(file.Data, 'utf-8'))))
                        options.append(str(ind))
                        ind+=1
                    selectedFile = input(" Choose a file: ")
                    while selectedFile not in options:
                        selectedFile = input(" Choose a file: ")
                    ViewFile(self.MyFiles[int(selectedFile)-1])
                else:
                    print ("No files available")
                input("Press enter to continue...")


    def createFile(self):
        filename = input("Enter the name of the file: ")
        while ChekcFileName(filename, self.MyFiles):
            print ("Name already in use. Try another")
            filename = input("Enter the name of the file: ")
        print("Write your file. Double enter to save and exit")
        filedata = DataCreator()
        self.MyFiles.append(File(filename, filedata))
        print ("File created")

    def sendFile(self, filename, sock):
        for file in self.MyFiles:
            if file.Name == filename:
                filesize = len(bytes(file.Data))
                sock.send("FILE"+str(filesize), 'utf-8')
                time.sleep(0.5)
                datasent = 0
                while datasent<filesize:
                    goal = datasent+1024
                    if datasent+1024>filesize:
                        goal = filesize
                    dataPiece = file.Data[datasent:goal]
                    sock.send(bytes(dataPiece, 'utf-8'))
                    datasent = goal
                break
    
    def recvData(self, sock, filename):# funcion para recibir un archivo
        data = sock.recv(1024).decode()
        if data[:4] == "FILE":
            bFile = b""
            fileSize = int(data[4:])
            dataRecv = 0
            while dataRecv<fileSize:
                data = sock.recv(1024)
                bFile += data
                dataRecv = len(bFile)
            self.MyFiles.append(File(filename, bFile.decode()))
            print ("File aded to library")

    def updatePeers(self, peerData):# actualiza la lista de personas en el servidor
        p2p.peers = str(peerData, "utf-8").split(",")[:-1]

    def findFilesLike(self, sock):
        search_params = sock.recv(1024).decode().split(',')
        print("Params: {}".format(search_params))
        if search_params[1] == "1": #full name coincidence
            result_answer = "" # looks like "name1,25;name2,43" where name1 is the name of the file, and the number is the size 
            if len(self.MyFiles)>0:
                for file in self.MyFiles:
                    if file.Name == search_params[0]:
                        result_answer += "{},{};".format(file.Name, len(bytes(file.Data, 'utf-8')))
                print("sending an answer to the server: '{}'".format(result_answer))
                if len(result_answer)>0:
                    sock.send(bytes(result_answer[:-1], 'utf-8'))
                else:
                    sock.send("NORESULTS".encode())
            else:
                sock.send("NORESULTS".encode())
        elif search_params[1] == "2": #partial name coincidence
            result_answer = "" # looks like "name1,25;name2;43" where name1 is the name of the file, and the number is the size 
            if len(self.MyFiles)>0:
                for file in self.MyFiles:
                    if search_params[0] in file.Name:
                        result_answer += "{},{};".format(file.Name, len(bytes(file.Data, 'utf-8')))
                if len(result_answer)>0:
                    sock.send(bytes(result_answer[:-1], 'utf-8'))
                else:
                    sock.send("NORESULTS".encode())
            else:
                sock.send("NORESULTS".encode())

    def __init__(self, addr): #iniciar la clase Cliente
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)#protocolo de confianza
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)#apagar servidor inmediatamente una vez que se cierra todo
        sock.connect((addr, 10000))
        print("Connected as client...")
        self.MyFiles = []

        iThread = threading.Thread(target=self.Menu, args=(sock,))
        iThread.daemon = True
        iThread.start()

        while True:# este loop detecta cuando el servidor o alguien le dice algo a este cliente
            time.sleep(4)
            data = sock.recv(1024)
            if not data:
                print("{}:{} > No data to read".format(addr[0],addr[1]))
                break
            if data[0:1] == b'\x11':
                self.updatePeers(data[1:])
            elif data.decode() == "SEARCHING":
                self.findFilesLike(sock)
            elif data.decode() == "DOWNLOAD":
                filename = sock.recv(1024).decode()
                self.sendFile(filename, sock)
            else:
                print ("Main: "+str(data.decode()))

class p2p:
    peers = ['127.0.0.1']#se inicia con el servidor conectado

class File:
    def __init__(self, name, data):
        self.Name = name
        self.Data = data

def DataCreator():
    data = ""
    while True:
        line = input("> ")
        if line=="":
            break
        data += line + "\n"
    return data

def ViewFile(file):
    print ("File name: {}".format(file.Name))
    line = ""
    for char in file.Data:
        if char=="\n":
            print(" {}".format(line))
            line = ""
        else:
            line += char
    print ("End of file")

def ChekcFileName(name, files):
    for file in files:
        if file.Name == name:
            return True
    return False

if __name__ == "__main__":
    while True:# aqui se separa el servidor del cliente una vez que se corre el programa
        try:
            print("trying to connect...")
            time.sleep(randint(1, 5))
            for peer in p2p.peers:
                try:
                    client = Client(peer) #si ya hay un peer que es un servidor, se conecta al servidor
                except KeyboardInterrupt:
                    sys.exit(0)
                except:
                    pass
                
                try:
                    server = Server()# si nadie es servidor, se intenta transformar en servidor
                except KeyboardInterrupt:
                    sys.exit(0)
                except:
                    print("Couldn't connect to server")
        except KeyboardInterrupt:
            sys.exit(0)