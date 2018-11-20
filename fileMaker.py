archivo = open("numeros.txt","w")

for i in range(1000):
    linea = ""
    for j in range(10):
        linea += "{} ".format(j)
    archivo.write(linea+"\n")