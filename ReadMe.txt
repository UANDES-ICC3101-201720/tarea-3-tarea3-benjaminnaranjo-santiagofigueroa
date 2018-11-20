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