# P4: LA FILA (cliente UDP: consultar cuantos turnos van)

import socket

PUERTO = 5001

host = input("IP del servidor [127.0.0.1]: ").strip() or "127.0.0.1"

cliente = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
cliente.settimeout(3)

try:
    cliente.sendto("CUANTOS".encode("utf-8"), (host, PUERTO))
    datos, _ = cliente.recvfrom(1024)
    respuesta = datos.decode("utf-8").strip()      
    tipo, _, valor = respuesta.partition(">")
    if tipo == "van":
        print(f"Turnos asignados hasta ahora: {valor}")
    else:
        print(f"El servidor respondio: {respuesta}")
except socket.gaierror:
    print(f"ERROR: no se pudo resolver la direccion '{host}'.")
except socket.timeout:
    print("Sin respuesta en 3 segundos: el servidor no esta activo o se perdio el datagrama.")
except ConnectionResetError:
    print("ERROR: no hay servidor escuchando en ese puerto UDP.")
finally:
    cliente.close()
