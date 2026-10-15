# =============================================================================
# Ejercicio 3 (parte A) - Servidor UDP de consulta de estado
# -----------------------------------------------------------------------------
# Escucha en el puerto 5001. Si recibe el datagrama "ESTADO" responde
# "servidor activo".
#
# Diferencias con TCP:
#   - SOCK_DGRAM en lugar de SOCK_STREAM.
#   - NO hay listen() ni accept(): no existen "conexiones".
#   - Cada datagrama es un mensaje completo (no hace falta buffer ni '\n').
#   - recvfrom() devuelve (datos, direccion_del_remitente) y se contesta con
#     sendto(datos, direccion), porque el socket no esta "conectado" a nadie.
# =============================================================================
import socket

HOST = "0.0.0.0"
PUERTO = 5001

servidor = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)   # UDP
servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
servidor.bind((HOST, PUERTO))
print(f"Servidor UDP escuchando en el puerto {PUERTO}...")

while True:
    # Espera un datagrama de cualquier cliente
    datos, direccion = servidor.recvfrom(1024)
    mensaje = datos.decode("utf-8").strip()   # strip quita espacios/saltos de linea sobrantes
    print(f"Datagrama de {direccion}: {mensaje!r}")

    if mensaje == "ESTADO":
        respuesta = "servidor activo"
    else:
        respuesta = "comando desconocido"

    # Se responde a la MISMA direccion de la que vino el datagrama
    servidor.sendto(respuesta.encode("utf-8"), direccion)
