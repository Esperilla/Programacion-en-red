#!/usr/bin/env python3
import socket

IP_SERVIDOR = "localhost"
PUERTO = 5050

cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

cliente.connect((IP_SERVIDOR, PUERTO))

print("Conectado al servidor eco. Escriba mensajes (vacio para salir).")

while True:
    mensaje = input("Usted dice: ")

    if mensaje == "":
        break

    cliente.send(mensaje.encode("utf-8"))

    eco = cliente.recv(1024).decode("utf-8")

    print("El servidor responde:", eco)

cliente.close()

print("Conexion cerrada.")