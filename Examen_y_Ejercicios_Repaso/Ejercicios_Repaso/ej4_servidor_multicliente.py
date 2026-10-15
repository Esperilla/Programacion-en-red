# =============================================================================
# Ejercicio 4 - Servidor de eco MULTICLIENTE con hilos
# -----------------------------------------------------------------------------
# Problema del Ejercicio 1: mientras atiende a un cliente (ciclo interno de
# recv), el servidor NO vuelve a accept(), asi que un segundo cliente se queda
# esperando.
#
# Solucion: el hilo principal SOLO acepta conexiones, y cada conexion aceptada
# se atiende en su propio hilo (threading.Thread). Asi varios clientes son
# atendidos al mismo tiempo sin esperarse unos a otros.
#
# Prueba: abrir dos terminales y ejecutar ej2_cliente_eco.py en ambas (o
# conectarse con dos clientes a la vez); los dos reciben su eco.
# =============================================================================
import socket
import threading

HOST = "0.0.0.0"
PUERTO = 5000


def atender_cliente(conexion, direccion):
    """Se ejecuta en un hilo aparte: atiende a UN cliente de principio a fin."""
    print(f"[{threading.current_thread().name}] Atendiendo a {direccion}")
    buffer = ""
    while True:
        datos = conexion.recv(1024)
        if not datos:                      # recv vacio = el cliente cerro
            break
        buffer += datos.decode("utf-8")
        while "\n" in buffer:              # framing por salto de linea
            mensaje, buffer = buffer.split("\n", 1)
            print(f"[{direccion}] {mensaje}")
            conexion.sendall((mensaje + "\n").encode("utf-8"))
    conexion.close()
    print(f"Cliente {direccion} desconectado")


servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
servidor.bind((HOST, PUERTO))
servidor.listen(5)
print(f"Servidor multicliente escuchando en el puerto {PUERTO}...")

# El hilo principal solo hace accept() y lanza hilos
while True:
    conexion, direccion = servidor.accept()
    hilo = threading.Thread(
        target=atender_cliente,          # funcion que ejecutara el hilo
        args=(conexion, direccion),      # argumentos (tupla)
        daemon=True,                     # daemon: el hilo muere si el programa principal termina (Ctrl+C)
    )
    hilo.start()                         # arranca el hilo y el while vuelve de inmediato a accept()
    # active_count incluye al hilo principal, por eso se resta 1
    print(f"Clientes activos: {threading.active_count() - 1}")
