"""Comunicación HTTP entre el cliente y el servicio de la bitácora."""
import requests

BASE_URL = "http://localhost:5000/api"
TIMEOUT = 5


def listar_activos():
    """Devuelve la lista de activos obtenida del servicio."""
    # TODO 1: GET /activos con límite de espera; un 4xx/5xx lanza HTTPError.
    respuesta = requests.get(f"{BASE_URL}/activos", timeout=TIMEOUT)
    respuesta.raise_for_status()
    return respuesta.json()


def registrar_incidente(activo_id, descripcion, severidad):
    """Registra un incidente y devuelve la respuesta del servicio."""
    # TODO 2: el diccionario se serializa a JSON con json= (Content-Type incluido).
    datos = {
        "activo_id": activo_id,
        "descripcion": descripcion,
        "severidad": severidad,
    }
    respuesta = requests.post(f"{BASE_URL}/incidentes", json=datos, timeout=TIMEOUT)
    respuesta.raise_for_status()
    return respuesta.json()


def resolver_incidente(incidente_id, accion_tomada):
    """Marca un incidente como resuelto y devuelve la respuesta."""
    # TODO 3: PUT sobre el sub-recurso de resolución del incidente.
    datos = {"accion_tomada": accion_tomada}
    respuesta = requests.put(
        f"{BASE_URL}/incidentes/{incidente_id}/resolucion",
        json=datos,
        timeout=TIMEOUT,
    )
    respuesta.raise_for_status()
    return respuesta.json()
