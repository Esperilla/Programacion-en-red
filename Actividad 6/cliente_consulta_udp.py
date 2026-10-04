# cliente_consulta_udp.py
# Práctica 6 — Sistema de turnos LA FILA
# Universidad Veracruzana · Programación en Red · Unidad II
#
# Uso:
#   python cliente_consulta_udp.py
#
# El cliente envía un datagrama UDP al servidor (puerto 5001) para consultar
# cuántos turnos se han asignado en total, SIN establecer una conexión.
# Protocolo:
#   Envía:   CUANTOS   (datagrama único)
#   Recibe:  van>N\n   (datagrama de respuesta)

import socket
import time


def main():
    # Solicitar la IP del servidor
    ip_servidor = input("IP del servidor [127.0.0.1]: ").strip()
    if not ip_servidor:
        # Valor por defecto para pruebas en la misma máquina
        ip_servidor = "127.0.0.1"

    # Crear socket UDP (SOCK_DGRAM, sin conexión)
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as cliente:

        # settimeout evita esperar indefinidamente si el datagrama se pierde
        # (en UDP no hay retransmisión automática)
        cliente.settimeout(5)

        try:
            # ── Enviar consulta al servidor ─────────────────────────
            # Un solo datagrama equivale a un mensaje completo en UDP
            cliente.sendto("CUANTOS".encode("utf-8"), (ip_servidor, 5001))

            # ── Recibir respuesta ───────────────────────────────────
            # recvfrom devuelve (datos, dirección_remitente)
            # Descartamos la dirección porque ya la conocemos
            datos, _ = cliente.recvfrom(1024)
            respuesta = datos.decode("utf-8").strip()

            if respuesta.startswith("van>"):
                # Extraer el total de turnos
                total = respuesta.split(">")[1]
                print(f"\n📋 Turnos asignados hasta ahora: {total}")
            else:
                print(f"[ERROR] Respuesta inesperada: {respuesta}")

        except TimeoutError:
            # El servidor no respondió dentro de los 5 segundos
            print("[ERROR] El servidor no respondió. Verifique la IP y que el servidor esté activo.")

main()
