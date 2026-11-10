# Práctica 8 — Servidor HTTP: CRUD con JSON en disco

Bitácora de incidencias de seguridad servida por HTTP con la biblioteca
estándar de Python (`http.server`). Permite crear, consultar, modificar,
reemplazar y borrar incidencias; los registros se guardan en
`incidencias.json` (sin base de datos) y el servidor audita sus propias
peticiones en `/logs` y `/contadores`.

| Archivo | Contenido |
|---|---|
| `servidor_bitacora.py` | Servidor HTTP en `http://localhost:8001` (pasos 1–8 de la guía + ejercicios 1, 4 y 5) |
| `cliente_bitacora.py` | Cliente con `requests` que recorre el ciclo CRUD completo, los errores 4xx y la auditoría |
| `incidencias.json` | Se crea automáticamente junto al servidor con el primer `POST` |

## Ejecución

```powershell
# Terminal 1 (desde esta carpeta)
python servidor_bitacora.py

# Terminal 2
pip install requests
python cliente_bitacora.py
```

`incidencias.json` se crea en la carpeta desde la que se ejecuta el servidor.

## Rutas

| Método | Ruta | Datos | Respuesta |
|---|---|---|---|
| GET | `/` | — | 200, descripción del servicio |
| GET | `/incidencias` | query `?tipo=` y/o `?estado=` | 200, lista (filtrada) |
| GET | `/incidencias/<id>` | id en la ruta | 200 / 400 / 404 |
| POST | `/incidencias` | cuerpo JSON: `tipo`, `descripcion` (y `estado` opcional) | 201 / 400 |
| PATCH | `/incidencias/<id>` | id + cuerpo JSON con los campos a cambiar | 200 / 400 / 404 |
| PUT | `/incidencias/<id>` | id + cuerpo JSON con `tipo` y `descripcion` | 200 / 400 / 404 |
| DELETE | `/incidencias/<id>` | id en la ruta | 204 (sin cuerpo) / 404 |
| GET | `/logs` | — | 200, bitácora de peticiones de la sesión |
| GET | `/contadores` | — | 200, contadores de la sesión |
| HEAD | `/`, `/incidencias`, `/logs`, `/contadores` | — | 200 sin cuerpo / 404 |

## Ejercicios

### 1. Vocabulario controlado

Se añadió la constante `ESTADOS_VALIDOS = ("abierta", "en_proceso", "resuelta")`
y la función `estado_invalido(datos)`, que `do_POST` y `do_PATCH` llaman antes
de tocar los datos. Si el cuerpo trae un `estado` fuera de esa lista, se
responde **400** con un mensaje que enumera los valores válidos. En `POST` el
campo es opcional (por omisión, `abierta`).

```text
curl -i -X PATCH http://localhost:8001/incidencias/1 -H "Content-Type: application/json" -d "{\"estado\": \"cerrada\"}"
HTTP/1.0 400 Bad Request
{"error": "estado invalido: 'cerrada'; valores validos: abierta, en_proceso, resuelta"}
```

### 2. La libreta en disco

Prueba realizada: se crearon incidencias con `POST`, se comprobó que estaban
escritas en `incidencias.json`, se detuvo el servidor y se volvió a arrancar.
Al iniciar, el servidor muestra lo que recuperó del archivo:

```text
Incidencias cargadas de incidencias.json: 1 (siguiente id: 2)
```

`GET /incidencias` devuelve los registros anteriores y el siguiente `POST`
recibe el id 2: el folio continúa donde se quedó porque `cargar()` calcula
`max(i["id"] for i in datos) + 1` a partir del archivo.

**¿Por qué `/logs` y `/contadores` sí vuelven a cero?** Porque solo las
incidencias se guardan en disco. `logs` y `contadores` son variables globales
del proceso: viven en la memoria RAM (volátil) y nunca se escriben en ningún
archivo. Al detener el servidor el proceso termina y esa memoria se libera;
al arrancarlo de nuevo, el módulo se vuelve a ejecutar desde el principio y
las estructuras se crean otra vez con sus valores iniciales (`[]` y ceros). En
cambio, `incidencias = cargar()` reconstruye la lista leyendo el archivo, y
`guardar()` lo reescribe después de cada `POST`, `PATCH`, `PUT` y `DELETE`.
Son, a propósito, una auditoría *de la sesión*.

### 3. El 501 invisible

Con el servidor original (sin `do_PUT`):

```text
curl -i -X PUT http://localhost:8001/incidencias/1
HTTP/1.0 501 Unsupported method ('PUT')
Content-Type: text/html;charset=utf-8
```

La terminal del servidor sí lo muestra:

```text
code 501, message Unsupported method ('PUT')
"PUT /incidencias/1 HTTP/1.1" 501 -
```

pero `/contadores` queda en `peticiones_totales: 0` y `5xx: 0`, y `/logs` no
tiene ninguna entrada `PUT`.

**¿Por qué?** Porque esa respuesta no la genera nuestro código, sino la
**clase base**. `BaseHTTPRequestHandler.handle_one_request()` busca un método
llamado `do_<MÉTODO>` (aquí, `do_PUT`); como no existe, llama directamente a
`self.send_error(501, ...)` y termina. Esa ruta nunca pasa por nuestro
`_enviar`, que es el único lugar donde se agrega la entrada a `logs` y se
actualizan los `contadores`. Por eso la respuesta es además HTML y no JSON. Lo
que sí aparece en la terminal es el registro propio de la clase base
(`log_error` → `log_message`). Por eso la guía de inicio, con `log_message`
silenciado (`pass`), no mostraba nada; aquí `log_message` imprime una línea
por petición para poder verlo.

### 4. `do_PUT`

`do_PUT` hace un reemplazo completo: toma el id de la ruta (400 si no es
entero), exige `tipo` y `descripcion` en el cuerpo (400 si falta alguno),
conserva el id original, reinicia `estado` a `abierta`, actualiza la `hora`,
llama a `guardar()` y responde **200** con el registro nuevo (404 si el id no
existe). Como ahora sí responde mediante `_enviar`, el `PUT` ya aparece en
`/logs`, en `/contadores` (se añadió `"PUT"` a `por_metodo`) y en el archivo.

```text
curl -i -X PUT http://localhost:8001/incidencias/1 -H "Content-Type: application/json" -d "{\"tipo\": \"incidente\", \"descripcion\": \"Ransomware\"}"
HTTP/1.0 200 OK
{"id": 1, "tipo": "incidente", "descripcion": "Ransomware", "estado": "abierta", "hora": "..."}

curl -i -X PUT http://localhost:8001/incidencias/1 -H "Content-Type: application/json" -d "{\"tipo\": \"incidente\"}"
HTTP/1.0 400 Bad Request
{"error": "faltan campos: descripcion"}
```

`/contadores` después de las pruebas: `"PUT": 3` en `por_metodo`.

### 5. Filtros combinados

En `do_GET`, la rama `/incidencias` aplica cada filtro presente (`tipo`,
`estado`) uno tras otro sobre la lista, de modo que se combinan como un "Y":

```powershell
curl http://localhost:8001/incidencias
curl "http://localhost:8001/incidencias?tipo=alerta"
curl "http://localhost:8001/incidencias?estado=abierta"
curl "http://localhost:8001/incidencias?tipo=alerta&estado=abierta"
curl "http://localhost:8001/incidencias?tipo=alerta&estado=resuelta"
```

El cliente en Python prueba las mismas combinaciones con
`requests.get(..., params={"tipo": "alerta", "estado": "abierta"})`.

## Notas

- En `cmd` o PowerShell de Windows, si un `-d "..."` de curl lleva acentos, la
  consola puede enviarlos en una codificación distinta de UTF-8 y el servidor
  responde 400 (`el cuerpo debe ser JSON válido`). Para mandar acentos, guarda
  el JSON en un archivo UTF-8 y usa `curl --data-binary @cuerpo.json ...`; el
  cliente en Python no tiene ese problema.
- En Windows, `localhost` puede tardar ~1 s por petición porque primero se
  intenta IPv6 (`::1`) y el servidor escucha en IPv4. Si molesta, usa
  `http://127.0.0.1:8001`.
