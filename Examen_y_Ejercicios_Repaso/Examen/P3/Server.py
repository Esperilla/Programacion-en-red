# Servidor para probar P3

import socket

HOST = "0.0.0.0"
PUERTO = 5001

servidor = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 
servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
servidor.bind((HOST, PUERTO))
print(f"Servidor UDP escuchando en el puerto {PUERTO}...")

while True:
    datos, direccion = servidor.recvfrom(1024)
    mensaje = datos.decode("utf-8").strip()  
    print(f"Datagrama de {direccion}: {mensaje!r}")

    if mensaje == "ESTADO":
        respuesta = "servidor activo"
    else:
        respuesta = "comando desconocido"

    servidor.sendto(respuesta.encode("utf-8"), direccion)
