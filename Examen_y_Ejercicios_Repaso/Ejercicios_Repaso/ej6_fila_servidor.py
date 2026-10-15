# =============================================================================
# Ejercicio 6 - Integrador: LA FILA (servidor)
# -----------------------------------------------------------------------------
# Sistema de turnos con DOS protocolos al mismo tiempo:
#
#   TCP, puerto 5000:   cliente -> "TURNO>apodo\n"     servidor -> "turno>N\n"
#   UDP, puerto 5001:   cliente -> "CUANTOS"           servidor -> "van>N\n"
#
# Organizacion con hilos:
#   - Hilo principal: acepta conexiones TCP.
#   - Un hilo por cada cliente TCP (atender_cliente).
#   - Un hilo para el ciclo UDP (ciclo_udp), porque recvfrom() bloquea y no
#     puede compartir hilo con accept().
#
# Contador compartido + Lock:
#   Varios hilos modifican la misma variable "turno_actual". La operacion
#   "leer valor, sumar 1, guardar" NO es atomica: si dos hilos la hacen a la vez
#   podrian leer el mismo valor y entregar el MISMO turno dos veces.
#   threading.Lock garantiza que solo un hilo a la vez entre a esa seccion
#   critica, asi los turnos salen consecutivos y sin repetirse.
#
# Tolerancia a fallos: cada hilo tiene su propio try/except, de modo que un
# cliente que falla o manda basura no tumba al servidor.
# =============================================================================
import socket
import threading
import time

HOST = "0.0.0.0"       # escuchar en todas las interfaces (para que otros equipos se conecten)
PUERTO_TCP = 5000
PUERTO_UDP = 5001

# ---- Estado compartido entre hilos ----
turno_actual = 0               # cuantos turnos se han asignado
candado = threading.Lock()     # protege a turno_actual


def registrar(texto):
    print(f"{time.strftime('%H:%M:%S')} | {texto}")


def tomar_turno():
    """Asigna el siguiente turno de forma segura entre hilos."""
    global turno_actual
    # "with candado" adquiere el Lock al entrar y lo libera al salir
    # (incluso si ocurre una excepcion). Solo un hilo a la vez ejecuta esto.
    with candado:
        turno_actual += 1
        return turno_actual


def total_asignados():
    """Lee el total de turnos asignados (tambien con el Lock para leer un valor consistente)."""
    with candado:
        return turno_actual


# -----------------------------------------------------------------------------
# Parte TCP: un hilo por cliente
# -----------------------------------------------------------------------------
def procesar_mensaje(mensaje):
    """Recibe una linea del cliente y devuelve la respuesta (sin el '\n')."""
    # partition(">") separa en (antes, ">", despues). Ej: "TURNO>ana" -> ("TURNO", ">", "ana")
    comando, separador, apodo = mensaje.strip().partition(">")
    if comando == "TURNO" and separador and apodo:
        numero = tomar_turno()
        registrar(f"Turno {numero} asignado a '{apodo}'")
        return f"turno>{numero}"
    # Mensaje con formato incorrecto: se responde con error pero NO se cierra nada
    return "error>formato esperado TURNO>apodo"


def atender_cliente(conexion, direccion):
    registrar(f"TCP conectado: {direccion}")
    buffer = ""
    try:
        while True:
            datos = conexion.recv(1024)
            if not datos:                       # el cliente cerro
                break
            buffer += datos.decode("utf-8")
            while "\n" in buffer:               # framing por '\n'
                mensaje, buffer = buffer.split("\n", 1)
                respuesta = procesar_mensaje(mensaje)
                conexion.sendall((respuesta + "\n").encode("utf-8"))
    except (ConnectionResetError, ConnectionAbortedError, BrokenPipeError):
        registrar(f"TCP {direccion} se desconecto abruptamente")
    except UnicodeDecodeError:
        registrar(f"TCP {direccion} envio datos que no son UTF-8")
    except Exception as e:
        # Red de seguridad: cualquier error inesperado solo termina ESTE hilo
        registrar(f"TCP {direccion} error inesperado: {e!r}")
    finally:
        conexion.close()
        registrar(f"TCP cerrado: {direccion}")


# -----------------------------------------------------------------------------
# Parte UDP: un solo hilo que atiende todos los datagramas
# -----------------------------------------------------------------------------
def ciclo_udp():
    sock_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock_udp.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock_udp.bind((HOST, PUERTO_UDP))
    registrar(f"UDP escuchando en el puerto {PUERTO_UDP}")

    while True:
        # El try esta DENTRO del while: si un datagrama provoca error,
        # se registra y el ciclo continua con el siguiente.
        try:
            datos, direccion = sock_udp.recvfrom(1024)
            mensaje = datos.decode("utf-8").strip()
            if mensaje == "CUANTOS":
                respuesta = f"van>{total_asignados()}\n"
                registrar(f"UDP {direccion} pregunto CUANTOS -> {respuesta.strip()}")
            else:
                respuesta = "error>comando esperado CUANTOS\n"
            sock_udp.sendto(respuesta.encode("utf-8"), direccion)
        except UnicodeDecodeError:
            registrar("UDP: datagrama no UTF-8 ignorado")
        except ConnectionResetError:
            # En Windows, si un cliente UDP ya cerro su puerto, el SO puede
            # reportar este error en el siguiente recvfrom. Se ignora.
            pass
        except Exception as e:
            registrar(f"UDP error inesperado: {e!r}")


# -----------------------------------------------------------------------------
# Programa principal
# -----------------------------------------------------------------------------
# 1) Arrancar el hilo UDP (daemon: muere al cerrar el programa)
threading.Thread(target=ciclo_udp, daemon=True, name="hilo-udp").start()

# 2) El hilo principal se encarga de TCP
servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
servidor.bind((HOST, PUERTO_TCP))
servidor.listen(10)
registrar(f"TCP escuchando en el puerto {PUERTO_TCP}  --  LA FILA esta abierta")

try:
    while True:
        conexion, direccion = servidor.accept()
        threading.Thread(target=atender_cliente, args=(conexion, direccion), daemon=True).start()
except KeyboardInterrupt:
    registrar(f"Servidor detenido. Total de turnos asignados: {total_asignados()}")
finally:
    servidor.close()
