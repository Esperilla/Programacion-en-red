"""
Ejercicio 4 — Consulta UDP con reintentos y espera creciente
=============================================================
Aplicar la función consultar() del Código 5 al protocolo de LA FILA:
  - Enviar "CUANTOS" al servidor UDP de turnos.
  - Si no responde, reintentar hasta tres veces DUPLICANDO la espera:
      Intento 1 -> espera 1 s  (2^0)
      Intento 2 -> espera 2 s  (2^1)
      Intento 3 -> espera 4 s  (2^2)
  - El None final se traduce en un mensaje claro, no en un error.

Pistas:
  - Espera: time.sleep(2 ** (intento - 1))
  - El None final debe traducirse en un mensaje y no en un error.
Se evalúa:
  - Con servidor apagado -> se observan los 3 intentos con sus pausas.
  - Encendiendo el servidor a medio ciclo -> la consulta tiene éxito.
"""

import socket
import time


HOST_SERVIDOR = "127.0.0.1"
PORT_SERVIDOR = 5001
MAX_REINTENTOS = 3
TIMEOUT_SEG    = 2        # tiempo máximo por cada recvfrom()


def consultar(servidor: tuple, mensaje: str, reintentos: int = MAX_REINTENTOS):
    """
    Envía una consulta UDP y reintenta si no hay respuesta.
    Espera creciente: 2^(intento-1) segundos entre intentos.
    Retorna la respuesta como str, o None si se agotaron los intentos.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as cliente:
        cliente.settimeout(TIMEOUT_SEG)

        for intento in range(1, reintentos + 1):
            espera = 2 ** (intento - 1)           # 1, 2, 4 segundos
            try:
                cliente.sendto((mensaje + "\n").encode("utf-8"), servidor)
                datos, _ = cliente.recvfrom(1024)
                return datos.decode("utf-8").strip()    # ¡éxito! -> salir ya

            except TimeoutError:
                print(f"  Intento {intento}/{reintentos}: sin respuesta "
                      f"(esperando {espera}s antes de reintentar...)")
                time.sleep(espera)

    return None     # se agotaron todos los intentos


def main() -> None:
    print("Consultando cuántas personas hay en la fila...")
    respuesta = consultar((HOST_SERVIDOR, PORT_SERVIDOR), "CUANTOS")

    if respuesta is not None:
        print(f"El servidor respondió: {respuesta}")
    else:
        print("El servidor de la fila no está disponible. Inténtalo más tarde.")


if __name__ == "__main__":
    main()
