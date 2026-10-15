# =============================================================================
# Ejercicio 6 - LA FILA (cliente TCP: pedir turno)
# -----------------------------------------------------------------------------
# Envia "TURNO>apodo\n" y muestra el turno asignado ("turno>N").
# Incluye el manejo de errores del Ejercicio 5 (a).
#
# Para la validacion: ejecutar este cliente en DOS equipos al mismo tiempo,
# escribiendo la IP del equipo donde corre ej6_fila_servidor.py.
# =============================================================================
import socket

PUERTO = 5000

# input() permite escribir la IP del servidor; Enter = este mismo equipo
host = input("IP del servidor [127.0.0.1]: ").strip() or "127.0.0.1"
apodo = input("Tu apodo: ").strip() or "anonimo"

cliente = None
try:
    cliente = socket.create_connection((host, PUERTO), timeout=5)
    cliente.sendall(f"TURNO>{apodo}\n".encode("utf-8"))

    # Leer hasta tener la linea completa de respuesta
    buffer = ""
    while "\n" not in buffer:
        datos = cliente.recv(1024)
        if not datos:
            raise ConnectionResetError   # el servidor cerro antes de contestar
        buffer += datos.decode("utf-8")
    respuesta = buffer.split("\n", 1)[0]          # ej. "turno>7"

    # Separar la respuesta del protocolo: "turno>7" -> ("turno", ">", "7")
    tipo, _, valor = respuesta.partition(">")
    if tipo == "turno":
        print(f"{apodo}, tu turno es el numero {valor}")
    else:
        print(f"El servidor respondio: {respuesta}")

except socket.gaierror:
    print(f"ERROR: no se pudo resolver la direccion '{host}'.")
except ConnectionRefusedError:
    print(f"ERROR: el servidor en {host}:{PUERTO} esta apagado.")
except socket.timeout:
    print("ERROR: el servidor no respondio a tiempo.")
except (ConnectionResetError, ConnectionAbortedError, BrokenPipeError):
    print("ERROR: el servidor se desconecto a media conversacion.")
finally:
    if cliente is not None:
        cliente.close()
