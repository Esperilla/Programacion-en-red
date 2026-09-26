#!/usr/bin/env python3
# bloqueo_cliente.py -- se conecta y CALLA unos segundos antes de enviar
import socket
import time
ESPERA = 4 # segundos que el cliente permanece callado
cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
cliente.connect(("localhost", 5199))
print("cliente> conectado; voy a callar", ESPERA, "segundos antes de enviar...")
time.sleep(ESPERA)
cliente.send("ya llegue!".encode())
cliente.close()