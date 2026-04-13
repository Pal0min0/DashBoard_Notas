import os
import pandas as pd
from flask import Flask, render_template, request, redirect, session, url_for, jsonify, send_file
from databases import (
    obtenerusuarios, registrar_usuario, verificar_password,
    obtenerestudiantes, agregar_estudiante, eliminar_estudiante,
    buscar_estudiantes, editar_estudiante, obtener_top_estudiantes,
    insertar_masivo, obtener_datos_reporte
)
from reporte_pdf import generar_reporte_pdf
from dashprincipal import creartablero

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "miku_secret_39c5bb_2026")

# Crear y montar el dashboard Dash dentro de Flask
creartablero(app)


# ── Sin caché en todas las respuestas ────────────────────────────────────────
@app.after_request
def add_header(response):
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"]        = "no-cache"
    response.headers["Expires"]       = "0"
    return response


# ── LOGIN / REGISTER / LOGOUT ────────────────────────────────────────────────

@app.route("/", methods=["GET", "POST"])
def login():
    if "username" in session:
        return redirect("/dashprincipal")

    error = None
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        usuario  = obtenerusuarios(username)

        if not usuario:
            error = "Usuario no encontrado"
        elif not verificar_password(usuario, password):
            error = "Contraseña incorrecta"
        else:
            session["username"] = usuario["username"]
            session["rol"]      = usuario["rol"]
            return redirect("/dashprincipal")

    return render_template("login.html", error=error)


@app.route("/register", methods=["GET", "POST"])
def register():
    if "username" in session:
        return redirect("/dashprincipal")

    error   = None
    success = None

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        confirm  = request.form.get("confirm",  "")

        if not username or not password:
            error = "Completa todos los campos"
        elif password != confirm:
            error = "Las contraseñas no coinciden"
        elif len(password) < 3:
            error = "La contraseña debe tener al menos 3 caracteres"
        else:
            ok = registrar_usuario(username, password, rol="docente")
            if ok:
                success = "Cuenta creada. Ya puedes iniciar sesión ✨"
            else:
                error = "El nombre de usuario ya existe"

    return render_template("register.html", error=error, success=success)


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


# ── DASHBOARD PRINCIPAL ───────────────────────────────────────────────────────

@app.route("/dashprincipal")
def dashprinci():
    if "username" not in session:
        return redirect("/")
    return render_template("dashprinci.html", usuario=session["username"])


# ── TOP ESTUDIANTES ───────────────────────────────────────────────────────────

@app.route("/top_estudiantes")
def top_estudiantes():
    if "username" not in session:
        return redirect("/")
    return render_template("top_estudiantes.html")


@app.route("/api/estudiantes/top")
def api_top():
    if "username" not in session:
        return jsonify({"ok": False, "error": "No autenticado"}), 401
    try:
        estudiantes = obtener_top_estudiantes(10)
        for e in estudiantes:
            e["promedio"] = float(e["promedio"])
        return jsonify({"ok": True, "estudiantes": estudiantes})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)})


# ── EDITAR ESTUDIANTES ────────────────────────────────────────────────────────

@app.route("/editar_estudiante")
def editar_estudiante_page():
    if "username" not in session:
        return redirect("/")
    return render_template("editar_estudiante.html")


@app.route("/api/estudiantes/buscar")
def api_buscar():
    if "username" not in session:
        return jsonify({"ok": False, "error": "No autenticado"}), 401
    nombre = request.args.get("nombre", "")
    try:
        estudiantes = buscar_estudiantes(nombre)
        return jsonify({"ok": True, "estudiantes": estudiantes})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e), "estudiantes": []})


@app.route("/api/estudiantes/editar", methods=["POST"])
def api_editar():
    if "username" not in session:
        return jsonify({"ok": False, "error": "No autenticado"}), 401
    datos = request.get_json()
    try:
        editar_estudiante(datos)
        return jsonify({"ok": True})
    except ValueError as e:
        return jsonify({"ok": False, "error": str(e)})
    except Exception as e:
        return jsonify({"ok": False, "error": f"Error al actualizar: {str(e)}"})


@app.route("/api/estudiantes/eliminar", methods=["POST"])
def api_eliminar():
    if "username" not in session:
        return jsonify({"ok": False, "error": "No autenticado"}), 401
    datos = request.get_json()
    try:
        eliminar_estudiante(datos["id"])
        return jsonify({"ok": True})
    except ValueError as e:
        return jsonify({"ok": False, "error": str(e)})
    except Exception as e:
        return jsonify({"ok": False, "error": f"Error al eliminar: {str(e)}"})


# ── CARGA MASIVA ──────────────────────────────────────────────────────────────

@app.route("/carga_masiva", methods=["GET", "POST"])
def carga_masiva():
    if "username" not in session:
        return redirect("/")

    if request.method == "GET":
        return render_template("carga_masiva.html")

    # POST — procesar archivo
    if "archivo" not in request.files:
        return jsonify({"ok": False, "error": "No se recibió ningún archivo."})

    archivo = request.files["archivo"]

    if archivo.filename == "":
        return jsonify({"ok": False, "error": "No seleccionaste ningún archivo."})

    if not archivo.filename.endswith((".xlsx", ".xls")):
        return jsonify({"ok": False, "error": "El archivo debe ser .xlsx o .xls"})

    try:
        df = pd.read_excel(archivo)
        resultado = insertar_masivo(df)
        return jsonify({
            "ok":         True,
            "insertados": int(resultado["insertados"]),
            "duplicados": int(resultado["duplicados"]),
            "vacios":     int(resultado["vacios"]),
            "invalidos":  int(resultado["invalidos"]),
            "detalles":   resultado["errores"]
        })
    except ValueError as e:
        return jsonify({"ok": False, "error": str(e), "detalles": []})
    except Exception as e:
        return jsonify({"ok": False, "error": f"Error procesando el archivo: {str(e)}", "detalles": []})


# ── JUEGO EASTER EGG ──────────────────────────────────────────────────────────

@app.route("/juego")
def juego():
    return render_template("gallina-pro.html")


# ── REPORTE PDF ───────────────────────────────────────────────────────────────

@app.route("/api/estudiantes/reporte/<int:id_estudiante>")
def reporte_pdf(id_estudiante):
    if "username" not in session:
        return redirect("/")
    try:
        datos = obtener_datos_reporte(id_estudiante)
        if not datos:
            return jsonify({"ok": False, "error": "Estudiante no encontrado"}), 404
        pdf_bytes = generar_reporte_pdf(datos)
        nombre    = datos["estudiante"]["nombre"].replace(" ", "_")
        import io
        return send_file(
            io.BytesIO(pdf_bytes),
            mimetype="application/pdf",
            as_attachment=True,
            download_name=f"reporte_{nombre}.pdf"
        )
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)