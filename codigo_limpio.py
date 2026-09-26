import socket
PUERTO = 9000
HOST = "0.0.0.0"
TAMANO_BUFFER = 1024
servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
# El servidor necesita una dirección conocida para que los clientes puedan conectarse.
servidor.bind((HOST, PUERTO))
# listen() deja el socket preparado para aceptar conexiones entrantes.
servidor.listen(1)
# accept() se bloquea hasta que un cliente se conecta y devuelve un socket nuevo.
conexion, direccion_cliente = servidor.accept()
# recv() espera los datos enviados por el cliente.
datos = conexion.recv(TAMANO_BUFFER)
print("Me llego:", datos.decode("utf-8"))
conexion.close()
servidor.close()
