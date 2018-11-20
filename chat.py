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
                print ("\t\tLooking for '{}'.".format(str(data, 'utf-8')))
                # TODO: Pedir a los nodos que muestren los archivos que tienen
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
    
    def mainMenu(self):
        while True:
            seleccion = 0
            opciones = [(1,"Enviar mensaje"),
                        (2,"Pedir archivo"),
                        (3,"Mostrar mis archivos")]
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

    def __init__(self, address):
        self.sock.connect((address, 10000))

        iThread = threading.Thread(target=self.mainMenu)
        iThread.daemon = True
        iThread.start()

        while True:
            data = self.sock.recv(1024)
            if not data:
                break
            print (str(data, 'utf-8'))


if (len(sys.argv) > 1):
    client = Client(sys.argv[1])
else:
    server = Server()
    server.run()