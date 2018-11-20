"""
Al ejecutar desde consola:
    python3 serverV2.py > Crea el servidor.
    python3 serverV2.py 127.0.0.5 > Crea un cliente. Un address distinto para cada uno
"""

import socket
import threading
import sys


class Server:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    connections = []

    def __init__(self):
        self.sock.bind(('0.0.0.0', 10000))
        self.sock.listen(1)

    def handler(self, c, a):
        while True:
            data = c.recv(1024)
            if str(data, 'utf-8') == "_FILE_":
                print ("{}:{} is asking for a file".format(a[0],a[1]))
                data = c.recv(1024)
                search = str(data, 'utf-8')
                search_results = []
                print ("\t\tLooking for '{}'.".format(search))
                # TODO: Pedir a los nodos que muestren los archivos que tienen
                for connection in self.connections:
                    connection.send(bytes("_SHOW_FILES_LIKE_", 'utf-8'))
                    connection.send(bytes(search, 'utf-8'))
                    results = c.recv(1024)
                    results = str(results, 'utf-8')
                    results = results.strip()
                    results = results.split("|") # | is a special char for separating results
                    for r in results:
                        search_results.append((a,r))
                print ("Search results:")
                for result in search_results:
                    print ("{}:{} has '{}'".format(result[0][0], result[0][1], result[1]))
            else:
                print ("{}:{} said: {}".format(a[0],a[1],str(data, 'utf-8')))
                for connection in self.connections:
                    connection.send(bytes(data))
            if not data:
                print(str(a[0])+":"+str(a[1]),"disconected")
                self.connections.remove(c)
                c.close()
                break
    def run(self):
        while True:
            c, a = self.sock.accept()
            cThread = threading.Thread(target=self.handler, args = (c,a))
            cThread.daemon = True
            cThread.start()
            self.connections.append(c)
            print(str(a[0])+":"+str(a[1]),"conected")

class Client:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    public = False
    MyFiles = []
    
    def mainMenu(self):
        while True:
            seleccion = 0
            opciones = [(1,"Enviar mensaje"),
                        (2,"Pedir archivo"),
                        (3,"Mostrar mis archivos"),
                        (4,"Agregar un archivo")]
            for i,text in opciones:
                print ("[{}] {}.".format(i,text))
            seleccion = input("Ingrese una opcion: ")
            op_invalida = True
            while op_invalida:
                for i,text in opciones:
                    if str(i) == str(seleccion):
                        op_invalida = False
                        break
                if op_invalida:    
                    seleccion = input("Opcion invalida. Ingrese una opcion: ")

            if seleccion == "1":
                self.sendMsg()
            elif seleccion == "2":
                self.askFile()
            elif seleccion == "3":
                self.showFiles()
                print ("Public files: {}".format(self.public))
            elif seleccion == "4":
                self.addFile()
                

    def sendMsg(self):
        self.sock.send(bytes(input("Write you message: "), 'utf-8'))
    
    def askFile(self):
        self.sock.send(bytes("_FILE_", 'utf-8'))
        self.sock.send(bytes(input("Enter the name of the file: "), 'utf-8'))
    
    def showFiles(self):
        seleccion = 0
        opciones = [(1,"SI"),
                    (2,"NO")]
        for i,text in opciones:
            print ("[{}] {}.".format(i,text))
        seleccion = input("Ingrese una opcion: ")
        op_invalida = True
        while op_invalida:
            for i,text in opciones:
                if str(i) == str(seleccion):
                    op_invalida = False
                    break
            if op_invalida:    
                seleccion = input("Opcion invalida. Ingrese una opcion: ")
        if seleccion == "1":
            self.public = True
        else:
            self.public = False
    
    def sendFile(self, file):
        pass

    def addFile(self):
        filename = input("Enter the name of the file: ")
        new_file = File(filename)
        self.MyFiles.append(new_file)
        print ("File added.")
    
    def searchFiles(self, searchValues):
        result = ""
        if self.public == False:
            return "Files are private"
        for file in self.MyFiles:
            if searchValues in file.Title:
                result += file.Title + "|"
        result = result[:-1]
        if len(result)<1:
            return "No matches"
        return result
        

    def __init__(self, address):
        self.sock.connect((address, 10000))

        iThread = threading.Thread(target=self.mainMenu)
        iThread.daemon = True
        iThread.start()

        while True:
            data = self.sock.recv(1024)
            if not data:
                break
            server_msg = str(data, 'utf-8')
            if server_msg == "_SHOW_FILES_LIKE_":
                data = self.sock.recv(1024)
                search_value = str(data, 'utf-8')
                result = self.searchFiles(search_value)
                self.sock.send(bytes(result, 'utf-8'))
            elif server_msg == "_BROADCAST_":
                print (server_msg)

class File:
    def __init__(self, Title):
        self.Title = Title

if (len(sys.argv) > 1):
    client = Client(sys.argv[1])
else:
    server = Server()
    server.run()