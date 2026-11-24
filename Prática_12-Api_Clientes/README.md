# Práctica 12 — Cliente que consume una API web

Programación en Red · NRC 19141 · Trabajo individual

Cliente de consola en Python que consume la API REST de una **bitácora de incidentes de ciberseguridad**: lista activos, registra incidentes y los resuelve, y maneja los códigos de estado HTTP y los errores de red sin mostrar rastreos de pila.

> **Infraestructura proporcionada:** `servicio/servicio_minimo.py` es el servicio de apoyo (Flask + SQLite) entregado con el material base y se conserva **sin modificaciones**. El trabajo evaluado está en `cliente/`.

## 1. Estructura

```text
Prática_12-Api_Clientes/
├── README.md
├── requirements.txt          # flask (servicio) y requests (cliente)
├── .gitignore                # excluye .venv/, __pycache__/, *.py[cod] y la base SQLite
├── cliente/
│   ├── main.py               # menú y manejo general de excepciones (proporcionado)
│   ├── api.py                # TODO 1-3: toda la comunicación HTTP
│   ├── activos.py            # TODO 4: presentación de activos
│   ├── incidentes.py         # TODO 5: confirmación del registro
│   └── resoluciones.py       # TODO 6: confirmación de la resolución
└── servicio/
    └── servicio_minimo.py    # servicio de apoyo (proporcionado, sin cambios)
```

## 2. Instalación

Requiere Python 3.10 o superior. Desde esta carpeta:

```bash
python -m venv .venv
```

Activa el entorno:

- Windows PowerShell: `.venv\Scripts\Activate.ps1`
- Linux o macOS: `source .venv/bin/activate`

Instala las dependencias:

```bash
pip install -r requirements.txt
```

## 3. Ejecución (dos terminales)

**Terminal 1**, el servicio:

```bash
python servicio/servicio_minimo.py
```

**Terminal 2**, el cliente (con el mismo entorno activado):

```bash
python cliente/main.py
```

Para empezar con datos limpios, detén el servicio y borra `servicio/bitacora.sqlite`. Al volver a arrancar se crea una base nueva con el activo `PC-LAB-01` (ID 1).

## 4. Contrato consumido

| Funcionalidad | Módulo | Operación HTTP | Cuerpo JSON | Éxito |
|---|---|---|---|---|
| Listar activos | `activos.py` | `GET /api/activos` | — | `200` |
| Registrar incidente | `incidentes.py` | `POST /api/incidentes` | `activo_id`, `descripcion`, `severidad` | `201` |
| Resolver incidente | `resoluciones.py` | `PUT /api/incidentes/<id>/resolucion` | `accion_tomada` | `200` |

## 5. Implementación

### `api.py` (TODO 1, 2 y 3)

Las tres funciones siguen el mismo patrón:

1. Construyen la URL a partir de `BASE_URL`. Si el servicio cambia de máquina o de puerto, solo hay que cambiar esa línea.
2. Envían la solicitud con `timeout=TIMEOUT` (5 s), para que una caída del servicio nunca bloquee el cliente.
3. En POST y PUT envían el diccionario con `json=datos`. `requests` lo serializa y agrega `Content-Type: application/json`.
4. Llaman a `raise_for_status()`, que convierte un 4xx o 5xx en `HTTPError`. `main.py` captura esa excepción y muestra el código.
5. Devuelven `respuesta.json()`, es decir, la estructura Python ya deserializada.

```python
def registrar_incidente(activo_id, descripcion, severidad):
    datos = {"activo_id": activo_id, "descripcion": descripcion, "severidad": severidad}
    respuesta = requests.post(f"{BASE_URL}/incidentes", json=datos, timeout=TIMEOUT)
    respuesta.raise_for_status()
    return respuesta.json()
```

### Presentación (TODO 4, 5 y 6)

- **`activos.py`**: si la lista está vacía muestra «No hay activos registrados.». Si no, imprime una tabla de texto con `ID` y `Nombre` y el total.
- **`incidentes.py`** y **`resoluciones.py`**: muestran una confirmación con el `id` y el `estado` que devolvió el servicio.

Ninguna funcionalidad llama a `requests` directamente: toda la comunicación HTTP vive en `api.py`.

## 6. Verificación previa con curl

```bash
curl -i http://localhost:5000/api/salud
curl -i http://localhost:5000/api/activos

curl -i -X POST http://localhost:5000/api/incidentes \
  -H "Content-Type: application/json" \
  -d '{"activo_id":1,"descripcion":"Puerto 23 abierto","severidad":"alta"}'

curl -i -X PUT http://localhost:5000/api/incidentes/1/resolucion \
  -H "Content-Type: application/json" \
  -d '{"accion_tomada":"Se cerró el puerto"}'
```

Resultados observados: `GET /api/salud` → `200 OK` con `{"estado": "ok"}`, y `GET /api/activos` → `200 OK` con `[{"id": 1, "nombre": "PC-LAB-01"}]`. Si se repite el PUT, la respuesta es `409 Conflict`. Si se usa un ID inexistente, la respuesta es `404 Not Found`.

## 7. Pruebas y evidencias

Ejecutadas con el cliente terminado contra el servicio de apoyo, partiendo de una base limpia.

| # | Caso de prueba | Entrada | Resultado obtenido en el cliente | Código (registro del servicio) |
|---|---|---|---|---|
| 1 | Listar activos con servicio activo | Menú → 1 | Tabla con `1  PC-LAB-01` y «Total: 1 activo(s).» | `GET /api/activos` **200** |
| 2 | Registrar incidente válido | Menú → 2, `1`, «Puerto 23 abierto», `alta` | «Incidente registrado correctamente. ID: 1 \| Estado: abierto» | `POST /api/incidentes` **201** |
| 3 | Registrar con activo inexistente | Menú → 2, `activo_id = 999` | «Error del servicio: 404» | `POST /api/incidentes` **404** |
| 4 | Resolver incidente abierto | Menú → 3, `1`, «Se cerró el puerto» | «Incidente resuelto correctamente. ID: 1 \| Estado: resuelto» | `PUT /api/incidentes/1/resolucion` **200** |
| 5 | Resolver incidente ya resuelto | Menú → 3, `1` otra vez | «Error del servicio: 409» | `PUT /api/incidentes/1/resolucion` **409** |
| 6 | Servicio apagado | Opciones 1, 2 y 3 | «Error: no se pudo contactar al servicio. ¿Está en ejecución?» (sin rastreo de pila) | — (excepción de red) |
| extra | Resolver incidente inexistente | Menú → 3, `999` | «Error del servicio: 404» | `PUT /api/incidentes/999/resolucion` **404** |

Registro del servicio durante las pruebas:

```text
"GET /api/activos HTTP/1.1" 200 -
"POST /api/incidentes HTTP/1.1" 201 -
"POST /api/incidentes HTTP/1.1" 404 -
"PUT /api/incidentes/1/resolucion HTTP/1.1" 200 -
"PUT /api/incidentes/1/resolucion HTTP/1.1" 409 -
"PUT /api/incidentes/999/resolucion HTTP/1.1" 404 -
```

> Las capturas de pantalla del cliente y de curl se agregan en la carpeta `evidencias/`.

## 8. Comprobaciones de comprensión

### Tema 2. Clientes, servicios e intermediarios

**¿Por qué el cliente no necesita saber si habla con el servicio final o con un proxy?**
Porque REST exige una interfaz uniforme: el proxy acepta los mismos métodos, URLs, códigos de estado y representaciones JSON que el servicio. El cliente solo habla HTTP con quien esté en la dirección configurada. Si en medio hay un intermediario que reenvía la solicitud, el cliente no lo nota, y la infraestructura puede cambiar sin tocar el programa.

**¿Qué papel juega la caché cuando muchos clientes repiten la misma consulta?**
Guarda la respuesta de la primera consulta (por ejemplo, un `GET /api/activos`) y la entrega a las siguientes sin reenviarlas al servicio. Así baja la carga del servidor y el tráfico de red, y los clientes reciben la respuesta más rápido. Esto solo vale para operaciones seguras como GET. Un POST o un PUT sí deben llegar al servicio.

### Tema 3. Serialización

**¿En qué se diferencia el diccionario de Python del texto JSON?**
El diccionario es una estructura en memoria con tipos de Python (`True`, `None`, comillas simples o dobles). El JSON es solo texto (una `str`) que sigue un formato estándar: comillas dobles obligatorias, `true`/`false` y `null`. Ese texto es lo que viaja por la red como bytes. `json.dumps()` pasa del diccionario al texto y `json.loads()` hace lo contrario.

**¿Qué ocurre si el texto JSON está mal formado al llamar a `json.loads()`?**
Se lanza `json.JSONDecodeError`, que es subclase de `ValueError`. Por eso `main.py` captura `ValueError`: si el servicio devolviera algo que no es JSON válido, `respuesta.json()` fallaría y el cliente mostraría «la respuesta del servicio no tiene el formato esperado» en lugar de cerrarse.

### Tema 4. APIs orientadas a recursos

**¿Qué método se usa para registrar un incidente y cuál para resolverlo?**
`POST /api/incidentes` para registrarlo, porque crea un recurso nuevo y el servidor le asigna el ID. `PUT /api/incidentes/<id>/resolucion` para resolverlo, porque actualiza el estado de un recurso que ya existe y está identificado por su URL.

**¿Qué diferencia hay entre 400 y 404?**
`400 Bad Request` significa que la solicitud está mal formada: JSON inválido o falta un campo obligatorio como `accion_tomada`. El servidor ni siquiera puede procesarla. `404 Not Found` significa que la solicitud es correcta pero el recurso al que se refiere no existe, por ejemplo `activo_id = 999`.

**¿Por qué resolver dos veces el mismo incidente es 409 y no 400?**
Porque la segunda solicitud está bien formada: tiene el JSON correcto y un ID que existe. Lo que impide la operación es el **estado actual** del recurso, que ya está resuelto. `409 Conflict` describe justo eso: una solicitud válida que choca con el estado del servidor. Un 400 haría creer al cliente que se equivocó en el formato.

### Tema 5. Tecnologías e integración

**¿Qué diferencia hay entre `requests` y `urllib`?**
`urllib` viene en la biblioteca estándar y no hay que instalarla, pero es más verbosa. Hay que serializar el JSON a mano, codificar a bytes, poner los encabezados, decodificar la respuesta, y los códigos 4xx/5xx llegan como excepciones distintas. `requests` es una biblioteca externa con una API más simple: `json=` serializa y pone el `Content-Type`, `.json()` deserializa y `raise_for_status()` centraliza la verificación de errores.

**¿Por qué el contrato es el único acuerdo necesario entre un cliente y un servicio heterogéneos?**
Porque lo único que intercambian es HTTP: URLs, métodos, códigos de estado y representaciones JSON. Nada más cruza la red. El servicio puede estar hecho en Flask con SQLite, en Java o en Node, y el cliente en Python, en JavaScript o con curl. Mientras ambos respeten el contrato, ninguno necesita conocer el lenguaje, el framework ni la base de datos del otro. En esta práctica, el cliente funciona contra cualquier servicio que implemente la tabla de la sección 4.

## 9. Seguridad y Git

- `.gitignore` excluye `.venv/`, `__pycache__/`, `*.py[cod]` y `servicio/bitacora.sqlite`.
- No se suben contraseñas, tokens ni llaves privadas.
- Historial con commits separados: estructura base, `api.py`, módulos de funcionalidades, pruebas y README.
