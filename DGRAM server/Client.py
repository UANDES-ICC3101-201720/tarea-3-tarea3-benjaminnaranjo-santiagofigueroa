import socket
import threading
import sys


class Client:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    MyFiles = []

    def ContentInput(self):
        content = ""
        line = input("Write some text. Double enter to end\n>>> ")
        while line != "":
            content += line + "\n"
            line = input()
        return content

    def ValidateOption(self, options):
        """
        Options: Expects a list with tuples, where te first value is the numer, and the second the text
        """
        selection = ""
        options_str = ""
        for i,t in options:
            options_str += str(i)
        while selection not in options_str or selection=="":
            selection = input("Chose an option: ")
        return int(selection)

    def PrintOptions(self, options):
        """
        Options: Expects a list with tuples, where te first value is the numer, and the second the text
        """
        for i,t in options:
            print ("({}) > {}.".format(i,t))
        return 0

    def PrintTitle(self, text):
        """
        text: Expects the text to be printed
        """
        text = text.upper()
        text_length = len(text)
        print("*"*3*text_length)
        print("*"+ str(" "*(text_length-1)) + text + str(" "*(text_length-1)) + "*")
        print("*"*3*text_length)
        print ()
    
    def RunSelection(self, Functions, Selection, Args=None):
        """
        Functions: List of functions
        selection: Int that indicates the function to run
        args: List of tuples to pass as args for the selected function
        """
        if Args == None:
            return Functions[Selection-1]()
        else:
            return Functions[Selection-1](Args[Selection-1])

    def MainMenu(self):
        while self.cond >= 0:
            self.PrintTitle("main menu")
            opciones = [
                (1, "Buscar archivo"),
                (2, "Crear archivo"),
                (3, "Ver un archivo"),
                (4, "Opciones de privacidad"),
                (5, "Salir")
            ]
            self.PrintOptions(opciones)
            selection = self.ValidateOption(opciones)
            self.RunSelection(
                [self.SearchFile, self.NewFile, self.ListFiles, self.PrivacyOptions, self.Exit],
                selection
            )

    def SearchFile(self):
        self.PrintTitle("search file")
        opciones = [(1,"Full file name"), (2, "Partial file name")]
        self.PrintOptions(opciones)
        selection = self.ValidateOption(opciones)
        self.sock[0].sendto(bytes("_FILE_", 'utf-8'),self.socket)
        self.RunSelection(
            [self.FullNameSearch, self.PartialNameSearch],
            selection
        )
        if selection<3:
            print ("Waiting for server answer...")
            server_answer = str(self.sock[0].recv(1024),'utf-8')
            print (server_answer)

    def FullNameSearch(self):
        file_name = input("Enter the name of the file.\n> ")
        self.sock[0].sendto(bytes(file_name,'utf-8'), self.socket)#check
        print ("Message delivered")
        return 1

    def PartialNameSearch(self):
        file_name = input("Enter the name of the file.\n> ")
        self.sock[0].sendto(bytes(file_name,'utf-8'), self.socket)#check
        print ("Message delivered")
        return 1

    def Return(self, arg = None):
        return 1
    
    def Exit(self, arg = None):
        self.cond = -1
        
        return -1

    def NewFile(self):
        self.PrintTitle("Create new file")
        title = input("File name: ")
        content = self.ContentInput()
        self.addFile(title, content)
        return 1

    def addFile(self, title, content):
        new_file = File(title, content)
        self.MyFiles.append(new_file)
        return 1

    def showFiles(self, searchValue):
        file_names = ""
        if self.public:
            for file in self.MyFiles:
                file_names += "{}|".format(file.Title)
        else:
            file_names = "Private user"
        if file_names == "":
            file_names = "No matches"
        return file_names[:-1]

    def ListFiles(self):
        self.PrintTitle("my files")
        i = 1
        options = []
        for file in self.MyFiles:
            print("{}. {}".format(i,file.Title))
            options.append((i,file.Title))
            i+=1
        options.append((i,"Volver"))
        options.append((i+1,"Salir"))
        selection = self.ValidateOption(options)
        if selection == i:
            return 1
        elif selection == i+1:
            self.cond = -1
            return -1
        else:
            print("Opening '{}'".format(self.MyFiles[selection-1].Title))
            self.ViewFile(self.MyFiles[selection-1].Title)
        return 1

    def ViewFile(self, fileName):
        self.PrintTitle("view file")
        for file in self.MyFiles:
            if file.Title == fileName:
                print(file.Data)
                print("="*20)
        input("Press enter to continue...")
        return 1

    def PrivacyOptions(self):
        self.PrintTitle("privacy options")
        print ("Showing my files: {}".format(self.public))
        options = [
            (1, "SHOW"),
            (2, "HIDE")
        ]
        self.PrintOptions(options)
        selection = self.ValidateOption(options)
        if selection == 1:
            self.public = True
        else:
            self.public = False
        return 1

    def __init__(self, address, port = 5000):
        self.s.connect((address,port))
        self.host = address
        self.port = port
        self.sock = (self.s, self.host, self.port)
        self.socket = (self.host, self.port)
        self.cond = 0
        self.public = False

        mainThread = threading.Thread(target=self.MainMenu)
        mainThread.daemon = True
        mainThread.start()


        while self.cond>=0:
            data, adr = self.s.recvfrom(1024)
            data = str(data, 'utf-8')
            print ("[MAIN] msg from '{}' saying: {}".format(adr,data))
            if not data:
                break
            server_msg = str(data, 'utf-8')
            if server_msg == "_SHOW_FILES_LIKE_":
                data, adr = self.s.recvfrom(1024)
                search_value = str(data, 'utf-8')
                result = self.showFiles(search_value)
                self.s.send(bytes(result, 'utf-8'))
            elif server_msg == "_BROADCAST_":
                print (server_msg)

class File:
    def __init__(self, Title, Data = ""):
        self.Title = Title
        self.Data = Data
    def AddData(self, Data):
        self.Data = Data

client1 = Client('localhost')