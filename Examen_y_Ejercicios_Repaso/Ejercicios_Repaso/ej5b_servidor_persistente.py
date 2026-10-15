# =============================================================================
# Ejercicio 5 (b) - Servidor multicliente PERSISTENTE (tolerante a fallos)
# -----------------------------------------------------------------------------
# Es el servidor del Ejercicio 4 con manejo de errores:
#   - Si un cliente se desconecta abruptamente (se cierra la ventana, se cae la
#     red, Ctrl+C), recv() lanza ConnectionResetError. Ese error ocurre DENTRO
#     del hilo de ese cliente, asi que el try/except vive en atender_cliente:
#     solo termina ese hilo y los demas clientes siguen siendo atendidos.
#   - finally registra SIEMPRE el cierre de cada conexion (normal o por error).
# =============================================================================
import socket
import threading
import time

HOST = "0.0.0.0"
PUERTO = 5000


def registrar(texto):
    """Imprime un mensaje con la hora, como un pequeno log."""
    print(f"{time.strftime('%H:%M:%S')} | {texto}")


def atender_cliente(conexion, direccion):
    registrar(f"Conexion abierta: {direccion}")
    buffer = ""
    try:
        while True:
            datos = conexion.recv(1024)
            if not datos:
                registrar(f"{direccion} cerro la conexion normalmente")
                break
            buffer += datos.decode("utf-8")
            while "\n" in buffer:
                mensaje, buffer = buffer.split("\n", 1)
                conexion.sendall((mensaje + "\n").encode("utf-8"))
    except (ConnectionResetError, ConnectionAbortedError, BrokenPipeError):
        # Desconexion abrupta: se registra y el hilo termina sin tumbar al servidor
        registrar(f"{direccion} se desconecto abruptamente")
    except UnicodeDecodeError:
        # El cliente mando bytes que no son UTF-8 valido
        registrar(f"{direccion} envio datos que no son UTF-8")
    finally:
        # Siempre se ejecuta: liberamos el socket y dejamos constancia del cierre
        conexion.close()
        registrar(f"Conexion cerrada: {direccion}")


servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
servidor.bind((HOST, PUERTO))
servidor.listen(5)
registrar(f"Servidor persistente escuchando en el puerto {PUERTO}")

try:
    while True:
        conexion, direccion = servidor.accept()
        threading.Thread(target=atender_cliente, args=(conexion, direccion), daemon=True).start()
except KeyboardInterrupt:
    # Ctrl+C en la consola del servidor: salir de forma ordenada
    registrar("Servidor detenido por el usuario")
finally:
    servidor.close()
