"""
Ejercicio 3 — Cliente que nunca falla
=======================================
Cliente TCP que pide al usuario la IP del servidor y maneja TODAS las salidas
de fallo:
  - Servidor apagado           -> ConnectionRefusedError
  - IP inválida / irresolvible -> socket.gaierror
  - Respuesta que nunca llega  -> TimeoutError
  - Desconexión a media conv.  -> ConnectionResetError / BrokenPipeError

En cada caso informa con un mensaje claro y termina con sys.exit(código ≠ 0).
Ninguna excepción llega al usuario como traceback.

Pistas:
  - Código 3 de la guía como base.
  - socket.gaierror aparece cuando la IP/nombre no se puede resolver.
  - sys.exit(1) termina con código de error.
"""

import socket
import sys


HOST_PREDETERMINADO = "127.0.0.1"
PORT = 5000
TIMEOUT = 5          # segundos máximos esperando respuesta


def obtener_ip() -> str:
    """Pide la IP al usuario; usa la predeterminada si el usuario no ingresa nada."""
    ip = input(f"Ingresa la IP del servidor [{HOST_PREDETERMINADO}]: ").strip()
    return ip if ip else HOST_PREDETERMINADO


def main() -> None:
    ip = obtener_ip()

    # ── Intento de conexión ────────────────────────────────────────────────────
    try:
        cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        cliente.settimeout(TIMEOUT)
        cliente.connect((ip, PORT))

    except socket.gaierror:
        print(f"[ERROR] No se pudo resolver la dirección '{ip}'. "
              "Verifica que sea una IP o nombre de host válido.")
        sys.exit(2)

    except ConnectionRefusedError:
        print(f"[ERROR] El servidor en {ip}:{PORT} está apagado o rechazó la conexión.")
        sys.exit(3)

    except TimeoutError:
        print(f"[ERROR] Tiempo de espera agotado al intentar conectar con {ip}:{PORT}.")
        sys.exit(4)

    except OSError as e:
        print(f"[ERROR] No se pudo conectar: {e}")
        sys.exit(1)

    # ── Conversación ──────────────────────────────────────────────────────────
    print(f"Conectado a {ip}:{PORT}. Escribe mensajes (vacío = salir).\n")

    try:
        with cliente:
            buffer = ""
            while True:
                mensaje = input("Tú -> ").strip()
                if not mensaje:
                    print("Cerrando conexión.")
                    break

                try:
                    cliente.sendall((mensaje + "\n").encode("utf-8"))
                except BrokenPipeError:
                    print("[ERROR] El servidor cerró la conexión mientras enviabas.")
                    sys.exit(5)

                try:
                    datos = cliente.recv(1024)
                    if not datos:
                        print("[AVISO] El servidor cerró la conexión.")
                        sys.exit(6)
                    print(f"Servidor -> {datos.decode('utf-8').strip()}")

                except TimeoutError:
                    print("[ERROR] El servidor no respondió en el tiempo esperado.")
                    sys.exit(7)

                except ConnectionResetError:
                    print("[ERROR] La conexión fue reiniciada inesperadamente.")
                    sys.exit(8)

    except KeyboardInterrupt:
        print("\nConversación interrumpida por el usuario.")


if __name__ == "__main__":
    main()
