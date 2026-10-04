# servidor_turnos.py
# Práctica 6 — Sistema de turnos LA FILA
# Universidad Veracruzana · Programación en Red · Unidad II
#
# Arquitectura:
#   · TCP (puerto 5000): un hilo por cliente conectado.
#     El cliente envía  TURNO>apodo\n
#     El servidor responde  turno>N\n  con el número consecutivo asignado.
#
#   · UDP (puerto 5001): un hilo dedicado al ciclo de escucha.
#     El cliente envía el datagrama  CUANTOS
#     El servidor responde  van>N\n  con el total de turnos asignados hasta ese momento.
#
#   · El contador de turnos es una sección crítica protegida con threading.Lock()
#     para garantizar que nunca se repitan ni se salten números.

import socket
import threading
import time

# ─────────────────────────────────────────────
#  Estado compartido entre todos los hilos
# ─────────────────────────────────────────────
contador_turnos = 0                # Variable compartida: total de turnos asignados
candado = threading.Lock()         # Candado para proteger la sección crítica


# ═══════════════════════════════════════════════════════════════════
#  FUNCIÓN: atender_cliente_tcp
#  Ejecutada en un hilo propio por cada cliente TCP que se conecta.
#  Protocolo:  recibe TURNO>apodo\n  →  responde turno>N\n
# ═══════════════════════════════════════════════════════════════════
def atender_cliente_tcp(conexion, direccion):
    print(f"[TCP] Cliente conectado desde {direccion}")
    buffer = ""   # Acumulador para el framing

    try:
        while True:
            # Recibir datos
            datos = conexion.recv(1024)

            if not datos:
                # El cliente cerró la conexión
                break

            # Acumular en el buffer y extraer mensajes completos (terminados en \n)
            buffer += datos.decode("utf-8")

            while "\n" in buffer:
                # Separar el primer mensaje completo del resto
                mensaje, buffer = buffer.split("\n", 1)
                mensaje = mensaje.strip()

                if mensaje.startswith("TURNO>"):
                    # Extraer el apodo del cliente (parte después de '>')
                    apodo = mensaje.split(">", 1)[1]

                    # ── Sección crítica ─────────────────────────────────
                    # Solo un hilo a la vez puede incrementar el contador
                    with candado:
                        global contador_turnos
                        contador_turnos += 1
                        numero_asignado = contador_turnos
                    # ── Fin de sección crítica ──────────────────────────

                    respuesta = f"turno>{numero_asignado}\n"
                    conexion.sendall(respuesta.encode("utf-8"))
                    print(f"[TCP] Turno {numero_asignado} asignado a '{apodo}' ({direccion})")

                else:
                    # Mensaje desconocido: informar al cliente
                    conexion.sendall("error>mensaje no reconocido\n".encode("utf-8"))

    except ConnectionResetError:
        # El cliente se desconectó abruptamente
        print(f"[TCP] Conexión con {direccion} cerrada abruptamente.")
    finally:
        conexion.close()
        print(f"[TCP] Hilo para {direccion} terminado.")


# ═══════════════════════════════════════════════════════════════════
#  FUNCIÓN: ciclo_udp
#  Ejecutada en un hilo dedicado; escucha datagramas UDP en puerto 5001.
#  Protocolo:  recibe CUANTOS  →  responde van>N\n
# ═══════════════════════════════════════════════════════════════════
def ciclo_udp(socket_udp):
    print("[UDP] Hilo de consultas UDP iniciado en puerto 5001.")

    while True:
        # recvfrom bloquea hasta recibir un datagrama y devuelve datos + dirección remota
        datos, direccion_cliente = socket_udp.recvfrom(1024)
        mensaje = datos.decode("utf-8").strip()

        if mensaje == "CUANTOS":
            # Lectura del contador: también se protege con candado para evitar
            # leer un valor inconsistente mientras otro hilo lo incrementa
            with candado:
                total = contador_turnos

            respuesta = f"van>{total}\n"
            socket_udp.sendto(respuesta.encode("utf-8"), direccion_cliente)
            print(f"[UDP] Consulta de {direccion_cliente} → van>{total}")

        else:
            # Datagrama desconocido: responder con error
            socket_udp.sendto("error>consulta no reconocida\n".encode("utf-8"), direccion_cliente)


# ═══════════════════════════════════════════════════════════════════
#  FUNCIÓN: main
#  Crea los sockets TCP y UDP, lanza los hilos y entra en el bucle
#  de aceptación de conexiones TCP.
# ═══════════════════════════════════════════════════════════════════
def main():
    # ── Socket TCP (puerto 5000) ────────────────────────────────────
    servidor_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # SO_REUSEADDR evita el error "address already in use" al reiniciar
    servidor_tcp.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    servidor_tcp.bind(("0.0.0.0", 5000))
    servidor_tcp.listen()
    print("[SERVIDOR] Escuchando TCP en puerto 5000...")

    # ── Socket UDP (puerto 5001) ────────────────────────────────────
    servidor_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    servidor_udp.bind(("0.0.0.0", 5001))
    print("[SERVIDOR] Escuchando UDP en puerto 5001...")

    # Lanzar el hilo dedicado para el ciclo de consultas UDP
    # daemon=True: el hilo se cierra automáticamente cuando el programa principal termina
    hilo_udp = threading.Thread(target=ciclo_udp, args=(servidor_udp,), daemon=True)
    hilo_udp.start()

    print("[SERVIDOR] Sistema de turnos LA FILA listo. Esperando clientes...\n")

    # ── Bucle principal: aceptar conexiones TCP ─────────────────────
    while True:
        # accept() bloquea hasta que un cliente se conecta
        conexion, direccion = servidor_tcp.accept()

        # Crear un hilo exclusivo para atender a este cliente
        hilo_cliente = threading.Thread(
            target=atender_cliente_tcp,
            args=(conexion, direccion),
            daemon=True     # daemon=True: no impide que el servidor cierre
        )
        hilo_cliente.start()

main()
