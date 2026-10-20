# =============================================================================
# Ejercicio 7 - LA FILA version RPC (cliente)
# -----------------------------------------------------------------------------
# Une en un solo cliente lo que antes eran ej6_fila_cliente_tcp.py (TURNO) y
# ej6_fila_cliente_udp.py (CUANTOS): ahora son dos llamadas a funcion.
#
# ServerProxy es el stub: servidor.tomar_turno("ana") empaca (marshalling),
# envia por HTTP, espera y desempaca la respuesta. Sin sockets a la vista.
# =============================================================================
import socket
import xmlrpc.client

PUERTO = 5000

host = input("IP del servidor [127.0.0.1]: ").strip() or "127.0.0.1"
apodo = input("Tu apodo: ").strip() or "anonimo"

servidor = xmlrpc.client.ServerProxy(f"http://{host}:{PUERTO}")
socket.setdefaulttimeout(5)    # para que una llamada no se quede colgada

try:
    turno = servidor.tomar_turno(apodo)      
    print(f"{apodo}, tu turno es el numero {turno}")

    van = servidor.cuantos_van()
    print(f"Turnos asignados hasta ahora: {van}")

    # El error se genera del lado del servidor y llega aqui como Fault.
    servidor.funcion_que_no_existe()

except xmlrpc.client.Fault as f:
    print(f"Fault del servidor (codigo {f.faultCode}): {f.faultString}")
except ConnectionRefusedError:
    print(f"ERROR: el servidor en {host}:{PUERTO} esta apagado.")
except socket.gaierror:
    print(f"ERROR: no se pudo resolver la direccion '{host}'.")
except socket.timeout:
    print("ERROR: el servidor no respondio a tiempo.")
except (ConnectionResetError, ConnectionAbortedError):
    print("ERROR: el servidor se desconecto a media llamada.")
except xmlrpc.client.ProtocolError as e:
    print(f"ERROR HTTP {e.errcode}: {e.errmsg}")
