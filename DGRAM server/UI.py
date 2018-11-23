import sys


def ValidateOption(options):
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

def PrintOptions(options):
    """
    Options: Expects a list with tuples, where te first value is the numer, and the second the text
    """
    for i,t in options:
        print ("({}) > {}.".format(i,t))
    return 0

def PrintTitle(text):
    """
    text: Expects the text to be printed
    """
    text = text.upper()
    text_length = len(text)
    print("*"*3*text_length)
    print("*"+ str(" "*(text_length-1)) + text + str(" "*(text_length-1)) + "*")
    print("*"*3*text_length)
    print ()

def RunSelection(Functions,selection,args=None):
    """
    Functions: List of functions
    selection: Int that indicates the function to run
    args: List of tuples to pass as args for the selected function
    """
    if args == None:
        return Functions[selection-1]()
    else:
        return Functions[selection-1](args[selection-1])
   

def MainMenu(sock):
    """
    sock: Is a tuple like this (s, host, port)
    """
    cond = 0
    while cond >= 0:
        PrintTitle("Main menu")
        opciones = [
            (1, "Buscar archivo"),
            (2, "Opciones de privacidad"),
            (3, "Salir")
        ]
        PrintOptions(opciones)
        selection = ValidateOption(opciones)
        cond = RunSelection(
            [SearchFile, PrintOptions, Exit],
            selection,
            [sock, None, None]
        )

def SearchFile(sock):
    PrintTitle("Search file")
    opciones = [(1,"Full file name"), (2, "Partial file name"), (3, "Return"), (4, "Exit")]
    PrintOptions(opciones)
    selection = ValidateOption(opciones)
    cond = RunSelection(
        [FullNameSearch, PartialNameSearch],
        selection,
        [sock,sock]
    )
    return cond

def FullNameSearch(sock):
    file_name = input("Enter the name of the file.\n> ")
    SendData("_FULL_NAME_SEARCH_", sock)
    SendData(file_name, sock)
    return 1

def PartialNameSearch(sock):
    file_name = input("Enter the name of the file.\n> ")
    SendData("_PARTIAL_NAME_SEARCH_", sock)
    SendData(file_name, sock)
    return 1
    


def PrivacyOptions(args = None):
    return 1




def SendData(data, sock):
    """
    data: Expects a string in utf-8
    sock: Expects a tuple with (s, host, port)
    """
    sock[0].sendto(bytes(data,'utf-8'),(sock[1],sock[2]))
    return 1

def RecieveData(sock):
    return 1

def Exit(args = None):
    return -1
