"""
Ejercicio 5 — LA FILA tolerante a fallos (extensión de la Práctica 6)
=======================================================================
Extender el servidor de turnos de la Práctica 6 para que NINGÚN cliente pueda
tumbarlo. Los siguientes casos deben quedar registrados en consola y el
servidor debe seguir asignando turnos sin repetir números:
  1. Desconexiones abruptas (ConnectionResetError / BrokenPipeError).
  2. Mensajes que no siguen el protocolo (algo distinto de "TURNO>apodo").
  3. Bytes que no son UTF-8 válido (UnicodeDecodeError).

Pistas:
  - Código 4 de la guía como plantilla del hilo de atención.
  - Validar el mensaje con startswith("TURNO>") antes de procesarlo.
  - El contador compartido sigue protegido con threading.Lock.
Se evalúa:
  - Demostración con un cliente que envía basura a propósito.
  - Dos clientes legítimos reciben turnos consecutivos.
"""

import socket
import threading


HOST = "127.0.0.1"
PORT = 5000

# Estado compartido: contador de turno protegido con Lock
turno_actual = 0
candado = threading.Lock()


def siguiente_turno() -> int:
    """Devuelve el próximo número de turno de forma atómica."""
    global turno_actual
    with candado:
        turno_actual += 1
        return turno_actual


def atender_cliente(conexion: socket.socket, direccion: tuple) -> None:
    """
    Hilo por cliente. Tolera:
      - Desconexiones abruptas
      - Mensajes que no siguen el protocolo
      - Bytes no UTF-8
    """
    print(f"[+] Cliente conectado: {direccion}")

    try:
        with conexion:
            buffer = ""
            while True:
                datos = conexion.recv(1024)
                if not datos:
                    print(f"[-] {direccion}: desconexión limpia.")
                    break

                # ── Error 3: bytes no UTF-8 ────────────────────────────────
                try:
                    buffer += datos.decode("utf-8")
                except UnicodeDecodeError:
                    print(f"[!] {direccion}: bytes no válidos en UTF-8; se descartan.")
                    continue

                while "\n" in buffer:
                    linea, buffer = buffer.split("\n", 1)
                    linea = linea.strip()
                    if not linea:
                        continue

                    # ── Error 2: protocolo incorrecto ──────────────────────
                    if not linea.startswith("TURNO>"):
                        print(f"[!] {direccion}: mensaje fuera de protocolo -> '{linea}'")
                        conexion.sendall(b"ERROR>protocolo incorrecto\n")
                        continue

                    # ── Camino feliz ───────────────────────────────────────
                    apodo = linea.split(">", 1)[1].strip()
                    if not apodo:
                        conexion.sendall(b"ERROR>apodo vacio\n")
                        continue

                    numero = siguiente_turno()
                    respuesta = f"TURNO>{numero}>{apodo}\n"
                    print(f"[=] {direccion}: turno {numero} asignado a '{apodo}'.")
                    conexion.sendall(respuesta.encode("utf-8"))

    # ── Error 1: desconexiones abruptas ────────────────────────────────────
    except ConnectionResetError:
        print(f"[-] {direccion}: conexión reiniciada abruptamente.")
    except BrokenPipeError:
        print(f"[-] {direccion}: pipe roto al enviar respuesta.")
    finally:
        print(f"[x] {direccion}: hilo terminado.")


def main() -> None:
    try:
        servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        servidor.bind((HOST, PORT))
        servidor.listen()
        print(f"LA FILA tolerante a fallos escuchando en {HOST}:{PORT}")
        print("Protocolo de solicitud: TURNO>apodo")
        print("Presiona Ctrl+C para detener.\n")

        while True:
            conexion, direccion = servidor.accept()
            hilo = threading.Thread(
                target=atender_cliente,
                args=(conexion, direccion),
                daemon=True,
            )
            hilo.start()

    except OSError as e:
        print(f"[ERROR] No se pudo iniciar el servidor en {HOST}:{PORT} -> {e}")
    except KeyboardInterrupt:
        print("\nServidor detenido por el usuario.")
    finally:
        servidor.close()


if __name__ == "__main__":
    main()
