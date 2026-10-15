# P4: LA FILA

import socket
import threading
import time

HOST = "0.0.0.0"      
PUERTO_TCP = 5000
PUERTO_UDP = 5001

turno_actual = 0               
candado = threading.Lock()    


def registrar(texto):
    print(f"{time.strftime('%H:%M:%S')} | {texto}")


def tomar_turno():
    """Asigna el siguiente turno de forma segura entre hilos."""
    global turno_actual

    with candado:
        turno_actual += 1
        return turno_actual


def total_asignados():
    """Lee el total de turnos asignados (tambien con el Lock para leer un valor consistente)."""
    with candado:
        return turno_actual


def procesar_mensaje(mensaje):
    """Recibe una linea del cliente y devuelve la respuesta (sin el '\n')."""
    comando, separador, apodo = mensaje.strip().partition(">")
    if comando == "TURNO" and separador and apodo:
        numero = tomar_turno()
        registrar(f"Turno {numero} asignado a '{apodo}'")
        return f"turno>{numero}"
    return "error>formato esperado TURNO>apodo"


def atender_cliente(conexion, direccion):
    registrar(f"TCP conectado: {direccion}")
    buffer = ""
    try:
        while True:
            datos = conexion.recv(1024)
            if not datos:                       
                break
            buffer += datos.decode("utf-8")
            while "\n" in buffer:              
                mensaje, buffer = buffer.split("\n", 1)
                respuesta = procesar_mensaje(mensaje)
                conexion.sendall((respuesta + "\n").encode("utf-8"))
    except (ConnectionResetError, ConnectionAbortedError, BrokenPipeError):
        registrar(f"TCP {direccion} se desconecto abruptamente")
    except UnicodeDecodeError:
        registrar(f"TCP {direccion} envio datos que no son UTF-8")
    except Exception as e:
        registrar(f"TCP {direccion} error inesperado: {e!r}")
    finally:
        conexion.close()
        registrar(f"TCP cerrado: {direccion}")


def ciclo_udp():
    sock_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock_udp.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock_udp.bind((HOST, PUERTO_UDP))
    registrar(f"UDP escuchando en el puerto {PUERTO_UDP}")

    while True:
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
            pass
        except Exception as e:
            registrar(f"UDP error inesperado: {e!r}")


threading.Thread(target=ciclo_udp, daemon=True, name="hilo-udp").start()

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
