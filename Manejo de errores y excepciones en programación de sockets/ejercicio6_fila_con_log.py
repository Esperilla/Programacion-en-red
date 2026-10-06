"""
Ejercicio 6 — Registro de errores en archivo (desafío)
=======================================================
Agregar al servidor del Ejercicio 5 un registro (log) en un archivo de texto.
Cada error escribe una línea con:
    fecha hora (IP, puerto) descripción
Ejemplo:
    2026-10-06 10:32:15 (187.141.12.9, 51020) conexión reiniciada por el cliente

Pistas:
  - time.strftime("%Y-%m-%d %H:%M:%S") da la marca de tiempo.
  - El archivo se abre en modo "a" (agregar) protegido con el MISMO Lock
    del contador (reutilizamos candado) para que ninguna línea quede
    incompleta aunque dos hilos registren al mismo tiempo.
Se evalúa:
  - El archivo crece con cada error provocado en la demostración.
  - Ninguna línea queda incompleta aunque dos hilos registren simultáneamente.
"""

import socket
import threading
import time


HOST        = "127.0.0.1"
PORT        = 5000
LOG_ARCHIVO = "errores_servidor.log"

# Estado compartido: contador y archivo de log protegidos con el MISMO Lock
turno_actual = 0
candado      = threading.Lock()


# ── Funciones auxiliares ───────────────────────────────────────────────────────

def siguiente_turno() -> int:
    """Devuelve el próximo número de turno de forma atómica."""
    global turno_actual
    with candado:
        turno_actual += 1
        return turno_actual


def registrar_error(direccion: tuple, descripcion: str) -> None:
    """
    Escribe una línea de error en el archivo de log.
    Usa el mismo candado del contador para garantizar que ninguna línea
    quede incompleta aunque dos hilos escriban al mismo tiempo.
    """
    marca = time.strftime("%Y-%m-%d %H:%M:%S")
    ip, puerto = direccion
    linea = f"{marca} ({ip}, {puerto}) {descripcion}\n"

    with candado:          # mismo Lock -> acceso atómico al archivo
        with open(LOG_ARCHIVO, "a", encoding="utf-8") as f:
            f.write(linea)

    # También mostramos en consola para la demostración en clase
    print(f"[LOG] {linea.strip()}")


# ── Hilo por cliente ───────────────────────────────────────────────────────────

def atender_cliente(conexion: socket.socket, direccion: tuple) -> None:
    """
    Igual que Ejercicio 5 pero con registro de errores en archivo.
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

                try:
                    buffer += datos.decode("utf-8")
                except UnicodeDecodeError:
                    desc = "bytes no válidos en UTF-8 recibidos"
                    registrar_error(direccion, desc)
                    continue

                while "\n" in buffer:
                    linea, buffer = buffer.split("\n", 1)
                    linea = linea.strip()
                    if not linea:
                        continue

                    if not linea.startswith("TURNO>"):
                        desc = f"protocolo incorrecto: '{linea}'"
                        registrar_error(direccion, desc)
                        conexion.sendall(b"ERROR>protocolo incorrecto\n")
                        continue

                    apodo = linea.split(">", 1)[1].strip()
                    if not apodo:
                        registrar_error(direccion, "apodo vacío en solicitud TURNO")
                        conexion.sendall(b"ERROR>apodo vacío\n")
                        continue

                    numero = siguiente_turno()
                    respuesta = f"TURNO>{numero}>{apodo}\n"
                    print(f"[=] {direccion}: turno {numero} -> '{apodo}'.")
                    conexion.sendall(respuesta.encode("utf-8"))

    except ConnectionResetError:
        registrar_error(direccion, "conexión reiniciada por el cliente")
    except BrokenPipeError:
        registrar_error(direccion, "pipe roto al intentar enviar respuesta")
    finally:
        print(f"[x] {direccion}: hilo terminado.")


# ── Punto de entrada ──────────────────────────────────────────────────────────

def main() -> None:
    print(f"Registro de errores -> {LOG_ARCHIVO}")
    try:
        servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        servidor.bind((HOST, PORT))
        servidor.listen()
        print(f"LA FILA con log de errores escuchando en {HOST}:{PORT}")
        print("Protocolo: TURNO>apodo  |  Ctrl+C para detener.\n")

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
