# =============================================================================
# Ejercicio 1 - Servidor TCP de eco
# -----------------------------------------------------------------------------
# Escucha en el puerto 5000 y le regresa al cliente cada LINEA que recibe.
#
# Ciclo de vida de un servidor TCP:
#     socket()  ->  bind()  ->  listen()  ->  accept()  ->  recv()/sendall()  ->  close()
#
# "Framing" por salto de linea:
#   TCP es un FLUJO de bytes, no respeta "mensajes". Un recv() puede traer medio
#   mensaje, uno completo o varios juntos. Por eso acumulamos lo recibido en un
#   buffer y solo procesamos lo que ya tenga un '\n' (un mensaje completo).
# =============================================================================
import socket

HOST = "0.0.0.0"   # 0.0.0.0 = escuchar en todas las interfaces de red del equipo
PUERTO = 5000

# 1) Crear el socket: AF_INET = IPv4, SOCK_STREAM = TCP
servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# SO_REUSEADDR permite volver a usar el puerto inmediatamente despues de
# reiniciar el servidor (si no, el SO lo deja "ocupado" unos segundos en TIME_WAIT
# y bind() falla con "Address already in use").
servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# 2) bind: asociar el socket a una IP y puerto (se pasa como TUPLA)
servidor.bind((HOST, PUERTO))

# 3) listen: el socket queda en modo "escucha"; 5 = conexiones en cola de espera
servidor.listen(5)
print(f"Servidor de eco escuchando en el puerto {PUERTO}...")

while True:
    # 4) accept: se BLOQUEA hasta que llega un cliente. Devuelve un socket NUEVO
    #    (conexion) para hablar con ese cliente, y su direccion (ip, puerto).
    conexion, direccion = servidor.accept()
    print(f"Cliente conectado desde {direccion}")

    buffer = ""   # aqui se acumula el texto que todavia no forma una linea completa
    while True:
        datos = conexion.recv(1024)   # recibe HASTA 1024 bytes
        if not datos:
            # recv() devuelve b"" (vacio) cuando el cliente cerro la conexion
            print(f"Cliente {direccion} se desconecto")
            break

        # Llegan bytes -> se convierten a texto con decode
        buffer += datos.decode("utf-8")

        # Mientras haya al menos un mensaje completo en el buffer, lo extraemos
        while "\n" in buffer:
            # split("\n", 1) parte SOLO en el primer salto de linea:
            # mensaje = lo de antes, buffer = lo que sobra (puede ser otro mensaje a medias)
            mensaje, buffer = buffer.split("\n", 1)
            print(f"Recibido de {direccion}: {mensaje}")
            # Eco: se reenvia el mismo mensaje, volviendo a poner el '\n' final.
            # sendall exige bytes -> encode
            conexion.sendall((mensaje + "\n").encode("utf-8"))

    conexion.close()   # cerramos el socket de ESTE cliente; el servidor sigue escuchando
