import socket
import UI
def Main():
    host = "127.0.0.1"
    port = 5000

    #s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s = socket.socket()
    s.connect((host,port))

    UI.MainMenu((s,host,port))

if __name__ == "__main__":
    Main()