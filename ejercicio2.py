# --- Ejercicio 2 ---
def es_puerto_valido(puerto: int) -> bool:
    return 0 <= puerto <= 65535


# Pruebas:
print(es_puerto_valido(5000))   # True
print(es_puerto_valido(70000))  # False