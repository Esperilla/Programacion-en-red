"""
Ejercicio 1 — Hilos con nombres propios
========================================
A partir del hola mundo con hilos, crear tres hilos cuyos nombres y número de
saludos salgan de una lista de tuplas: [("Ana", 3), ("Beto", 5), ("Cora", 2)].
Verificar que todos terminan antes del mensaje final.

Pistas:
  - Un ciclo for que crea los Thread guardándolos en una lista.
  - Un segundo ciclo para hacer .join() a cada uno.
Se evalúa: salida entrelazada, mensaje final SIEMPRE al final, código limpio.
"""

import threading
import time


def saludar(nombre: str, veces: int) -> None:
    """Imprime 'veces' saludos con el nombre del hilo."""
    for i in range(1, veces + 1):
        print(f"[{nombre}] Hola #{i}")
        time.sleep(0.1)          # simula trabajo breve
    print(f"[{nombre}] ¡Terminé mis {veces} saludos!")


def main() -> None:
    # Lista de tuplas (nombre, número_de_saludos)
    participantes = [
        ("Ana",  3),
        ("Beto", 5),
        ("Cora", 2),
    ]

    # --- primer ciclo: crear y lanzar todos los hilos ---
    hilos: list[threading.Thread] = []
    for nombre, veces in participantes:
        hilo = threading.Thread(target=saludar, args=(nombre, veces), name=nombre)
        hilos.append(hilo)
        hilo.start()

    # --- segundo ciclo: esperar a que TODOS terminen ---
    for hilo in hilos:
        hilo.join()

    # Este mensaje aparece SIEMPRE después de que todos los hilos terminaron
    print("\n[OK] Todos los hilos han terminado. Fin del programa.")


if __name__ == "__main__":
    main()
