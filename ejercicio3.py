# --- Ejercicio 3 ---
mensaje = "ana>luis:nos vemos a las 3"

# Separar emisor del resto usando '>'
remitente, resto = mensaje.split(">", 1)

# Separar destinatario del contenido usando ':'
destinatario, texto = resto.split(":", 1)

print(f"Remitente: {remitente}")
print(f"Destinatario: {destinatario}")
print(f"Texto: {texto}")

# --- Extra ---
# Codificar a bytes (por defecto UTF-8)
texto_bytes = texto.encode("utf-8")
print("Codificado (bytes):", texto_bytes)

# Decodificar de vuelta a string
texto_recuperado = texto_bytes.decode("utf-8")
print("Decodificado (str):", texto_recuperado)