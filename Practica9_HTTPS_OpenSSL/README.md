# Práctica 9 — HTTPS y OpenSSL: el candado del navegador

Programación en Red · NRC 19141 · Unidad IV

Se genera un certificado autofirmado con OpenSSL, se levanta un servidor
HTTPS mínimo con `http.server` + `ssl` y, como reto, se sirve la bitácora
CRUD de la Práctica 8 sobre TLS sin tocar su lógica.

| Archivo | Contenido |
|---|---|
| `certificado.pem` | Certificado autofirmado (público, sí se sube) |
| `llave.pem` | Llave privada RSA 2048 — **no se sube** (está en `.gitignore`) |
| `servidor_https.py` | Ejercicio 3: servidor HTTPS de archivos en `https://localhost:8443` |
| `index.html` | Página que muestra `servidor_https.py` |
| `servidor_bitacora.py` | Ejercicio 6: bitácora de la Práctica 8 sobre HTTPS (puerto 8443) |
| `cliente_bitacora.py` | Ejercicio 6: cliente `requests` con `verify="certificado.pem"` |
| `evidencias/` | Salidas reales de los comandos (ejercicios 2 y 6) |

## Generar la llave y el certificado

La llave privada no está en el repositorio. Para ejecutar la práctica hay que
generarla en esta carpeta (Git Bash, Linux o macOS):

```bash
openssl req -x509 -newkey rsa:2048 -nodes -keyout llave.pem -out certificado.pem -days 365 -subj "/CN=localhost" -addext "subjectAltName=DNS:localhost,IP:127.0.0.1"
```

> En **Git Bash** para Windows, `-subj "/CN=localhost"` puede convertirse en
> una ruta de Windows. Si falla, antepón `MSYS_NO_PATHCONV=1` al comando o
> escribe `-subj "//CN=localhost"`.

Si se genera una llave nueva, el certificado también cambia: hay que
regenerar los dos juntos.

---

## Ejercicio 1 — Generar el certificado

Con el comando de arriba se obtuvieron `llave.pem` (llave privada) y
`certificado.pem` (certificado X.509 v3 autofirmado, válido un año).

## Ejercicio 2 — Leer el certificado

```bash
openssl x509 -in certificado.pem -text -noout
```

Salida completa en [`evidencias/ej2_certificado.txt`](evidencias/ej2_certificado.txt).
Campos pedidos:

| Campo | Valor |
|---|---|
| Emisor (Issuer) | `CN=localhost` |
| Sujeto (Subject) | `CN=localhost` |
| Vigencia — Not Before | `Nov  6 22:05:14 2026 GMT` |
| Vigencia — Not After | `Nov  6 22:05:14 2027 GMT` |
| Subject Alternative Name | `DNS:localhost, IP Address:127.0.0.1` |
| Algoritmo de firma | `sha256WithRSAEncryption` |
| Llave pública | RSA 2048 bits |
| Restricciones básicas | `CA:TRUE` (critical) |

**Observación:** emisor y sujeto son **el mismo** (`CN=localhost`), y el
*Authority Key Identifier* es igual al *Subject Key Identifier*. Eso es lo que
significa "autofirmado": el certificado se avala a sí mismo; ninguna CA lo
firmó.

## Ejercicio 3 — Servidor HTTPS

```bash
python servidor_https.py
```

```
Servidor HTTPS en https://localhost:8443
```

`ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)` crea el contexto TLS del lado
servidor, `load_cert_chain` carga certificado y llave, y `wrap_socket`
envuelve el socket TCP ya creado por `HTTPServer`: todo lo que antes salía en
claro ahora pasa por TLS. Con `openssl s_client` se ve que la conexión
negocia **TLS 1.3** con el cifrado **TLS_AES_256_GCM_SHA384**
([`evidencias/ej6_openssl_s_client.txt`](evidencias/ej6_openssl_s_client.txt)).

> ⚠️ **Hallazgo de seguridad:** `SimpleHTTPRequestHandler` sirve *todos* los
> archivos de la carpeta. Con este servidor corriendo,
> `https://localhost:8443/llave.pem` responde **200** y entrega la llave
> privada a quien la pida. Se probó con `curl`. En un servidor real los
> archivos públicos van en una carpeta aparte de la llave (por ejemplo
> `SimpleHTTPRequestHandler` con `directory=` apuntando a `public/`). Por eso
> se agregó `index.html`: así la raíz muestra una página y no el listado de
> archivos, aunque la llave sigue accesible si alguien escribe su ruta.

## Ejercicio 4 — La advertencia del navegador

Con `servidor_https.py` corriendo, abrir `https://localhost:8443`.

Lo que ocurre:

- **(a) Advertencia:** el navegador bloquea la página con *"La conexión no es
  privada"* / *"Your connection is not private"* y el código
  **`NET::ERR_CERT_AUTHORITY_INVALID`**. Al abrirlo desde el navegador
  integrado de la práctica se obtuvo ese mismo error.
- **(b) Detalles del certificado** (clic en "No seguro" → "El certificado no
  es válido"): *Emitido para* `localhost`, *Emitido por* `localhost`, vigencia
  6 nov 2026 – 6 nov 2027 y la huella SHA-256
  `0C:F5:A7:44:52:89:DB:0B:62:93:C6:38:7E:93:9B:B9:D1:D6:AC:79:FB:CE:69:B6:1F:58:CE:65:1A:2C:EC:46`.
- **(c) Después de aceptar el riesgo** ("Configuración avanzada" →
  "Continuar a localhost (no seguro)"), la página carga, pero **no aparece el
  candado normal**: la barra muestra **"No seguro"** con el `https` tachado o
  en rojo. El matiz es que la conexión **sí está cifrada** con TLS, pero el
  navegador avisa que **no pudo verificar la identidad** del servidor.

Capturas (agregarlas en `evidencias/`):

- `evidencias/ej4a_advertencia.png`
- `evidencias/ej4b_detalles_certificado.png`
- `evidencias/ej4c_pagina_cargada.png`

## Ejercicio 5 — Reflexión

El cifrado y la autenticación son promesas distintas de TLS. Con el
certificado autofirmado, el navegador y el servidor sí negocian llaves y
cifran el tráfico (confidencialidad e integridad): nadie en la red puede leer
ni alterar las peticiones. Lo que falta es la tercera promesa, la
**autenticación**. El certificado dice "soy localhost", pero lo firmó el mismo
servidor que lo presenta, y cualquiera puede generar en un segundo un
certificado que diga "soy mibanco.com". Si el navegador aceptara
certificados autofirmados sin avisar, un atacante en medio (*man-in-the-middle*)
podría presentar el suyo y el cifrado solo serviría para hablar en privado con
el impostor. Por eso la advertencia aparece aunque el canal vaya cifrado.

Para que no aparezca, el certificado tiene que encadenar con una raíz en la
que el navegador o el sistema operativo ya confía:

1. **En producción:** pedir el certificado a una CA reconocida (por ejemplo
   Let's Encrypt, gratis y automático con ACME), para un dominio real que se
   pueda demostrar que es nuestro, con el nombre correcto en el SAN y vigente.
2. **En desarrollo:** crear una CA local propia e instalarla como raíz de
   confianza en el equipo (es lo que hace `mkcert`), o importar
   `certificado.pem` al almacén de "Entidades de certificación raíz de
   confianza". Esto solo vale para *tu* máquina y no debe hacerse con
   certificados de terceros.

Además, el nombre que se escribe en la barra debe coincidir con el SAN
(`localhost` o `127.0.0.1`) y la fecha del equipo debe caer dentro de la
vigencia.

## Ejercicio 6 — La bitácora segura (punto extra)

Se copiaron `servidor_bitacora.py` y `cliente_bitacora.py` de la Práctica 8.
Los cambios en el servidor son tres: `import ssl`, el puerto `8443` y el
arranque con `SSLContext` + `wrap_socket`. El cliente solo cambia `BASE` a
`https://localhost:8443` y agrega `verify="certificado.pem"` en cada
petición.

```bash
python servidor_bitacora.py
```

```bash
pip install requests
python cliente_bitacora.py
```

### Pruebas con curl ([`evidencias/ej6_curl.txt`](evidencias/ej6_curl.txt))

| Comando | Resultado |
|---|---|
| `curl --cacert certificado.pem https://localhost:8443/incidencias` | ✅ `200` con la lista JSON; curl validó que el certificado coincide con `localhost` |
| `curl https://localhost:8443/incidencias` (sin opciones) | ❌ error `60` `SEC_E_UNTRUSTED_ROOT`: la cadena fue emitida por una entidad no confiable |
| `curl -k https://localhost:8443/incidencias` | ✅ `200`, pero **sin verificar** quién responde |
| `curl http://localhost:8443/incidencias` | ❌ error `56` *Connection was reset*: el servidor espera un *ClientHello* de TLS y recibe texto HTTP plano, así que corta la conexión |

Un `POST` con `--cacert` también funcionó (`201`) y el registro se guardó en
`incidencias.json`: el CRUD completo opera igual que en la Práctica 8.

### Cliente Python ([`evidencias/ej6_cliente_python.txt`](evidencias/ej6_cliente_python.txt))

El ciclo completo POST → GET → PATCH → PUT → DELETE → 4xx → auditoría corre
sobre HTTPS. Al final el cliente compara las tres formas de verificar:

```
verify='certificado.pem'  -> 200 (correcto: se valida la identidad)
verify=True (CA del sistema) -> SSLError: nadie reconocido firmo el certificado
verify=False -> 200, avisos: ['InsecureRequestWarning']  (mala practica)
```

### Preguntas

**¿Qué diferencia hay entre `-k` y `--cacert`?**
`--cacert certificado.pem` le dice a curl "confía en este certificado como
raíz". curl **sí verifica**: que la firma encadene con ese certificado, que no
esté vencido y que el nombre `localhost` esté en el SAN. Si alguien en medio
presenta otro certificado, la conexión falla. `-k` (`--insecure`) **apaga la
verificación**: sigue cifrando, pero acepta cualquier certificado, incluido el
de un impostor. Es decir, `--cacert` conserva la autenticación y `-k` la
sacrifica. Lo mismo pasa en Python con `verify="certificado.pem"` y
`verify=False`.

**¿Por qué el CRUD no necesitó ningún cambio?**
Porque TLS es una capa que va **debajo de HTTP** y encima de TCP.
`wrap_socket` cambia el socket por uno que cifra al escribir y descifra al
leer, pero hacia arriba se ve igual (`recv`/`send`, `rfile`/`wfile`). El
`Manejador` sigue recibiendo el mismo texto HTTP ya descifrado (`do_GET`,
`do_POST`…), y los contadores, los logs y `incidencias.json` no saben que hubo
cifrado de por medio. Es la ventaja del modelo por capas: cada una ofrece un
servicio a la de arriba sin que esta conozca los detalles.

---

## 6. Contesta

**Un sitio con certificado válido y candado, ¿garantiza que el sitio es
confiable? ¿Qué garantiza exactamente?**
No. El candado garantiza que (1) la conexión va cifrada y no se altera en el
camino, y (2) el servidor controla el dominio que aparece en la barra, porque
una CA lo verificó. **No** garantiza que el dueño sea honesto ni que el
contenido sea seguro: un sitio de *phishing* como `mibanco-seguro-login.com`
puede obtener un certificado válido de Let's Encrypt en minutos. El candado
dice "hablas en privado con *este* dominio", no "este dominio es bueno". Hay
que revisar el dominio con cuidado.

**¿Dónde han visto certificados rotos o expirados en la vida real? ¿Qué
hicieron?**
Casos comunes: portales institucionales o de gobierno con el certificado
vencido, la página de configuración del módem/router (`192.168.1.1`, que usa
un autofirmado), redes Wi-Fi públicas con portal cautivo que interceptan HTTPS,
y equipos con la fecha mal configurada, donde *todos* los sitios marcan error.
Lo correcto es no introducir contraseñas ni datos personales, revisar los
detalles del certificado (emisor, fechas, nombre), corregir la hora del equipo
si ese es el problema y, si es un sitio institucional, avisar al
administrador. Solo se acepta el riesgo cuando sabemos exactamente qué
dispositivo es, como el router propio.

**Proyecto integrador: si el sistema maneja credenciales o datos sensibles,
¿qué implica servirlo por HTTP plano?**
Que contraseñas, *tokens* de sesión, cookies y datos personales viajan
legibles: cualquiera en la misma red (Wi-Fi compartida, el ISP, un equipo
comprometido) puede capturarlos con Wireshark, robar sesiones o modificar las
respuestas, por ejemplo inyectando código. Además los navegadores marcan el
sitio como "No seguro", varias APIs del navegador (geolocalización, *service
workers*, cookies `Secure`) solo funcionan en HTTPS, y con datos personales se
incumplirían obligaciones de protección de datos (en México, la LFPDPPP).
Conclusión: HTTPS es obligatorio, con un certificado de una CA reconocida (Let's
Encrypt), redirección de HTTP a HTTPS, HSTS y la llave privada fuera del
repositorio.

## Referencias

- Kurose, J. & Ross, K. *Redes de computadoras: un enfoque descendente*, cap. 8.
- Documentación de OpenSSL: <https://docs.openssl.org> (`req`, `x509`, `s_client`).
- RFC 8446, *The Transport Layer Security (TLS) Protocol Version 1.3*.
