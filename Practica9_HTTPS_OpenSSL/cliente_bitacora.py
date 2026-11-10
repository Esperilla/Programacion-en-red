# =============================================================================
# Practica 9 - Ejercicio 6: cliente de la bitacora sobre HTTPS (requests)
# -----------------------------------------------------------------------------
# Igual que en la Practica 8, pero contra https://localhost:8443. Todas las
# peticiones verifican el certificado del servidor con verify="certificado.pem"
# (el equivalente a curl --cacert). Al final se muestra, solo como
# demostracion, que verify=False (= curl -k) funciona pero lanza
# InsecureRequestWarning: eso jamas debe quedar en codigo real.
# -----------------------------------------------------------------------------
# Recorre el ciclo CRUD completo contra servidor_bitacora.py:
#   crear (POST) -> consultar (GET, con filtros) -> modificar (PATCH)
#   -> reemplazar (PUT) -> borrar (DELETE) -> errores 4xx -> auditoria.
#
# Requiere: pip install requests
# Arranca primero el servidor: python servidor_bitacora.py
# =============================================================================
import json

import requests

BASE = "https://localhost:8443"
CA = "certificado.pem"  # certificado autofirmado en el que confiamos


def mostrar(titulo, r):
    """Imprime el codigo de estado y el cuerpo JSON (si lo hay) de una respuesta."""
    print(f"\n--- {titulo} ---")
    print(f"{r.request.method} {r.url} -> {r.status_code}")
    if r.content:
        print(json.dumps(r.json(), ensure_ascii=False, indent=2))


def main():
    try:
        requests.head(BASE, timeout=5, verify=CA)
    except requests.exceptions.SSLError as e:
        print(f"Fallo la verificacion TLS: {e}")
        return
    except requests.ConnectionError:
        print(f"No se pudo conectar a {BASE}. ¿Esta corriendo servidor_bitacora.py?")
        return

    # Crear: los datos van en el cuerpo (json=)
    r = requests.post(f"{BASE}/incidencias",
                      json={"tipo": "alerta", "descripcion": "Escaneo de puertos"},
                      timeout=10, verify=CA)
    mostrar("POST crear alerta", r)
    creada = r.json()

    r = requests.post(f"{BASE}/incidencias",
                      json={"tipo": "vulnerabilidad", "descripcion": "SSH con contrasena debil",
                            "estado": "en_proceso"},
                      timeout=10, verify=CA)
    mostrar("POST crear vulnerabilidad en_proceso", r)
    segunda = r.json()

    # Consultar: el filtro va en la URL (params=)
    mostrar("GET todas", requests.get(f"{BASE}/incidencias", timeout=10, verify=CA))
    mostrar("GET solo tipo=alerta",
            requests.get(f"{BASE}/incidencias", params={"tipo": "alerta"}, timeout=10, verify=CA))

    # Ejercicio 5: filtros combinados
    for params in ({"estado": "abierta"},
                   {"estado": "en_proceso"},
                   {"tipo": "alerta", "estado": "abierta"},
                   {"tipo": "alerta", "estado": "resuelta"},
                   {"tipo": "vulnerabilidad", "estado": "en_proceso"}):
        r = requests.get(f"{BASE}/incidencias", params=params, timeout=10, verify=CA)
        print(f"\nGET {r.url} -> {r.status_code}, {len(r.json())} resultado(s)")

    # Modificar: id en la ruta, cambios en el cuerpo
    r = requests.patch(f"{BASE}/incidencias/{creada['id']}",
                       json={"estado": "resuelta"}, timeout=10, verify=CA)
    mostrar("PATCH estado=resuelta", r)

    # Ejercicio 1: estado fuera del vocabulario -> 400
    r = requests.patch(f"{BASE}/incidencias/{creada['id']}",
                       json={"estado": "cerrada"}, timeout=10, verify=CA)
    mostrar("PATCH estado invalido (400)", r)
    r = requests.post(f"{BASE}/incidencias",
                      json={"tipo": "alerta", "descripcion": "x", "estado": "pendiente"},
                      timeout=10, verify=CA)
    mostrar("POST estado invalido (400)", r)

    # Ejercicio 4: PUT reemplaza el registro completo (estado vuelve a abierta)
    r = requests.put(f"{BASE}/incidencias/{creada['id']}",
                     json={"tipo": "incidente", "descripcion": "Ransomware en equipo de caja"},
                     timeout=10, verify=CA)
    mostrar("PUT reemplazo completo", r)
    r = requests.put(f"{BASE}/incidencias/{creada['id']}",
                     json={"tipo": "incidente"}, timeout=10, verify=CA)
    mostrar("PUT sin descripcion (400)", r)

    # Borrar: solo el id en la ruta; 204 no trae cuerpo
    r = requests.delete(f"{BASE}/incidencias/{segunda['id']}", timeout=10, verify=CA)
    mostrar("DELETE (204)", r)

    # Comprobar el codigo antes de usar el cuerpo
    r = requests.get(f"{BASE}/incidencias/999", timeout=10, verify=CA)
    if r.status_code == 404:
        print("\nno existe:", r.json()["error"])

    # La auditoria del servidor, desde fuera
    mostrar("GET /contadores", requests.get(f"{BASE}/contadores", timeout=10, verify=CA))
    mostrar("GET /logs", requests.get(f"{BASE}/logs", timeout=10, verify=CA))

    # Comparacion de verificacion (lo mismo que curl --cacert / curl -k / curl sin CA)
    print("\n--- Verificacion del certificado ---")
    r = requests.get(f"{BASE}/incidencias", verify=CA, timeout=10)
    print(f"verify='{CA}'  -> {r.status_code} (correcto: se valida la identidad)")
    try:
        requests.get(f"{BASE}/incidencias", timeout=10)  # usa las CA del sistema
    except requests.exceptions.SSLError:
        print("verify=True (CA del sistema) -> SSLError: nadie reconocido firmo el certificado")
    import warnings
    with warnings.catch_warnings(record=True) as avisos:
        warnings.simplefilter("always")
        r = requests.get(f"{BASE}/incidencias", verify=False, timeout=10)  # mala practica
    print(f"verify=False -> {r.status_code}, avisos: "
          f"{[a.category.__name__ for a in avisos]}  (mala practica)")


if __name__ == "__main__":
    main()
