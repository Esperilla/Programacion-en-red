"""Presentación de los activos registrados en el servicio."""
import api


def listar():
    """Consulta los activos y los presenta al usuario."""
    datos = api.listar_activos()

    # TODO 4: presentar los activos como una tabla sencilla de texto.
    if not datos:
        print("No hay activos registrados.")
        return

    print(f"\n{'ID':>4}  Nombre")
    print(f"{'-' * 4}  {'-' * 20}")
    for activo in datos:
        print(f"{activo['id']:>4}  {activo['nombre']}")
    print(f"\nTotal: {len(datos)} activo(s).")
