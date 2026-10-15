# P4: LA FILA (cliente TCP: pedir turno)

import socket

PUERTO = 5000

host = input("IP del servidor [127.0.0.1]: ").strip() or "127.0.0.1"
apodo = input("Tu apodo: ").strip() or "anonimo"

cliente = None
try:
    cliente = socket.create_connection((host, PUERTO), timeout=5)
    cliente.sendall(f"TURNO>{apodo}\n".encode("utf-8"))

    buffer = ""
    while "\n" not in buffer:
        datos = cliente.recv(1024)
        if not datos:
            raise ConnectionResetError   
        buffer += datos.decode("utf-8")
    respuesta = buffer.split("\n", 1)[0]         

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
