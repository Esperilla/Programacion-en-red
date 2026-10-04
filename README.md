# Programación en Red

## Descripción

Repositorio que contiene todas las actividades, ejercicios y proyectos asignados durante el curso de **Programación en Red** — *Universidad Veracruzana · Unidad II*.  
Cubre los fundamentos de comunicación de datos: sockets TCP/UDP, bloqueo, framing, concurrencia con hilos y arquitecturas cliente-servidor.

---

## Estructura del Repositorio

```
Programacion-en-red/
│
├── ejercicio1.py                              # Ejercicio básico 1
├── ejercicio2.py                              # Ejercicio básico 2
├── ejercicio3.py                              # Ejercicio básico 3
│
├── codigo1_EcoTCP_servidor.py                 # Servidor eco TCP (bloqueante, 1 cliente)
├── codigo2_EcoTCP_cliente.py                  # Cliente eco TCP
│
├── codigo3_Demostracion_Bloqueo_servidor.py   # Demostración de bloqueo en TCP (servidor)
├── codigo3_Demostracion_Bloqueo_cliente.py    # Demostración de bloqueo en TCP (cliente)
│
├── codigo4_EcoUDP_servidor.py                 # Servidor eco UDP
├── codigo4_EcoUDP_cliente.py                  # Cliente eco UDP
│
├── codigo5_Framing_servidor.py                # Servidor con framing por delimitador \n
├── codigo5_Framing_cliente.py                 # Cliente con framing por delimitador \n
│
├── codigo_limpio.py                           # Código de referencia / plantilla limpia
│
├── 01-Actividad Práctica batalla naval TCP-UDP/
│   ├── battleship_attack.py                   # Cliente atacante (TCP)
│   ├── battleship_attack_udp.py               # Cliente atacante (UDP)
│   ├── battleship_defend.py                   # Servidor defensor (TCP)
│   └── battleship_defend_udp.py               # Servidor defensor (UDP)
│
└── Actividad 6/                               # Sistema de turnos "LA FILA"
    ├── servidor_turnos.py                     # Servidor concurrente TCP+UDP con hilos
    ├── cliente_turno_tcp.py                   # Cliente que solicita turno vía TCP
    ├── cliente_consulta_udp.py                # Cliente que consulta turnos vía UDP
    └── Guia_Concurrencia_Hilos_TCP_y_UDP.pdf  # Guía de referencia
```

---

## Contenido del Curso

### Ejercicios Básicos
- **ejercicio1.py** – Conceptos fundamentales de sockets
- **ejercicio2.py** – Ejercicio práctico de comunicación
- **ejercicio3.py** – Ejercicio práctico avanzado

### Códigos de Demostración

| Archivo | Protocolo | Descripción |
|---|---|---|
| `codigo1_EcoTCP_servidor/cliente` | TCP | Servidor eco clásico (un cliente a la vez, bloqueante) |
| `codigo3_Demostracion_Bloqueo_*` | TCP | Muestra el comportamiento bloqueante de `accept()` y `recv()` |
| `codigo4_EcoUDP_servidor/cliente` | UDP | Eco sin conexión mediante datagramas |
| `codigo5_Framing_servidor/cliente` | TCP | Recepción robusta con delimitador `\n` para evitar mensajes pegados/partidos |

### Proyectos Prácticos

#### 01 — Batalla Naval TCP/UDP
Implementación de un juego de batalla naval usando sockets TCP y UDP.  
El atacante envía coordenadas y el defensor responde si fue agua o impacto.

#### Actividad 6 — Sistema de Turnos "LA FILA"
Sistema de gestión de turnos con arquitectura **TCP + UDP concurrente**:

- **TCP (puerto 5000)**: un hilo por cliente. El cliente envía `TURNO>apodo\n` y recibe `turno>N\n`.
- **UDP (puerto 5001)**: hilo dedicado. El cliente envía `CUANTOS` y recibe `van>N\n`.
- El contador de turnos es una **sección crítica** protegida con `threading.Lock()`.

```bash
# Ejecutar el servidor
python servidor_turnos.py

# En otras terminales:
python cliente_turno_tcp.py      # Solicitar un turno
python cliente_consulta_udp.py   # Consultar cuántos turnos van
```

---

## Requisitos

- Python 3.x
- Conocimientos básicos de networking
- Módulos estándar: `socket`, `threading`

---

## Uso

Cada archivo incluye comentarios detallados sobre su funcionamiento.  
Para los proyectos que involucran cliente y servidor, abre **dos terminales** y ejecuta primero el servidor.

---

**Última actualización**: Octubre 2026