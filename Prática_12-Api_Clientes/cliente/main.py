"""Punto de entrada del mini cliente de la bitácora."""
import requests

import activos
import incidentes
import resoluciones

OPCIONES = {
    "1": ("Listar activos", activos.listar),
    "2": ("Registrar incidente", incidentes.registrar),
    "3": ("Resolver incidente", resoluciones.resolver),
}


def menu():
    """Muestra el menú y ejecuta la opción elegida por el usuario."""
    while True:
        print("\n=== Bitácora de incidentes ===")
        for clave, (etiqueta, _) in OPCIONES.items():
            print(f"{clave}. {etiqueta}")
        print("0. Salir")
        opcion = input("Opción: ").strip()

        if opcion == "0":
            break
        if opcion not in OPCIONES:
            print("Opción no válida.")
            continue

        try:
            _, funcion = OPCIONES[opcion]
            funcion()
        except NotImplementedError as pendiente:
            print(f"Funcionalidad pendiente. {pendiente}")
        except requests.exceptions.ConnectionError:
            print("Error: no se pudo contactar al servicio. ¿Está en ejecución?")
        except requests.exceptions.Timeout:
            print("Error: el servicio no respondió a tiempo.")
        except requests.exceptions.HTTPError as error:
            print(f"Error del servicio: {error.response.status_code}")
        except (KeyError, TypeError, ValueError):
            print("Error: la respuesta del servicio no tiene el formato esperado.")


if __name__ == "__main__":
    menu()
