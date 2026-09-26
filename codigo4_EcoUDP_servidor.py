#!/usr/bin/env python3
# ============================================================
# ECO UDP (SERVIDOR)
# datagram socket (socket de datagramas): SIN listen/accept.
# recvfrom() devuelve (datos, direccion); sendto() responde ahi.
# UDP es best-effort (de mejor esfuerzo): si un datagrama se
# pierde, NADIE se entera -- no hay retransmision.
# ============================================================
import socket
PUERTO = 51021
servidor = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # SOCK_DGRAM = UDP
servidor.bind(("0.0.0.0", PUERTO))
print("Eco UDP escuchando en el puerto", PUERTO, "...")
# OJO: no hay listen() ni accept(): en UDP nadie "acepta" nada
while True:
# recvfrom devuelve DOS cosas: los datos Y la direccion del remitente
    datos, direccion = servidor.recvfrom(1024)
    mensaje = datos.decode("utf-8") # RECIBIR = DECODE
    print("Datagrama de", direccion, ":", mensaje)
    if mensaje.strip() == "":
        break
    eco = "ECO> " + mensaje
# sendto necesita el DESTINO en cada envio, porque no hay conexion
    servidor.sendto(eco.encode("utf-8"), direccion) # ENVIAR = ENCODE
servidor.close()
print("Eco UDP terminado.")