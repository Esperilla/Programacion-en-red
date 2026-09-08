import socket


HOST = "10.67.0.120"
PORT = 5050


def atacar(host=HOST, port=PORT):
    direccion_defensor = (host, port)

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as cliente:
        print(f"Atacante UDP listo para enviar ataques a {host}:{port}")
        print("Escribe una coordenada o 'salir' para terminar.")

        while True:
            coordenada = input("Ataque: ").strip()
            if coordenada.lower() == "salir":
                break
            if not coordenada:
                continue

            cliente.sendto(
                coordenada.upper().encode("utf-8"),
                direccion_defensor,
            )
            datos, _ = cliente.recvfrom(1024)
            respuesta = datos.decode("utf-8")
            print(f"Respuesta del defensor: {respuesta}")


if __name__ == "__main__":
    atacar()
