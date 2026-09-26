#!/usr/bin/env python3
# framing_servidor.py -- recepcion correcta con delimitador "\n"
# Problema que resuelve: TCP es un flujo de bytes; un recv(1024)
# puede traer mensajes PEGADOS o PARTIDOS.
import socket
PUERTO = 5061
servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
servidor.bind(("localhost", PUERTO))
servidor.listen(1)
print("servidor framing> escuchando en", PUERTO)
conexion, direccion = servidor.accept()
print("servidor framing> cliente:", direccion)
buffer = "" # aqui se ACUMULA lo que va llegando
while True:
    datos = conexion.recv(1024)
    if not datos: # el cliente cerro la conexion
        break
    buffer += datos.decode("utf-8")
# mientras haya un delimitador en el buffer, hay un mensaje COMPLETO
    while "\n" in buffer:
        mensaje, buffer = buffer.split("\n", 1) # corta el primer mensaje
        print("servidor framing> mensaje completo recibido:", mensaje)
conexion.close()
servidor.close()