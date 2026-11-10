# =============================================================================
# Practica 8 - Servidor HTTP: CRUD con JSON en disco (bitacora de incidencias)
# -----------------------------------------------------------------------------
# Servidor HTTP con la biblioteca estandar (http.server). Administra una
# bitacora de incidencias de seguridad guardada en incidencias.json:
#   GET    /incidencias[?tipo=..&estado=..]  lista (con filtros combinables)
#   GET    /incidencias/<id>                 lee una
#   POST   /incidencias                      crea            -> 201
#   PATCH  /incidencias/<id>                 modifica campos -> 200
#   PUT    /incidencias/<id>                 reemplaza todo  -> 200 (ejercicio 4)
#   DELETE /incidencias/<id>                 elimina         -> 204
#   GET    /logs, GET /contadores            auditoria de la sesion
#
# Ejercicios resueltos:
#   1. Vocabulario controlado de "estado" en POST, PATCH (y PUT).
#   4. do_PUT: reemplazo completo del registro.
#   5. Filtro "estado" combinable con "tipo" en GET /incidencias.
#   (2 y 3 se explican en el README de esta carpeta.)
# =============================================================================
import http.server, json, time
from urllib.parse import urlparse, parse_qs

HOST = "localhost"
PUERTO = 8001

ARCHIVO = "incidencias.json"  # la "base de datos": un archivo JSON
siguiente_id = 1

# Ejercicio 1: unicos valores aceptados para "estado"
ESTADOS_VALIDOS = ("abierta", "en_proceso", "resuelta")


def cargar():
    """Lee las incidencias del archivo JSON al arrancar el servidor."""
    global siguiente_id
    try:
        with open(ARCHIVO, encoding="utf-8") as f:
            datos = json.load(f)
        if datos:
            siguiente_id = max(i["id"] for i in datos) + 1
        return datos
    except (FileNotFoundError, json.JSONDecodeError):
        return []  # primera ejecucion o archivo corrupto: empezar vacio


def guardar():
    """Reescribe el archivo JSON con la lista actual de incidencias."""
    with open(ARCHIVO, "w", encoding="utf-8") as f:
        json.dump(incidencias, f, ensure_ascii=False, indent=2)


incidencias = cargar()  # al arrancar, recupera lo que habia en disco

# Bitacora de peticiones y contadores: viven en memoria (solo la sesion)
logs = []

contadores = {
    "peticiones_totales": 0,
    "por_metodo": {"GET": 0, "POST": 0, "PATCH": 0, "PUT": 0, "DELETE": 0, "HEAD": 0},
    "por_familia": {"2xx": 0, "4xx": 0, "5xx": 0},
    "incidencias_por_tipo": {"alerta": 0, "vulnerabilidad": 0, "incidente": 0},
}


def estado_invalido(datos):
    """Ejercicio 1: devuelve un mensaje de error si 'estado' no es valido, o None."""
    if "estado" in datos and datos["estado"] not in ESTADOS_VALIDOS:
        return (f"estado invalido: {datos['estado']!r}; "
                f"valores validos: {', '.join(ESTADOS_VALIDOS)}")
    return None


class Manejador(http.server.BaseHTTPRequestHandler):

    def _leer_json(self):
        """Lee el cuerpo de la peticion y lo interpreta como JSON."""
        try:
            tam = int(self.headers.get("Content-Length", 0))
            return json.loads(self.rfile.read(tam).decode("utf-8"))
        except (ValueError, json.JSONDecodeError):
            return None  # cuerpo ausente o JSON invalido

    def _enviar(self, codigo, datos=None):
        """Envia la respuesta JSON y anota la peticion en logs y contadores."""
        cuerpo = b"" if datos is None else json.dumps(datos, ensure_ascii=False).encode("utf-8")
        self.send_response(codigo)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(cuerpo)))
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(cuerpo)
        logs.append({"hora": time.strftime("%H:%M:%S"),
                     "metodo": self.command, "ruta": self.path, "codigo": codigo})
        contadores["peticiones_totales"] += 1
        contadores["por_metodo"][self.command] = contadores["por_metodo"].get(self.command, 0) + 1
        contadores["por_familia"][f"{codigo // 100}xx"] += 1

    def _id_de_ruta(self, url):
        """Extrae el id de /incidencias/<id>; si no es entero responde 400 y devuelve None."""
        try:
            return int(url.path.split("/")[2])
        except ValueError:
            self._enviar(400, {"error": "id debe ser entero"})
            return None

    def do_HEAD(self):
        url = urlparse(self.path)
        if url.path in ("/", "/incidencias", "/logs", "/contadores"):
            self._enviar(200)
        else:
            self._enviar(404)

    def do_GET(self):
        url = urlparse(self.path)
        parametros = parse_qs(url.query)

        if url.path == "/":
            self._enviar(200, {
                "servicio": "Bitácora de incidencias",
                "rutas": ["GET /incidencias", "GET /incidencias/<id>",
                          "POST /incidencias", "PATCH /incidencias/<id>",
                          "PUT /incidencias/<id>", "DELETE /incidencias/<id>",
                          "GET /logs", "GET /contadores"],
            })

        elif url.path == "/incidencias":
            lista = incidencias
            # Ejercicio 5: cada filtro presente reduce la lista; se pueden combinar
            for campo in ("tipo", "estado"):
                if campo in parametros:
                    lista = [i for i in lista if i[campo] == parametros[campo][0]]
            self._enviar(200, lista)

        elif url.path.startswith("/incidencias/"):
            buscado = self._id_de_ruta(url)
            if buscado is None:
                return
            for inc in incidencias:
                if inc["id"] == buscado:
                    self._enviar(200, inc)
                    return
            self._enviar(404, {"error": f"incidencia {buscado} no encontrada"})

        elif url.path == "/logs":
            self._enviar(200, logs)

        elif url.path == "/contadores":
            self._enviar(200, contadores)

        else:
            self._enviar(404, {"error": f"ruta no conocida: {url.path}"})

    def do_POST(self):
        url = urlparse(self.path)
        if url.path != "/incidencias":
            self._enviar(404, {"error": f"ruta no conocida: {url.path}"})
            return

        datos = self._leer_json()
        if not isinstance(datos, dict):
            self._enviar(400, {"error": "el cuerpo debe ser JSON válido"})
            return
        faltan = [c for c in ("tipo", "descripcion") if c not in datos]
        if faltan:
            self._enviar(400, {"error": f"faltan campos: {', '.join(faltan)}"})
            return
        error = estado_invalido(datos)
        if error:
            self._enviar(400, {"error": error})
            return

        global siguiente_id
        incidencia = {
            "id": siguiente_id,
            "tipo": str(datos["tipo"]),
            "descripcion": str(datos["descripcion"]),
            "estado": datos.get("estado", "abierta"),
            "hora": time.strftime("%Y-%m-%d %H:%M:%S"),
        }
        siguiente_id += 1
        incidencias.append(incidencia)
        contadores["incidencias_por_tipo"][incidencia["tipo"]] = (
            contadores["incidencias_por_tipo"].get(incidencia["tipo"], 0) + 1)
        guardar()  # <-- aqui se escribe incidencias.json
        self._enviar(201, incidencia)

    def do_PATCH(self):
        url = urlparse(self.path)
        if not url.path.startswith("/incidencias/"):
            self._enviar(404, {"error": f"ruta no conocida: {url.path}"})
            return
        buscado = self._id_de_ruta(url)
        if buscado is None:
            return

        datos = self._leer_json()
        if not isinstance(datos, dict):
            self._enviar(400, {"error": "el cuerpo debe ser JSON válido"})
            return
        error = estado_invalido(datos)
        if error:
            self._enviar(400, {"error": error})
            return

        for inc in incidencias:
            if inc["id"] == buscado:
                for campo in ("tipo", "descripcion", "estado"):
                    if campo in datos:
                        inc[campo] = str(datos[campo])
                guardar()  # <-- el cambio queda en el archivo
                self._enviar(200, inc)
                return
        self._enviar(404, {"error": f"incidencia {buscado} no encontrada"})

    def do_PUT(self):
        """Ejercicio 4: reemplazo completo. Conserva id, reinicia estado a 'abierta'."""
        url = urlparse(self.path)
        if not url.path.startswith("/incidencias/"):
            self._enviar(404, {"error": f"ruta no conocida: {url.path}"})
            return
        buscado = self._id_de_ruta(url)
        if buscado is None:
            return

        datos = self._leer_json()
        if not isinstance(datos, dict):
            self._enviar(400, {"error": "el cuerpo debe ser JSON válido"})
            return
        faltan = [c for c in ("tipo", "descripcion") if c not in datos]
        if faltan:
            self._enviar(400, {"error": f"faltan campos: {', '.join(faltan)}"})
            return

        for i, inc in enumerate(incidencias):
            if inc["id"] == buscado:
                incidencias[i] = {
                    "id": buscado,  # el id original nunca cambia
                    "tipo": str(datos["tipo"]),
                    "descripcion": str(datos["descripcion"]),
                    "estado": "abierta",
                    "hora": time.strftime("%Y-%m-%d %H:%M:%S"),
                }
                guardar()  # <-- el reemplazo queda en el archivo
                self._enviar(200, incidencias[i])
                return
        self._enviar(404, {"error": f"incidencia {buscado} no encontrada"})

    def do_DELETE(self):
        url = urlparse(self.path)
        if not url.path.startswith("/incidencias/"):
            self._enviar(404, {"error": f"ruta no conocida: {url.path}"})
            return
        buscado = self._id_de_ruta(url)
        if buscado is None:
            return

        for i, inc in enumerate(incidencias):
            if inc["id"] == buscado:
                del incidencias[i]
                guardar()  # <-- el archivo tambien lo olvida
                self._enviar(204)  # sin cuerpo
                return
        self._enviar(404, {"error": f"incidencia {buscado} no encontrada"})

    def log_message(self, formato, *args):
        # Una linea por peticion en la terminal del servidor. Tambien aparecen
        # aqui las respuestas que genera la clase base sin pasar por _enviar
        # (por ejemplo un 501 de un metodo no implementado).
        print(f"{time.strftime('%H:%M:%S')} | {self.address_string()} | {formato % args}")


if __name__ == "__main__":
    servidor = http.server.HTTPServer((HOST, PUERTO), Manejador)
    print(f"Escuchando en http://{HOST}:{PUERTO}  (Ctrl+C para detener)")
    print(f"Incidencias cargadas de {ARCHIVO}: {len(incidencias)} (siguiente id: {siguiente_id})")
    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        print("\nServidor detenido.")
    finally:
        servidor.server_close()
