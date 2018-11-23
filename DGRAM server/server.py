import socket
import os
import threading

def GetFile(name, sock):
    fileName = sock.recv(1024)
    if os.path.isfile(fileName):
        sock.send(bytes("Exists {}".format(os.path.getsize(fileName)), 'utf-8'))
        userResponse =  sock.recv(1024)
        if userResponse[:2] == "OK":
            with open(fileName, 'rt') as f:
                bytesToSend = f.read(1024)
                sock.send(bytesToSend)
                while bytesToSend != "":
                    bytesToSend = f.read(1024)
                    sock.send(bytesToSend)
    else:
        sock.send(bytes("ERROR",'utf-8'))
    
    sock.close()

def Main():
    host = "127.0.0.1"
    port = 5000
    
    #s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s = socket.socket()

    s.bind((host,port))

    s.listen(5)

    print ("Server started")
    
    while True:
        c, a = s.accept()
        print ("{} connected".format(a))
        t = threading.Thread(target=GetFile, args=("retrThread", c))
        t.start()

    s.close()

if __name__ == "__main__":
    Main()