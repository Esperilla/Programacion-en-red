# P2: Cliente TCP tolerante a fallos

import socket

HOST = "127.0.0.1"
PUERTO = 5000
MENSAJES = ["hola", "profe", "adios"]


class ServidorDesconectado(Exception):
    """El servidor cerro la conexion antes de enviar una respuesta."""


def recibir_linea(sock, buffer):
    """Lee hasta recibir una linea completa y devuelve la linea y el resto."""
    while "\n" not in buffer:
        datos = sock.recv(1024)
        if not datos:
            raise ServidorDesconectado()
        buffer += datos.decode("utf-8")   
    return buffer.split("\n", 1)


cliente = None
try:
    cliente = socket.create_connection((HOST, PUERTO), timeout=5)
    buffer = ""   

    for mensaje in MENSAJES:
        cliente.sendall((mensaje + "\n").encode("utf-8"))
        respuesta, buffer = recibir_linea(cliente, buffer)
        print(f"Enviado: {mensaje!r:10} -> Respuesta: {respuesta!r}")

except socket.gaierror:
    print(f"ERROR: no se pudo resolver la direccion '{HOST}'. Revise la IP o el nombre.")
except ConnectionRefusedError:
    print(f"ERROR: el servidor en {HOST}:{PUERTO} esta apagado o no acepta conexiones.")
except socket.timeout:
    print("ERROR: el servidor tardo demasiado en responder.")
except (ServidorDesconectado, ConnectionResetError, ConnectionAbortedError, BrokenPipeError):
    print("ERROR: el servidor se desconecto a media conversacion.")
finally:
    if cliente is not None:
        cliente.close()
