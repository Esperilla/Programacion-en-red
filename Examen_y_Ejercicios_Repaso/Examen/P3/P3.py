# P3: Cliente UDP con reintentos

import socket
import time

HOST = "127.0.0.1"   
PUERTO = 5001

cliente = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
cliente.settimeout(3)   

esperas_entre_reintentos = [1, 2, 4]
intentos_totales = 1 + len(esperas_entre_reintentos)  

try:
    for intento in range(1, intentos_totales + 1):
        try:
            cliente.sendto("ESTADO".encode("utf-8"), (HOST, PUERTO))
            datos, direccion = cliente.recvfrom(1024)
            print(f"Respuesta de {direccion}: {datos.decode('utf-8')}")
            break
        except (socket.timeout, ConnectionResetError):
            if intento == intentos_totales:
                print(
                    "Sin respuesta tras 4 intentos (espera de 3 s por intento). "
                    "El servidor no esta activo o se perdieron los datagramas."
                )
            else:
                espera = esperas_entre_reintentos[intento - 1]
                print(f"Intento {intento} sin respuesta. Reintentando en {espera} s...")
                time.sleep(espera)
finally:
    cliente.close()
