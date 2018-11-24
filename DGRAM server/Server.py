import socket
import threading

class Server:
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    connections = []

    def __init__(self):
        self.sock.bind(('localhost', 5000))
        #self.sock.listen(3)

    def handler(self):
        while True:
            data, address = self.sock.recvfrom(1024)
            if address not in self.connections:
                self.connections.append(address)
            if str(data, 'utf-8') == "_FILE_":
                print ("{}:{} is asking for a file".format(address[0],address[1]))
                self.sock.sendto(bytes("_SEND_SEARCH_",'utf-8'),address)#enviar mensaje al solicitante
                data, asker = self.sock.recvfrom(1024)
                search = str(data, 'utf-8')
                search_results = []
                print ("\t\tLooking for '{}'.".format(search))
                # TODO: Pedir a los nodos que muestren los archivos que tienen
                for connection in self.connections:
                    self.sock.sendto(bytes("_SHOW_FILES_LIKE_", 'utf-8'),connection)
                    self.sock.sendto(bytes(search, 'utf-8'),connection)
                    results, a = self.sock.recvfrom(1024)
                    results = str(results, 'utf-8')
                    results = results.strip()
                    results = results.split("|") # | is a special char for separating results
                    for r in results:
                        search_results.append((a,r))
                
                print ("Search results:") # esta linea muestra los resultados en la consola servidor
                self.sock.sendto(bytes("_SEARCH_RESULTS_", 'utf-8'),asker) # se envia un mensaje especial al cliente que solicito una busqueda
                for result in search_results:
                    print ("{}:{} has '{}'".format(result[0][0], result[0][1], result[1]))
                    self.sock.sendto(bytes(result[1], 'utf-8'),asker) # se le envia una lista de las personas que tienen el archivo, para que elija cual descargar
                    # esto es suponiendo que haya buscado una palabra y varios documentos coincidan con esa palabra.
                    # como la foto en que buscaba caballo, y habia "mi caballo blanco" y "el caballo blanco de napoleon"
                # TODO: Esperar respuesta de usuario, pedir archivos, enviar archivo.
                # En esta indentacion hay que esperar la respuesta del cliente que pidió el libro.
                # Cuando el usuario responde, se recibe el nombre del archivo, con el .txt o lo que sea
                # sevuelve a pedir el archivo y esta vez se toma el primer resultado y se envia

                
            else:
                print ("{}:{} said: {}".format(address[0],address[1],str(data, 'utf-8')))
                for connection in self.connections:
                    self.sock.sendto(bytes(data),connection)
            if not data:
                print(str(address[0])+":"+str(address[1]),"disconected")
                self.connections.remove(address)
                break

    def run(self):
        print ("Server running")
        self.handler()

server = Server()
server.run()