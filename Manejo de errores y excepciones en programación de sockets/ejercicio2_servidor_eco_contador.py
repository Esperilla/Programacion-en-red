"""
Ejercicio 2 — Servidor de eco con contador por cliente
=======================================================
Extender el servidor de eco de la guía anterior para que cada respuesta lleve
el número de mensajes que ese cliente ha enviado:
  - Cliente manda: hola\n  -> servidor responde: 1>hola
  - Cliente manda: otro\n  -> servidor responde: 2>otro
  - Y así sucesivamente...

Pistas:
  - El contador es una variable LOCAL de atender_cliente (entero que se
    incrementa por línea recibida).
  - La respuesta se construye con un f-string.
Se evalúa: conteo independiente por cliente; dos clientes simultáneos NO
comparten contador.
"""

import socket
import threading


HOST = "127.0.0.1"
PORT = 5000


def atender_cliente(conexion: socket.socket, direccion: tuple) -> None:
    """Atiende a un cliente con eco numerado. El contador es local -> independiente."""
    contador = 0          # <-- variable LOCAL: cada hilo tiene la suya
    print(f"[+] Cliente conectado: {direccion}")

    try:
        with conexion:
            buffer = ""
            while True:
                datos = conexion.recv(1024)
                if not datos:
                    break                         # cliente cerró la conexión

                buffer += datos.decode("utf-8")

                while "\n" in buffer:
                    linea, buffer = buffer.split("\n", 1)
                    linea = linea.strip()
                    if not linea:
                        continue

                    contador += 1                 # incrementar contador local
                    respuesta = f"{contador}>{linea}\n"
                    conexion.sendall(respuesta.encode("utf-8"))

    except ConnectionResetError:
        print(f"[-] {direccion}: conexión reiniciada por el cliente.")
    except BrokenPipeError:
        print(f"[-] {direccion}: pipe roto al enviar respuesta.")
    finally:
        print(f"[=] {direccion}: conexión cerrada (envió {contador} mensaje(s)).")


def main() -> None:
    try:
        servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        servidor.bind((HOST, PORT))
        servidor.listen()
        print(f"Servidor de eco con contador escuchando en {HOST}:{PORT}")
        print("Conecta clientes con:  telnet 127.0.0.1 5000")
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
