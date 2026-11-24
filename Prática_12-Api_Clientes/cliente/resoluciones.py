"""Captura de la acción tomada y resolución de incidentes."""
import api


def resolver():
    """Solicita los datos de resolución y muestra el resultado."""
    try:
        incidente_id = int(input("ID del incidente: ").strip())
    except ValueError:
        print("El ID del incidente debe ser un número entero.")
        return

    accion_tomada = input("Acción tomada: ").strip()
    if not accion_tomada:
        print("La acción tomada no puede estar vacía.")
        return

    respuesta = api.resolver_incidente(incidente_id, accion_tomada)

    # TODO 6: confirmación con el id y el estado recibidos.
    print(
        f"Incidente resuelto correctamente. "
        f"ID: {respuesta['id']} | Estado: {respuesta['estado']}"
    )
