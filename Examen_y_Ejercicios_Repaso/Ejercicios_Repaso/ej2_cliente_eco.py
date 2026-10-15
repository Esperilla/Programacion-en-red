# =============================================================================
# Ejercicio 2 - Cliente TCP
# -----------------------------------------------------------------------------
# Se conecta al servidor de eco (Ejercicio 1), envia "hola", "redes" y "adios",
# y muestra la respuesta a cada uno.
#
# Cada mensaje se manda terminado en '\n' porque ese es nuestro protocolo
# (el servidor separa los mensajes por salto de linea).
# =============================================================================
import socket

HOST = "127.0.0.1"   # IP del servidor (127.0.0.1 = este mismo equipo). Cambiar si esta en otra PC.
PUERTO = 5000

# create_connection hace socket() + connect() en un solo paso.
# Recibe una TUPLA (IP, puerto).
cliente = socket.create_connection((HOST, PUERTO))

buffer = ""   # mismo framing que el servidor: acumulamos hasta tener una linea

for mensaje in ["hola", "redes", "adios"]:
    # sendall exige bytes: encode al enviar
    cliente.sendall((mensaje + "\n").encode("utf-8"))

    # Leemos hasta tener una linea completa (la respuesta podria llegar en pedazos)
    while "\n" not in buffer:
        datos = cliente.recv(1024)
        if not datos:          # el servidor cerro la conexion
            break
        buffer += datos.decode("utf-8")   # decode al recibir

    respuesta, buffer = buffer.split("\n", 1)
    print(f"Enviado: {mensaje!r:10} -> Respuesta: {respuesta!r}")

cliente.close()   # cerrar la conexion; el servidor vera un recv() vacio
