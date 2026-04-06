import mysql.connector
import pandas as pd
import os
from werkzeug.security import generate_password_hash, check_password_hash


def conectar():
    conexion = mysql.connector.connect(
         host=os.environ.get("DB_HOST", "localhost"),
        user=os.environ.get("DB_USER", "root"),
        password=os.environ.get("DB_PASSWORD", ""),
        database=os.environ.get("DB_NAME", "dashnotas"),
        port=int(os.environ.get("DB_PORT", 3306))
    )
    return conexion


# ─── USUARIOS ────────────────────────────────────────────────────────────────

def obtenerusuarios(username):
    conn = conectar()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM usuarios WHERE username = %s", (username,))
    usuario = cursor.fetchone()
    conn.close()
    return usuario


def registrar_usuario(username, password, rol="docente"):
    conn   = conectar()
    cursor = conn.cursor()
    hashed = generate_password_hash(password)
    try:
        cursor.execute(
            "INSERT INTO usuarios (username, password, rol) VALUES (%s, %s, %s)",
            (username, hashed, rol)
        )
        conn.commit()
        return True
    except mysql.connector.IntegrityError:
        return False          # username duplicado
    finally:
        conn.close()


def verificar_password(usuario_dict, password_ingresada):
    stored = usuario_dict["password"]
    # Soporta tanto hash werkzeug como contraseñas planas (legacy)
    if stored.startswith("pbkdf2:") or stored.startswith("scrypt:"):
        return check_password_hash(stored, password_ingresada)
    return stored == password_ingresada   # legacy plain-text


# ─── ESTUDIANTES — Lectura ────────────────────────────────────────────────────

def obtenerestudiantes():
    """Devuelve DataFrame con todos los estudiantes (para el dashboard Dash)."""
    conn = conectar()
    df   = pd.read_sql("SELECT * FROM estudiantes", conn)
    conn.close()
    df.columns = [c.capitalize() for c in df.columns]
    rename = {
        "Nota1": "Nota1", "Nota2": "Nota2", "Nota3": "Nota3",
        "Desempeno": "Desempeño"
    }
    df = df.rename(columns=rename)
    return df


def buscar_estudiantes(nombre):
    """Busca estudiantes por nombre (parcial). Si nombre está vacío devuelve todos."""
    conn   = conectar()
    cursor = conn.cursor(dictionary=True)
    if nombre.strip():
        cursor.execute("""
            SELECT * FROM estudiantes
            WHERE LOWER(nombre) LIKE LOWER(%s)
            ORDER BY nombre
        """, (f"%{nombre.strip()}%",))
    else:
        cursor.execute("SELECT * FROM estudiantes ORDER BY nombre")
    resultado = cursor.fetchall()
    cursor.close()
    conn.close()
    return resultado


def obtener_top_estudiantes(limite=10):
    """Devuelve los top N estudiantes ordenados por promedio calculado."""
    conn   = conectar()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT nombre, carrera, nota1, nota2, nota3,
               ROUND((nota1 + nota2 + nota3) / 3, 2) AS promedio
        FROM estudiantes
        ORDER BY promedio DESC
        LIMIT %s
    """, (limite,))
    resultado = cursor.fetchall()
    cursor.close()
    conn.close()
    return resultado


# ─── ESTUDIANTES — Escritura ──────────────────────────────────────────────────

def agregar_estudiante(nombre, edad, carrera, nota1, nota2, nota3):
    """Agrega un estudiante y calcula su promedio y desempeño."""
    promedio = round((nota1 + nota2 + nota3) / 3, 2)
    if promedio >= 4.5:
        desempeno = "Excelente"
    elif promedio >= 3.5:
        desempeno = "Bueno"
    elif promedio >= 3.0:
        desempeno = "Regular"
    else:
        desempeno = "Deficiente"

    conn   = conectar()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO estudiantes (nombre, edad, carrera, nota1, nota2, nota3, promedio, desempeno) "
        "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
        (nombre, edad, carrera, nota1, nota2, nota3, promedio, desempeno)
    )
    conn.commit()
    conn.close()
    return promedio, desempeno


def editar_estudiante(datos):
    """Actualiza los datos de un estudiante por su id."""
    conn   = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE estudiantes
        SET nombre = %s, edad = %s, carrera = %s,
            nota1  = %s, nota2 = %s, nota3   = %s,
            promedio = ROUND((%s + %s + %s) / 3, 2),
            desempeno = CASE
                WHEN ROUND((%s + %s + %s) / 3, 2) >= 4.5 THEN 'Excelente'
                WHEN ROUND((%s + %s + %s) / 3, 2) >= 3.5 THEN 'Bueno'
                WHEN ROUND((%s + %s + %s) / 3, 2) >= 3.0 THEN 'Regular'
                ELSE 'Deficiente'
            END
        WHERE id = %s
    """, (
        datos["nombre"], datos["edad"], datos["carrera"],
        datos["nota1"],  datos["nota2"], datos["nota3"],
        # para promedio
        datos["nota1"],  datos["nota2"], datos["nota3"],
        # para desempeno CASE (3 veces)
        datos["nota1"],  datos["nota2"], datos["nota3"],
        datos["nota1"],  datos["nota2"], datos["nota3"],
        datos["nota1"],  datos["nota2"], datos["nota3"],
        datos["id"]
    ))
    conn.commit()
    filas  = cursor.rowcount
    cursor.close()
    conn.close()
    if filas == 0:
        raise ValueError("No se encontró el estudiante con ese ID.")


def eliminar_estudiante(id_estudiante):
    """Elimina un estudiante por su id."""
    conn   = conectar()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM estudiantes WHERE id = %s", (id_estudiante,))
    conn.commit()
    filas  = cursor.rowcount
    cursor.close()
    conn.close()
    if filas == 0:
        raise ValueError("No se encontró el estudiante con ese ID.")


# ─── CARGA MASIVA ─────────────────────────────────────────────────────────────

def estudiante_existe(nombre, carrera, edad, cursor):
    cursor.execute("""
        SELECT COUNT(*) FROM estudiantes
        WHERE LOWER(nombre) = LOWER(%s)
          AND LOWER(carrera) = LOWER(%s)
          AND edad = %s
    """, (nombre.strip(), carrera.strip(), int(edad)))
    return cursor.fetchone()[0] > 0


def insertar_masivo(df_raw):
    resultado = {"insertados": 0, "duplicados": 0, "vacios": 0, "invalidos": 0, "errores": []}
    columnas_requeridas = ["nombre", "edad", "carrera", "nota1", "nota2", "nota3"]

    df = df_raw.copy()
    df.columns = [c.strip().lower() for c in df.columns]

    faltantes = [c for c in columnas_requeridas if c not in df.columns]
    if faltantes:
        raise ValueError(f"Columnas faltantes en el Excel: {', '.join(faltantes)}")

    df = df[columnas_requeridas]

    antes = len(df)
    df = df.dropna(how="all").dropna(subset=columnas_requeridas)
    resultado["vacios"] += antes - len(df)

    df["nombre"]  = df["nombre"].astype(str).str.strip().str.title()
    df["carrera"] = df["carrera"].astype(str).str.strip().str.title()

    for col in ["edad", "nota1", "nota2", "nota3"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    antes = len(df)
    df = df.dropna(subset=["edad", "nota1", "nota2", "nota3"])
    resultado["invalidos"] += antes - len(df)

    mask_edad = (df["edad"] >= 15) & (df["edad"] <= 80)
    for _, row in df[~mask_edad].iterrows():
        resultado["errores"].append(f"Edad inválida ({int(row['edad'])}) — {row['nombre']}")
    resultado["invalidos"] += (~mask_edad).sum()
    df = df[mask_edad]

    for nota in ["nota1", "nota2", "nota3"]:
        mask = (df[nota] >= 0) & (df[nota] <= 5)
        for _, row in df[~mask].iterrows():
            resultado["errores"].append(f"{nota} inválida ({row[nota]}) — {row['nombre']}")
        resultado["invalidos"] += (~mask).sum()
        df = df[mask]

    antes = len(df)
    df = df.drop_duplicates(subset=["nombre", "carrera", "edad"])
    resultado["duplicados"] += antes - len(df)

    if len(df) == 0:
        return resultado

    conn   = conectar()
    cursor = conn.cursor()

    for _, row in df.iterrows():
        try:
            if estudiante_existe(row["nombre"], row["carrera"], row["edad"], cursor):
                resultado["duplicados"] += 1
                resultado["errores"].append(
                    f"Ya existe en BD — {row['nombre']} ({row['carrera']}, {int(row['edad'])} años)")
                continue
            promedio = round((float(row["nota1"]) + float(row["nota2"]) + float(row["nota3"])) / 3, 2)
            if promedio >= 4.5:   desempeno = "Excelente"
            elif promedio >= 3.5: desempeno = "Bueno"
            elif promedio >= 3.0: desempeno = "Regular"
            else:                 desempeno = "Deficiente"

            cursor.execute("""
                INSERT INTO estudiantes (nombre, edad, carrera, nota1, nota2, nota3, promedio, desempeno)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (row["nombre"], int(row["edad"]), row["carrera"],
                  float(row["nota1"]), float(row["nota2"]), float(row["nota3"]),
                  promedio, desempeno))
            resultado["insertados"] += 1
        except Exception as e:
            resultado["errores"].append(f"Error insertando {row['nombre']}: {str(e)}")
            resultado["invalidos"] += 1

    conn.commit()
    cursor.close()
    conn.close()
    return resultado


if __name__ == "__main__":
    conn = conectar()
    print("Conexión exitosa")
    conn.close()


# ─── REPORTE PDF ──────────────────────────────────────────────────────────────

def obtener_datos_reporte(id_estudiante):
    """Devuelve todos los datos necesarios para generar el reporte PDF."""
    conn   = conectar()
    cursor = conn.cursor(dictionary=True)

    # datos del estudiante
    cursor.execute("SELECT * FROM estudiantes WHERE id = %s", (id_estudiante,))
    estudiante = cursor.fetchone()
    if not estudiante:
        conn.close()
        return None

    carrera = estudiante["carrera"]

    # estadísticas de la carrera
    cursor.execute("""
        SELECT
            ROUND(AVG(promedio), 2)                          AS promedio_carrera,
            COUNT(*)                                          AS total,
            SUM(CASE WHEN promedio >= 3.0 THEN 1 ELSE 0 END) AS aprobados,
            SUM(CASE WHEN promedio <  3.0 THEN 1 ELSE 0 END) AS reprobados
        FROM estudiantes
        WHERE carrera = %s
    """, (carrera,))
    stats = cursor.fetchone()

    # posición en el ranking de la carrera
    cursor.execute("""
        SELECT COUNT(*) AS pos
        FROM estudiantes
        WHERE carrera = %s AND promedio > %s
    """, (carrera, estudiante["promedio"]))
    pos_row = cursor.fetchone()
    posicion = (pos_row["pos"] or 0) + 1

    cursor.close()
    conn.close()

    return {
        "estudiante": estudiante,
        "stats":      stats,
        "posicion":   posicion,
    }