import socket

HOST = "0.0.0.0"
PORT = 5050

POSICIONES_BARCOS = {"A1", "B2", "C3"}


def atender_ataque(mensaje, posiciones_barcos):
    coordenada = mensaje.strip().upper()
    if coordenada in posiciones_barcos:
        posiciones_barcos.remove(coordenada)
        return "TOCADO"
    return "AGUA"


def iniciar_servidor(host=HOST, port=PORT):
    posiciones_barcos = set(POSICIONES_BARCOS)

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as servidor:
        servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        servidor.bind((host, port))
        servidor.listen(1)
        print(f"Defensor esperando ataques en {host}:{port}...")

        conexion, direccion = servidor.accept()
        with conexion:
            print(f"Atacante conectado desde {direccion[0]}:{direccion[1]}")
            while True:
                datos = conexion.recv(1024)
                if not datos:
                    break

                ataque = datos.decode("utf-8")
                respuesta = atender_ataque(ataque, posiciones_barcos)
                conexion.sendall(respuesta.encode("utf-8"))
                print(f"Ataque: {ataque.strip()} -> {respuesta}")


if __name__ == "__main__":
    iniciar_servidor()
