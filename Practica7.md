# Práctica 7 - Parte 1: Capturar y leer tráfico HTTP real

**Programación en Red · NRC 19141 · Unidad IV**
**Alumno:** *Emmanuel Alexis Esperilla Castro*
**Fecha:** 27 de octubre de 2026

---
| Nº | Sitio / URL | Versión HTTP | Método | Línea de estado (versión, código, frase) | User-Agent | Server | Content-Type |
|----|-------------|--------------|--------|------------------------------------------|------------|--------|--------------|
| 1 | https://www.netacad.com/es/ | HTTP/2 | OPTIONS | 204 No Content | Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/156.0.0.0 Safari/537.36 Edg/156.0.0.0 | istio-envoy | application/javascript; charset=UTF-8 |
| 2 | https://dsia.uv.mx/miuv/escritorio/login.aspx | HTTP/2 | GET | 200 OK | Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/156.0.0.0 Safari/537.36 Edg/156.0.0.0 | nginx | text/json;charset=utf-8 |
| 3 | https://github.com/Esperilla | HTTP/2 | OPTIONS | 204 No Content | Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/156.0.0.0 Safari/537.36 Edg/156.0.0.0 | istio-envoy | application/javascript; charset=UTF-8 |

**1. ¿Por qué Host es obligatorio en HTTP/1.1 si la conexión ya sabe la IP?**

Por el _virtual hosting_ basado en nombres. Una sola IP (un solo servidor) puede alojar **muchos sitios** distintos. La conexión TCP solo le dice al servidor “llegó algo a esta IP en el puerto 443”, pero no _cuál_ de los dominios que aloja quiere el cliente. El encabezado Host es el que desambigua: le dice “quiero `www.uv.mx`”, y así el servidor sabe qué sitio servir. La analogía: la IP es la dirección del edificio; Host es el nombre del inquilino en el buzón. En HTTP/1.0 no era obligatorio porque se asumía un sitio por IP; HTTP/1.1 lo volvió obligatorio justo para permitir hosting compartido, CDNs y proxies inversos. (En HTTP/2-3 su equivalente es el pseudo-encabezado `:authority`.)

**2. HTTP es texto plano y legible: ¿qué implica para una contraseña en un formulario?**

Que viaja **legible por la red**. Si envías un formulario de login por HTTP puro, el usuario y la contraseña van en el cuerpo del POST tal cual, sin cifrar. Cualquiera que pueda interceptar el tráfico —alguien en el mismo WiFi, un router malicioso, el ISP, un atacante en medio (MITM)— la lee directo, por ejemplo abriendo la captura en Wireshark. Por eso existe HTTPS: no hace que HTTP deje de ser texto plano, sino que mete todo ese texto dentro de un **túnel cifrado con TLS**, así el que intercepta solo ve ruido. La conclusión práctica: nunca envíes credenciales ni datos sensibles por HTTP sin cifrar; siempre HTTPS. (Esto es justo el puente a tu clase siguiente.)

**3. ¿Qué tienen en común “apodo>mensaje” (Unidad I), XML-RPC y HTTP?**

Asumiendo que “apodo>mensaje” es ese protocolo de chat sencillo donde el mensaje lleva el apodo y un delimitador `>` (corrígeme si era otra cosa), los tres comparten:

- Son **protocolos de capa de aplicación**: definen el _formato y las reglas_ con que un cliente y un servidor intercambian mensajes, no cómo viajan los bits.
- Son **basados en texto / legibles por humanos**: `apodo>mensaje` es texto con un delimitador, XML-RPC es XML (etiquetas de texto), HTTP/1.1 es texto con líneas y encabezados. En todos puedes “leer” el mensaje.
- Son un **acuerdo de estructura**: ambos extremos pactan una gramática (un `>`, unas etiquetas `<methodCall>`, o la línea de solicitud + encabezados) para poder _parsear_ y entenderse.
- Todos corren **encima de TCP**: se apoyan en el transporte confiable y le agregan su propia semántica. De hecho XML-RPC va literalmente **montado sobre HTTP** (usa POST para enviar su XML), así que el parentesco ahí es directo.

---

# Práctica 7 - Parte 2: Provocar códigos 200, 404 y 500

## Ejercicio 1 · Un 200 a mano

```bash
curl -v https://httpbin.org/get
```

**Salida de referencia**:

```bash
*   Trying 54.147.68.244:443...
* Connected to httpbin.org (54.147.68.244) port 443
* ALPN: curl offers h2,http/1.1
* TLSv1.3 (OUT), TLS handshake, Client hello (1):
* TLSv1.2 (IN), TLS handshake, Server hello (2):
* SSL connection using TLSv1.2 / ECDHE-RSA-AES128-GCM-SHA256
* Server certificate:
*  subject: CN=httpbin.org
*  issuer: C=US; O=Amazon; CN=Amazon RSA 2048 M02
* using HTTP/1.1
> GET /get HTTP/1.1          ← LÍNEA DE SOLICITUD (método, ruta, versión) que generamos
> Host: httpbin.org
> User-Agent: curl/8.5.0     ← USER-AGENT con que se presenta curl
> Accept: */*
>
< HTTP/1.1 200 OK            ← LÍNEA DE ESTADO (versión, código, frase)
< Date: Tue, 27 Oct 2026 21:47:20 GMT
< Content-Type: application/json
< Content-Length: 256
< Connection: keep-alive
< Server: gunicorn/19.9.0
< Access-Control-Allow-Origin: *
< Access-Control-Allow-Credentials: true
<
{
  "args": {},
  "headers": {
    "Accept": "*/*",
    "Host": "httpbin.org",
    "User-Agent": "curl/8.5.0"
  },
  "origin": "189.xxx.xxx.xxx",
  "url": "https://httpbin.org/get"
}
* Connection #0 to host httpbin.org left intact
```

**Lo que hay que identificar:**
- **Línea de solicitud (la generamos nosotros):** `GET /get HTTP/1.1` — método `GET`, ruta `/get`, versión `HTTP/1.1`.
- **User-Agent de curl:** `User-Agent: curl/8.5.0`.
- **Línea de estado (la responde el servidor):** `HTTP/1.1 200 OK` — todo salió bien, el recurso existe y se devuelve.

---

## Ejercicio 2 · Un 404 provocado

```bash
curl -v https://httpbin.org/noexiste
```

**Salida de referencia**:

```bash
> GET /noexiste HTTP/1.1
> Host: httpbin.org
> User-Agent: curl/8.5.0
> Accept: */*
>
< HTTP/1.1 404 NOT FOUND     ← LÍNEA DE ESTADO
< Date: Tue, 27 Oct 2026 21:47:20 GMT
< Content-Type: text/html
< Content-Length: 233
< Connection: keep-alive
< Server: gunicorn/19.9.0
<
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">
<title>404 Not Found</title>
<h1>Not Found</h1>
<p>The requested URL was not found on the server. ...</p>
```

**Línea de estado:** `HTTP/1.1 404 NOT FOUND`.

**¿Por qué es 4xx y no 5xx?** Los códigos **4xx** señalan errores **del lado del cliente**: la petición en sí está mal planteada. Aquí el servidor funciona perfectamente; simplemente **la ruta `/noexiste` que pedimos no corresponde a ningún recurso**. El error es nuestro (pedimos algo que no existe), no una avería del servidor. Un **5xx** se reservaría para cuando el servidor sí entiende la petición pero **falla al procesarla** por un problema interno suyo.

---

## Ejercicio 3 · Un 500 bajo pedido

```bash
curl -v https://httpbin.org/status/500
```

**Salida de referencia:**

```bash
> GET /status/500 HTTP/1.1
> Host: httpbin.org
> User-Agent: curl/8.5.0
> Accept: */*
>
< HTTP/1.1 500 INTERNAL SERVER ERROR   ← LÍNEA DE ESTADO
< Date: Tue, 27 Oct 2026 21:47:20 GMT
< Content-Type: text/html; charset=utf-8
< Content-Length: 0
< Connection: keep-alive
< Server: gunicorn/19.9.0
<
* Connection #0 to host httpbin.org left intact
```

**Línea de estado:** `HTTP/1.1 500 INTERNAL SERVER ERROR` (cuerpo vacío: `Content-Length: 0`).

**Diferencia de responsabilidad frente al 404:**
- En el **404**, la **petición era inválida** (pedimos un recurso inexistente): la "culpa" es del **cliente**. El servidor está sano.
- En el **500**, la **petición era válida y bien formada**, pero el **servidor falló internamente** al atenderla (una excepción no controlada, una conexión caída a la base de datos, un bug). La "culpa" es del **servidor**.

En resumen: 4xx = "lo que pediste está mal"; 5xx = "lo que pediste está bien, pero yo (servidor) me rompí".

---

## Ejercicio 4 · Métodos distintos de GET

### 4a · POST con cuerpo

```bash
curl -v -d "nombre=Ada&materia=redes" https://httpbin.org/post
```

**Salida de referencia:**

```bash
> POST /post HTTP/1.1
> Host: httpbin.org
> User-Agent: curl/8.5.0
> Accept: */*
> Content-Length: 24                                ← curl lo agrega solo
> Content-Type: application/x-www-form-urlencoded    ← curl lo agrega solo
>
< HTTP/1.1 200 OK
< Content-Type: application/json
< Content-Length: 325
<
{
  "args": {},
  "data": "",
  "files": {},
  "form": {
    "nombre": "Ada",
    "materia": "redes"
  },
  "json": null,
  "headers": {
    "Content-Type": "application/x-www-form-urlencoded",
    "Host": "httpbin.org",
    "User-Agent": "curl/8.5.0"
  },
  "origin": "189.xxx.xxx.xxx",
  "url": "https://httpbin.org/post"
}
```

**Qué cambió:** el método pasó a `POST` y la petición **lleva cuerpo**. Al usar `-d`, curl **añade automáticamente** `Content-Length` y `Content-Type: application/x-www-form-urlencoded`. El servidor nos devuelve en `"form"` los datos que enviamos: eso confirma que el cuerpo viajó y fue interpretado.

### 4b · HEAD

```bash
curl -I https://httpbin.org/get
```

**Salida de referencia:**

```bash
HTTP/1.1 200 OK
Date: Tue, 27 Oct 2026 21:47:20 GMT
Content-Type: application/json
Content-Length: 429
Connection: keep-alive
Server: gunicorn/19.9.0
Access-Control-Allow-Origin: *
Access-Control-Allow-Credentials: true
```

**Qué cambió:** `HEAD` pide **solo los encabezados, sin cuerpo**. Fíjense que `Content-Length` indica el tamaño que *tendría* la respuesta (429), pero **no se descarga ningún byte del cuerpo**. Es útil para comprobar si un recurso existe, su tamaño o su fecha, sin gastar ancho de banda bajándolo.

---

## Ejercicio 5 · La petición literal con netcat

```bash
printf 'GET /get HTTP/1.1\r\nHost: httpbin.org\r\nConnection: close\r\n\r\n' | nc httpbin.org 80
```

**Salida de referencia:**

```bash
HTTP/1.1 200 OK
Date: Tue, 27 Oct 2026 21:47:26 GMT
Content-Type: application/json
Content-Length: 182
Connection: close
Server: gunicorn/19.9.0
Access-Control-Allow-Origin: *

{
  "args": {},
  "headers": {
    "Accept": "",
    "Host": "httpbin.org"
  },
  "origin": "189.xxx.xxx.xxx",
  "url": "http://httpbin.org/get"
}
```

**¿Qué encabezados agrega curl por su cuenta que nosotros no escribimos a mano?**

Al escribir la petición con `printf` solo puse `Host` y `Connection`. Comparando con la petición de curl, curl **añade solo**:

| Encabezado | ¿Lo escribimos en nc? | ¿Lo pone curl solo? |
|---|---|---|
| `Host` | Sí | Sí (desde la URL) |
| `User-Agent: curl/8.5.0` | **No** | **Sí** |
| `Accept: */*` | **No** | **Sí** |
| `Content-Length` / `Content-Type` (solo con cuerpo, p. ej. `-d`) | No | **Sí** |

Conclusión: con netcat la petición es **mínima** (solo lo que tecleamos); curl, por comodidad, agrega `User-Agent` y `Accept` automáticamente (y `Content-Length`/`Content-Type` cuando hay cuerpo). En el JSON espejo de httpbin se nota: por netcat el `User-Agent` sale vacío porque nunca lo mandamos.

---

## 7 · Preguntas

**• Recurso protegido pedido sin credenciales: ¿401 o 403? ¿Diferencia?**

Se espera **401 Unauthorized**. El 401 significa *"no te he podido autenticar"*: faltan credenciales o son inválidas, y el servidor no sabe quién eres. Suele acompañarse del encabezado `WWW-Authenticate`, que **invita** al cliente a autenticarse y reintentar.

El **403 Forbidden** es distinto: el servidor **sí sabe quién eres** (o la identidad es irrelevante) pero **no tienes permiso** para ese recurso, y **volver a autenticarte no cambiaría nada**. Regla práctica: *401 = "identifícate"; 403 = "ya sé quién eres y aun así no puedes"*.

**• ¿Qué debería hacer el programador para que una falla no llegue como un 500 pelado?**

Aplicar **manejo de errores** en vez de dejar que una excepción no controlada burbujee hasta el handler por defecto (que produce el 500 vacío):
- **Capturar excepciones** (try/catch) y **validar las entradas** antes de procesarlas, devolviendo el código correcto según la causa: `400` si el cliente mandó algo inválido, `404` si no existe, `422` si falla la validación, `503` si una dependencia está caída.
- Usar un **manejador de errores global / middleware** para que ninguna ruta quede sin red de seguridad.
- **Registrar (log) el detalle real del lado del servidor** para diagnosticar, pero **devolver al cliente un mensaje genérico y seguro** (nunca stack traces ni datos internos: eso es una fuga de información).
- Si de verdad es un fallo interno, responder un `500`/`503` **con cuerpo estructurado** (p. ej. JSON con un código de error y un mensaje legible), no vacío.
- **Degradación elegante**: timeouts, reintentos y valores por defecto ante fallos de servicios externos.

En corto: distinguir error del cliente vs. del servidor, fallar de forma controlada, loguear adentro y exponer poco afuera.

