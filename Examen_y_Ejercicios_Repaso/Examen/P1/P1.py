# P1: Servidor eco TCP multicliente con hilos

import socket
import threading

HOST = "0.0.0.0"
PUERTO = 5000


def atender_cliente(conexion, direccion):
    print(f"[{threading.current_thread().name}] Atendiendo a {direccion}")
    buffer = b""

    try:
        while True:
            datos = conexion.recv(4096)
            if not datos: 
                break

            buffer += datos
            while b"\n" in buffer: 
                mensaje_bytes, buffer = buffer.split(b"\n", 1)
                mensaje = mensaje_bytes.decode("utf-8")
                print(f"[{direccion}] {mensaje}")
                conexion.sendall((mensaje + "\n").encode("utf-8"))
    except (ConnectionError, OSError, UnicodeDecodeError) as exc:
        print(f"[{direccion}] Error en la conexión: {exc}")
    finally:
        conexion.close()
        print(f"Cliente {direccion} desconectado")


servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
servidor.bind((HOST, PUERTO))
servidor.listen(5)
print(f"Servidor multicliente escuchando en el puerto {PUERTO}...")

while True:
    conexion, direccion = servidor.accept()
    hilo = threading.Thread(
        target=atender_cliente,
        args=(conexion, direccion),
        daemon=True,
    )
    hilo.start()
    print(f"Clientes activos: {threading.active_count() - 1}")
