Iniciar un servidor:                > python3 chat.py
Iniciar un cliente:                 > python3 chat.py 127.2.5.1 
                                        (puede ser cualquier direccion)

Hay que crearlos en consolas distintas.

La clase Servidor se encarga de comunicar a todos los clientes.
La clase Cliente tiene tres opciones:
    Enviar un mensaje, por ahora ese mensaje le llega a todo el mundo, inlcuido él.
    Pedir un archivo. Envía un mensaje al Servidor para que procese el pedido.
    Mostrar mis archivos. Cambia la configuración de privacidad del cliente, en caso de que este 
     no quiera mostrarle sus archivos al servidor.

Cuando se busca un archivo, se envía a todos los clientes el texto de busqueda, y los clientes
 devuelven una lista con los libros que tienen que contengan el texto de busqueda en el título.
 Si lo archivos de un cliente son privados, se devuelve el mensaje correspondiente.
 Si un cliente no tiene ninguna cincidencia, se devuelve el mensaje correspondiente.