# Programación en Red

Repositorio de actividades, ejercicios y proyectos del curso **Programación en
Red** de la Universidad Veracruzana (Unidad II). El material practica
comunicación cliente-servidor con sockets **TCP y UDP**, bloqueo, framing,
concurrencia con hilos, manejo de errores y protocolos sencillos de aplicación.

## Requisitos

- Python 3.x
- No se requieren dependencias externas: los programas usan principalmente
  módulos de la biblioteca estándar (`socket`, `threading` y `time`).
- Para ejecutar una comunicación cliente-servidor, inicia primero el servidor
  y después el cliente en otra terminal. Si se usan equipos distintos, cambia
  la dirección IP configurada o solicitada por el programa.

## Estructura del repositorio

### Ejemplos introductorios

En la raíz se encuentran los primeros ejercicios y demostraciones:

| Archivos | Tema |
|---|---|
| `ejercicio1.py`, `ejercicio2.py`, `ejercicio3.py` | Ejercicios básicos de sockets |
| `codigo1_EcoTCP_servidor.py`, `codigo2_EcoTCP_cliente.py` | Servidor y cliente de eco TCP |
| `codigo3_Demostracion_Bloqueo_servidor.py`, `codigo3_Demostracion_Bloqueo_cliente.py` | Comportamiento bloqueante de `accept()` y `recv()` |
| `codigo4_EcoUDP_servidor.py`, `codigo4_EcoUDP_cliente.py` | Eco mediante datagramas UDP |
| `codigo5_Framing_servidor.py`, `codigo5_Framing_cliente.py` | Framing de mensajes TCP mediante el delimitador `\n` |
| `codigo_limpio.py` | Código de referencia/plantilla |

### `01-Actividad Práctica batalla naval TCP-UDP/`

Implementación de una batalla naval mínima con dos variantes de transporte:

- `battleship_defend.py` y `battleship_attack.py`: defensor y atacante TCP.
- `battleship_defend_udp.py` y `battleship_attack_udp.py`: defensor y atacante
  UDP.

El atacante envía coordenadas y el defensor responde `TOCADO` o `AGUA`.
Los scripts incluyen una dirección IP de ejemplo y usan el puerto `5050`;
revísalos y ajústalos antes de ejecutarlos en otra red.

### `Actividad 6/`

Sistema de turnos **LA FILA** con dos protocolos y ejecución concurrente:

- `servidor_turnos.py`: servidor TCP en el puerto `5000` y servidor UDP en el
  puerto `5001`; usa un hilo por cliente TCP, un hilo para consultas UDP y
  `threading.Lock()` para proteger el contador compartido.
- `cliente_turno_tcp.py`: solicita un turno enviando
  `TURNO>apodo\n`.
- `cliente_consulta_udp.py`: consulta el total enviando `CUANTOS` y recibe
  `van>N\n`.
- `Guia_Concurrencia_Hilos_TCP_y_UDP.pdf`: guía de la actividad.

Ejemplo de ejecución desde la carpeta `Actividad 6`:

```powershell
# Terminal 1
python servidor_turnos.py

# Terminal 2
python cliente_turno_tcp.py

# Terminal 3
python cliente_consulta_udp.py
```

Los clientes solicitan la IP del servidor y usan `127.0.0.1` por defecto.

### `Manejo de errores y excepciones en programación de sockets/`

Serie de ejercicios centrados en robustez:

1. `ejercicio1_hilos_nombres.py`: atención de clientes mediante hilos.
2. `ejercicio2_servidor_eco_contador.py`: servidor eco con contador.
3. `ejercicio3_cliente_robusto.py`: cliente con manejo de errores.
4. `ejercicio4_udp_reintentos.py`: reintentos para comunicación UDP.
5. `ejercicio5_fila_tolerante.py`: sistema de turnos tolerante a fallos.
6. `ejercicio6_fila_con_log.py`: servidor de turnos con registro de errores en
   `errores_servidor.log`.

La guía de esta sección se encuentra en
`Guia_Manejo_Errores_Excepciones_y_Ejercicios.pdf`.

### `Examen_y_Ejercicios_Repaso/`

Material de repaso y soluciones/prácticas del examen:

- `Examen_Sockets.html`: enunciado o material del examen.
- `Ejercicios_Repaso/`: seis ejercicios sobre eco TCP, UDP, servidores
  multicliente, clientes robustos y el sistema de turnos.
- `Examen/P1/`, `Examen/P2/` y `Examen/P3/`: soluciones y capturas de
  demostración de las prácticas 1, 2 y 3; `P3` también incluye `Server.py`.
- `Examen/P4/`: implementación de **LA FILA** con
  `P4_Servidor.py`, `P4_cliente_tcp.py` y `P4_cliente_udp.py`, junto con las
  capturas de cliente TCP, cliente UDP y servidor.

## Protocolos destacados

| Sistema | Transporte | Puerto | Mensajes principales |
|---|---|---:|---|
| Eco | TCP | Según el script | Texto enviado y devuelto por el servidor |
| Eco | UDP | Según el script | Datagramas independientes |
| Batalla naval | TCP o UDP | `5050` | Coordenada → `TOCADO`/`AGUA` |
| LA FILA | TCP | `5000` | `TURNO>apodo\n` → `turno>N\n` |
| LA FILA | UDP | `5001` | `CUANTOS` → `van>N\n` |

Los puertos y hosts pueden variar entre ejercicios; consulta las constantes al
inicio de cada archivo antes de conectar clientes y servidores.

## Uso general

Ejecuta cada programa desde su propia carpeta, por ejemplo:

```powershell
python nombre_del_archivo.py
```

Algunos scripts son servidores de ejecución continua y se detienen con
`Ctrl+C`. Los archivos de examen y las capturas se conservan como material de
referencia y no forman un paquete instalable.

---

**Última actualización:** 15 de octubre de 2026
