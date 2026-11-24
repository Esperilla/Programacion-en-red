"""Captura y registro de incidentes."""
import api

SEVERIDADES = ("baja", "media", "alta", "critica")


def registrar():
    """Solicita los datos del incidente y muestra el resultado del registro."""
    try:
        activo_id = int(input("ID del activo: ").strip())
    except ValueError:
        print("El ID del activo debe ser un número entero.")
        return

    descripcion = input("Descripción: ").strip()
    if not descripcion:
        print("La descripción no puede estar vacía.")
        return

    severidad = input(f"Severidad {SEVERIDADES}: ").strip().lower()
    if severidad not in SEVERIDADES:
        print("Severidad no válida.")
        return

    respuesta = api.registrar_incidente(activo_id, descripcion, severidad)

    # TODO 5: confirmación con el id y el estado recibidos.
    print(
        f"Incidente registrado correctamente. "
        f"ID: {respuesta['id']} | Estado: {respuesta['estado']}"
    )
