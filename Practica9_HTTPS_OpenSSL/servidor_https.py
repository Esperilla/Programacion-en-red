# =============================================================================
# Practica 9 - Ejercicio 3: servidor HTTPS minimo
# -----------------------------------------------------------------------------
# Sirve los archivos de esta carpeta (SimpleHTTPRequestHandler) pero dentro de
# un canal TLS. Necesita certificado.pem y llave.pem en la misma carpeta:
#
#   openssl req -x509 -newkey rsa:2048 -nodes \
#     -keyout llave.pem -out certificado.pem -days 365 \
#     -subj "/CN=localhost" \
#     -addext "subjectAltName=DNS:localhost,IP:127.0.0.1"
#
# Ejecutar: python servidor_https.py  ->  https://localhost:8443
# =============================================================================
import http.server, ssl

servidor = http.server.HTTPServer(("localhost", 8443),
                                  http.server.SimpleHTTPRequestHandler)
contexto = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
contexto.load_cert_chain("certificado.pem", "llave.pem")
servidor.socket = contexto.wrap_socket(servidor.socket, server_side=True)
print("Servidor HTTPS en https://localhost:8443")
servidor.serve_forever()
