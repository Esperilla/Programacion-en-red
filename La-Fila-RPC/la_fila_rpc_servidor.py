# =============================================================================
# Ejercicio 7 - LA FILA version RPC (servidor)
# -----------------------------------------------------------------------------
# Mismo sistema de turnos del Ejercicio 6, pero con XML-RPC: ya no hay sockets,
# encode ni framing a la vista; el middleware los hace por debajo.
#
# El servicio UDP de CUANTOS ya no hace falta: cuantos_van() es una funcion
# mas y, por debajo, todo viaja por TCP/HTTP.
#
# Servidor con hilos:
#   SimpleXMLRPCServer atiende una llamada a la vez. Se le mezcla
#   el manejo de peticiones con el manejo de hilos.
# Por eso el contador sigue necesitando threading.Lock: varios hilos lo modifican al mismo tiempo.
# =============================================================================
import threading
import time
from socketserver import ThreadingMixIn
from xmlrpc.server import SimpleXMLRPCServer, SimpleXMLRPCRequestHandler

HOST = "0.0.0.0"   
PUERTO = 5000

turno_actual = 0               
candado = threading.Lock()    


def registrar(texto):
    print(f"{time.strftime('%H:%M:%S')} | [{threading.current_thread().name}] {texto}")


def tomar_turno(apodo):
    """Asigna el siguiente turno de forma segura entre hilos."""
    global turno_actual
    apodo = str(apodo).strip()
    if not apodo:
        raise ValueError("el apodo no puede estar vacio")
    with candado:
        turno_actual += 1
        numero = turno_actual
    registrar(f"Turno {numero} asignado a '{apodo}'")
    return numero


def cuantos_van():
    """Devuelve el total de turnos asignados (leido con el Lock)."""
    with candado:
        total = turno_actual
    registrar(f"Consulta cuantos_van -> {total}")
    return total


# -----------------------------------------------------------------------------
# Servidor XML-RPC con un hilo por peticion
# -----------------------------------------------------------------------------
class ServidorRPCConHilos(ThreadingMixIn, SimpleXMLRPCServer):
    daemon_threads = True      
    allow_reuse_address = True 


class ManejadorSilencioso(SimpleXMLRPCRequestHandler):
    def log_message(self, formato, *args):
        pass                  


servidor = ServidorRPCConHilos((HOST, PUERTO), requestHandler=ManejadorSilencioso, allow_none=True)
servidor.register_function(tomar_turno, "tomar_turno")
servidor.register_function(cuantos_van, "cuantos_van")
servidor.register_introspection_functions()   

registrar(f"Servidor RPC en http://{HOST}:{PUERTO}  --  LA FILA esta abierta")
try:
    servidor.serve_forever()
except KeyboardInterrupt:
    registrar(f"Servidor detenido. Total de turnos asignados: {cuantos_van()}")
finally:
    servidor.server_close()
