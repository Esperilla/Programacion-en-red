import socket

HOST = "127.0.0.1"
PORT = 5050


def atacar(host=HOST, port=PORT):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as cliente:
        cliente.connect((host, port))
        print(f"Conectado al defensor en {host}:{port}")
        print("Escribe una coordenada o 'salir' para terminar.")

        while True:
            coordenada = input("Ataque: ").strip()
            if coordenada.lower() == "salir":
                break
            if not coordenada:
                continue

            cliente.sendall(coordenada.upper().encode("utf-8"))
            datos = cliente.recv(1024)
            if not datos:
                print("El defensor cerro la conexion.")
                break

            respuesta = datos.decode("utf-8")
            print(f"Respuesta del defensor: {respuesta}")


if __name__ == "__main__":
    atacar()
