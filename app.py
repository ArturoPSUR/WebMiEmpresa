import os
import sqlite3
from datetime import date

from flask import Flask, g, jsonify, request, send_from_directory

DB_PATH = os.environ.get("DB_PATH", "data/inventario.db")

TIPOS = ["Mobiliario", "Equipo informático", "Material didáctico",
         "Material de laboratorio", "Material deportivo",
         "Infraestructura", "Otro"]
ESTADOS = ["Nuevo", "Bueno", "Regular", "Deteriorado", "Baja"]
USOS = ["Alto", "Medio", "Bajo"]

COLS = ("nombre", "tipo", "ubicacion", "fecha_adquisicion",
        "vida_util_anios", "estado", "uso")

SCHEMA = """
CREATE TABLE IF NOT EXISTS materiales (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre            TEXT    NOT NULL,
    tipo              TEXT    NOT NULL,
    ubicacion         TEXT    NOT NULL,
    fecha_adquisicion TEXT    NOT NULL,
    vida_util_anios   INTEGER NOT NULL CHECK (vida_util_anios > 0),
    estado            TEXT    NOT NULL,
    uso               TEXT    NOT NULL,
    creado_en         TEXT    DEFAULT CURRENT_TIMESTAMP
);
"""

app = Flask(__name__, static_folder="static", static_url_path="/static")


# ---------- Base de datos ----------
def init_db():
    os.makedirs(os.path.dirname(os.path.abspath(DB_PATH)), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.executescript(SCHEMA)
    conn.commit()
    conn.close()


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(_exc):
    db = g.pop("db", None)
    if db is not None:
        db.close()


init_db()


# ---------- Validación ----------
def validar(data):
    errores = {}
    if not isinstance(data, dict):
        return None, {"general": "El cuerpo debe ser un objeto JSON."}

    limpio = {}

    for campo in ("nombre", "ubicacion"):
        valor = data.get(campo)
        if not isinstance(valor, str) or not valor.strip():
            errores[campo] = "Campo obligatorio."
        elif len(valor.strip()) > 100:
            errores[campo] = "Máximo 100 caracteres."
        else:
            limpio[campo] = valor.strip()

    for campo, permitidos in (("tipo", TIPOS), ("estado", ESTADOS), ("uso", USOS)):
        valor = data.get(campo)
        if valor not in permitidos:
            errores[campo] = "Valor no válido. Opciones: " + ", ".join(permitidos)
        else:
            limpio[campo] = valor

    fecha = data.get("fecha_adquisicion")
    try:
        f = date.fromisoformat(fecha)
        if f > date.today():
            errores["fecha_adquisicion"] = "No puede ser una fecha futura."
        else:
            limpio["fecha_adquisicion"] = f.isoformat()
    except (TypeError, ValueError):
        errores["fecha_adquisicion"] = "Fecha no válida (formato AAAA-MM-DD)."

    vida = data.get("vida_util_anios")
    if isinstance(vida, bool) or not isinstance(vida, int) or not 1 <= vida <= 100:
        errores["vida_util_anios"] = "Debe ser un entero entre 1 y 100."
    else:
        limpio["vida_util_anios"] = vida

    return limpio, errores


def fila_o_404(db, item_id):
    return db.execute("SELECT * FROM materiales WHERE id = ?", (item_id,)).fetchone()


# ---------- API ----------
@app.get("/api/opciones")
def opciones():
    return jsonify({"tipos": TIPOS, "estados": ESTADOS, "usos": USOS})


@app.get("/api/materiales")
def listar():
    filas = get_db().execute("SELECT * FROM materiales ORDER BY id DESC").fetchall()
    return jsonify([dict(f) for f in filas])


@app.get("/api/materiales/<int:item_id>")
def obtener(item_id):
    fila = fila_o_404(get_db(), item_id)
    if fila is None:
        return jsonify({"error": "No encontrado"}), 404
    return jsonify(dict(fila))


@app.post("/api/materiales")
def crear():
    limpio, errores = validar(request.get_json(silent=True))
    if errores:
        return jsonify({"errores": errores}), 400
    db = get_db()
    cur = db.execute(
        f"INSERT INTO materiales ({', '.join(COLS)}) VALUES ({', '.join('?' * len(COLS))})",
        [limpio[c] for c in COLS],
    )
    db.commit()
    return jsonify(dict(fila_o_404(db, cur.lastrowid))), 201


@app.put("/api/materiales/<int:item_id>")
def actualizar(item_id):
    db = get_db()
    if fila_o_404(db, item_id) is None:
        return jsonify({"error": "No encontrado"}), 404
    limpio, errores = validar(request.get_json(silent=True))
    if errores:
        return jsonify({"errores": errores}), 400
    db.execute(
        f"UPDATE materiales SET {', '.join(c + ' = ?' for c in COLS)} WHERE id = ?",
        [limpio[c] for c in COLS] + [item_id],
    )
    db.commit()
    return jsonify(dict(fila_o_404(db, item_id)))


@app.delete("/api/materiales/<int:item_id>")
def eliminar(item_id):
    db = get_db()
    cur = db.execute("DELETE FROM materiales WHERE id = ?", (item_id,))
    db.commit()
    if cur.rowcount == 0:
        return jsonify({"error": "No encontrado"}), 404
    return "", 204


# ---------- Frontend ----------
@app.get("/")
def index():
    return send_from_directory(app.static_folder, "index.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)