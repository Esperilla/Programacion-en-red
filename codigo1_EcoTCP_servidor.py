#!/usr/bin/env python3
# ============================================================
# TCP ECHO SERVER (SERVIDOR ECO TCP)
# Programacion en Red · Universidad Veracruzana
# ------------------------------------------------------------
# Que hace: repite (echo = eco) todo lo que el cliente mande.
# Ciclo de vida del SERVER (servidor):
# socket() -> bind() -> listen() -> accept() -> recv/send -> close()
# Regla de oro: ENVIAR = ENCODE · RECIBIR = DECODE
# ============================================================
import socket
PUERTO = 5050 # port (puerto) acordado entre cliente y servidor

def armar_eco(mensaje, numero):
    return f"ECO #{numero}> {mensaje}"

# 1) socket(): crear el stream socket (socket de flujo) TCP sobre IPv4
servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
# 2) bind(): asociar el socket a (IP local, puerto)
# "0.0.0.0" = todas las interfaces de red de esta maquina
servidor.bind(("0.0.0.0", PUERTO))
# 3) listen(): pasar a modo escucha; 1 = backlog (cuantas conexiones esperan en fila)
servidor.listen(1)
print("Servidor eco escuchando en el puerto", PUERTO, "...")
# 4) accept(): BLOCKING (bloqueante) -- el programa SE DETIENE aqui
# hasta que un cliente se conecte. Devuelve DOS cosas:
# un socket NUEVO para hablar con ese cliente, y su direccion.
conexion, direccion = servidor.accept()
contador = 0
print("Cliente conectado desde", direccion)
while True:
    datos = conexion.recv(1024) # recv tambien es bloqueante
    if not datos: # datos vacios (b'') = el cliente cerro
        break
    mensaje = datos.decode("utf-8") # RECIBIR = DECODE
    print("Me llego:", mensaje)
    contador += 1
    eco = armar_eco(mensaje, contador)
    conexion.sendall(eco.encode("utf-8"))
# 5) close(): se cierran AMBOS sockets (la conversacion y el receptor)
conexion.close()
servidor.close()
print("Servidor eco terminado.")