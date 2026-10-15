# =============================================================================
# Ejercicio 5 (a) - Cliente TCP "endurecido" con try / except especificos
# -----------------------------------------------------------------------------
# Es el cliente del Ejercicio 2, pero ahora informa con un mensaje claro si:
#   - el servidor esta apagado              -> ConnectionRefusedError
#   - la IP / nombre no se puede resolver   -> socket.gaierror
#   - el servidor se va a media conversacion-> recv() vacio, ConnectionResetError,
#                                              ConnectionAbortedError, BrokenPipeError
#
# Se usan excepciones ESPECIFICAS (no un "except:" generico) para saber
# exactamente que fallo y dar un mensaje util.
# =============================================================================
import socket

HOST = "127.0.0.1"   # Prueba poner "no.existe.local" para ver el gaierror
PUERTO = 5000


class ServidorDesconectado(Exception):
    """Excepcion propia: el servidor cerro la conexion antes de responder."""


def recibir_linea(sock, buffer):
    """Lee del socket hasta tener una linea completa. Devuelve (linea, resto_del_buffer)."""
    while "\n" not in buffer:
        datos = sock.recv(1024)
        if not datos:
            # El servidor cerro "limpiamente" a media conversacion
            raise ServidorDesconectado()
        buffer += datos.decode("utf-8")
    return buffer.split("\n", 1)


cliente = None
try:
    # --- Fase de conexion: aqui pueden ocurrir gaierror y ConnectionRefusedError
    cliente = socket.create_connection((HOST, PUERTO), timeout=5)
    print(f"Conectado a {HOST}:{PUERTO}")

    # --- Fase de conversacion: aqui el servidor se puede ir
    buffer = ""
    for mensaje in ["hola", "redes", "adios"]:
        cliente.sendall((mensaje + "\n").encode("utf-8"))
        respuesta, buffer = recibir_linea(cliente, buffer)
        print(f"Enviado: {mensaje!r:10} -> Respuesta: {respuesta!r}")

except socket.gaierror:
    # gai = getaddrinfo: no se pudo traducir el nombre/IP a una direccion
    print(f"ERROR: no se pudo resolver la direccion '{HOST}'. Revise la IP o el nombre del servidor.")
except ConnectionRefusedError:
    # El equipo existe pero nadie escucha en ese puerto
    print(f"ERROR: el servidor en {HOST}:{PUERTO} esta apagado o no acepta conexiones.")
except socket.timeout:
    print("ERROR: el servidor tardo demasiado en responder.")
except (ServidorDesconectado, ConnectionResetError, ConnectionAbortedError, BrokenPipeError):
    # Cualquiera de estas = la conexion se rompio despues de haberse establecido
    print("ERROR: el servidor se desconecto a media conversacion.")
finally:
    # finally se ejecuta SIEMPRE (haya error o no): garantizamos cerrar el socket
    if cliente is not None:
        cliente.close()
        print("Conexion cerrada.")
