# cliente_turno_tcp.py
# Práctica 6 — Sistema de turnos LA FILA
# Universidad Veracruzana · Programación en Red · Unidad II
#
# Uso:
#   python cliente_turno_tcp.py
#
# El cliente se conecta al servidor TCP (puerto 5000), envía su apodo
# y recibe el número de turno asignado.
# Protocolo:
#   Envía:   TURNO>apodo\n
#   Recibe:  turno>N\n

import socket
import time


def main():
    # Solicitar la IP del servidor (permite pruebas con equipos reales en la misma red)
    ip_servidor = input("IP del servidor [127.0.0.1]: ").strip()
    if not ip_servidor:
        # Valor por defecto para pruebas en la misma máquina
        ip_servidor = "127.0.0.1"

    # Solicitar el apodo del cliente
    apodo = input("Tu apodo: ").strip()
    if not apodo:
        apodo = "Anonimo"

    print(f"\nConectando al servidor {ip_servidor}:5000 ...")

    # Abrir conexión TCP; 'with' garantiza el cierre aunque ocurra un error
    with socket.create_connection((ip_servidor, 5000)) as conexion:
        # ── Enviar solicitud de turno ──────────────────────────────
        # Formato: TURNO>apodo\n  (texto plano UTF-8, delimitado por \n)
        mensaje = f"TURNO>{apodo}\n"
        conexion.sendall(mensaje.encode("utf-8"))

        # ── Recibir respuesta del servidor ──────────────────────────
        # Acumular en buffer por si recv() devuelve datos parciales
        buffer = ""
        while "\n" not in buffer:
            trozo = conexion.recv(1024).decode("utf-8")
            if not trozo:
                # El servidor cerró la conexión inesperadamente
                break
            buffer += trozo

        # Extraer el primer mensaje completo (hasta \n)
        respuesta = buffer.split("\n")[0].strip()

        if respuesta.startswith("turno>"):
            # Extraer el número asignado
            numero = respuesta.split(">")[1]
            print(f"\n✔ Tu turno es el número: {numero}")
            print(f"  Apodo registrado: {apodo}")
        else:
            # El servidor respondió con un mensaje inesperado
            print(f"[ERROR] Respuesta inesperada del servidor: {respuesta}")

    print("\nConexión cerrada.")

main()
