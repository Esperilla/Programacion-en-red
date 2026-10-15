# =============================================================================
# Ejercicio 3 (parte B) - Cliente UDP que consulta el estado
# -----------------------------------------------------------------------------
# Envia "ESTADO" al servidor UDP y espera la respuesta A LO MAS 3 segundos.
#
# Como UDP no garantiza entrega, el datagrama (o la respuesta) puede perderse,
# o el servidor puede estar apagado. Sin un timeout, recvfrom() se quedaria
# esperando para siempre. settimeout(3) hace que, pasados 3 s sin respuesta,
# se lance la excepcion socket.timeout.
# =============================================================================
import socket

HOST = "127.0.0.1"   # IP del servidor UDP
PUERTO = 5001

cliente = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
cliente.settimeout(3)   # maximo 3 segundos de espera en recvfrom

try:
    # En UDP no hay connect: se indica el destino en cada sendto
    cliente.sendto("ESTADO".encode("utf-8"), (HOST, PUERTO))
    datos, direccion = cliente.recvfrom(1024)
    print(f"Respuesta de {direccion}: {datos.decode('utf-8')}")
except socket.timeout:
    # (en Python 3.10+ socket.timeout es lo mismo que TimeoutError)
    print("Sin respuesta en 3 segundos: el servidor no esta activo o se perdio el datagrama.")
except ConnectionResetError:
    # En Windows, si el puerto destino esta cerrado, el SO avisa con este error
    print("El servidor no esta escuchando en ese puerto.")
finally:
    cliente.close()
