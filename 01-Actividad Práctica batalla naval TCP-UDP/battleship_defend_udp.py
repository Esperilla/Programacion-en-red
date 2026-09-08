import socket


HOST = "10.67.0.120"
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

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as servidor:
        servidor.bind((host, port))
        print(f"Defensor UDP esperando ataques en {host}:{port}...")

        while True:
            datos, direccion = servidor.recvfrom(1024)
            ataque = datos.decode("utf-8")
            respuesta = atender_ataque(ataque, posiciones_barcos)
            servidor.sendto(respuesta.encode("utf-8"), direccion)
            print(
                f"Ataque de {direccion[0]}:{direccion[1]}: "
                f"{ataque.strip()} -> {respuesta}"
            )


if __name__ == "__main__":
    iniciar_servidor()
