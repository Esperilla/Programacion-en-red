"""Servicio de apoyo para la Práctica 12.

API REST mínima de una bitácora de incidentes de ciberseguridad.
Crea su propia base SQLite y precarga un activo de ejemplo.
Ejecutar: python servicio_minimo.py
"""
import sqlite3
from pathlib import Path

from flask import Flask, jsonify, request

app = Flask(__name__)
RUTA_BD = Path(__file__).with_name("bitacora.sqlite")


def get_db():
    """Abre una conexión con filas tipo diccionario y claves foráneas activas."""
    conexion = sqlite3.connect(RUTA_BD)
    conexion.row_factory = sqlite3.Row
    conexion.execute("PRAGMA foreign_keys = ON")
    return conexion


def inicializar_bd():
    """Crea las tablas si no existen y precarga el activo de demostración."""
    with get_db() as conexion:
        conexion.executescript(
            """
            CREATE TABLE IF NOT EXISTS activos (
                id INTEGER PRIMARY KEY,
                nombre TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS incidentes (
                id INTEGER PRIMARY KEY,
                activo_id INTEGER NOT NULL REFERENCES activos(id),
                descripcion TEXT NOT NULL,
                severidad TEXT NOT NULL,
                estado TEXT NOT NULL DEFAULT 'abierto',
                accion_tomada TEXT
            );
            INSERT OR IGNORE INTO activos (id, nombre)
            VALUES (1, 'PC-LAB-01');
            """
        )


@app.get("/api/salud")
def salud():
    """Confirma que el servicio está disponible."""
    return jsonify({"estado": "ok"})


@app.get("/api/activos")
def listar_activos():
    """Devuelve todos los activos registrados."""
    with get_db() as conexion:
        filas = conexion.execute("SELECT * FROM activos").fetchall()
    return jsonify([dict(fila) for fila in filas])


@app.get("/api/activos/<int:activo_id>")
def consultar_activo(activo_id):
    """Devuelve un activo por id o 404 si no existe."""
    with get_db() as conexion:
        fila = conexion.execute(
            "SELECT * FROM activos WHERE id = ?", (activo_id,)
        ).fetchone()
    if fila is None:
        return jsonify({"error": "Activo no encontrado"}), 404
    return jsonify(dict(fila))


@app.get("/api/incidentes")
def listar_incidentes():
    """Devuelve todos los incidentes registrados."""
    with get_db() as conexion:
        filas = conexion.execute("SELECT * FROM incidentes").fetchall()
    return jsonify([dict(fila) for fila in filas])


@app.post("/api/incidentes")
def registrar_incidente():
    """Registra un incidente abierto asociado a un activo existente."""
    datos = request.get_json(silent=True) or {}
    for campo in ("activo_id", "descripcion", "severidad"):
        if campo not in datos:
            return jsonify({"error": f"Falta el campo {campo}"}), 400

    with get_db() as conexion:
        try:
            cursor = conexion.execute(
                "INSERT INTO incidentes (activo_id, descripcion, severidad)"
                " VALUES (?, ?, ?)",
                (datos["activo_id"], datos["descripcion"], datos["severidad"]),
            )
            conexion.commit()
        except sqlite3.IntegrityError:
            return jsonify({"error": "El activo no existe"}), 404
    return jsonify({"id": cursor.lastrowid, "estado": "abierto"}), 201


@app.put("/api/incidentes/<int:incidente_id>/resolucion")
def resolver_incidente(incidente_id):
    """Marca un incidente abierto como resuelto; exige la acción tomada."""
    datos = request.get_json(silent=True) or {}
    accion = datos.get("accion_tomada", "").strip()
    if not accion:
        return jsonify({"error": "Se requiere accion_tomada"}), 400

    with get_db() as conexion:
        incidente = conexion.execute(
            "SELECT estado FROM incidentes WHERE id = ?", (incidente_id,)
        ).fetchone()
        if incidente is None:
            return jsonify({"error": "Incidente no encontrado"}), 404
        if incidente["estado"] != "abierto":
            return jsonify({"error": "El incidente ya está resuelto"}), 409
        conexion.execute(
            "UPDATE incidentes SET estado = 'resuelto', accion_tomada = ?"
            " WHERE id = ?",
            (accion, incidente_id),
        )
        conexion.commit()
    return jsonify({"id": incidente_id, "estado": "resuelto"})


if __name__ == "__main__":
    inicializar_bd()
    app.run(debug=True)
