from datetime import datetime
from bson.objectid import ObjectId
from flask import Flask, render_template, request, redirect, session
from pymongo import MongoClient
import certifi

app = Flask(__name__)

# ==========================
# SECRET KEY
# ==========================
app.secret_key = "ecoruta123"

# ==========================
# CONEXIÓN MONGODB
# ==========================
import ssl
import certifi

cliente = MongoClient(
    "mongodb+srv://refl090518mmcylsa1_db_user:pikis9002@cluster0.zkhjb4f.mongodb.net/?appName=Cluster0",
    tls=True,
    tlsCAFile=certifi.where(),
    tlsAllowInvalidCertificates=True
)

db = cliente["Ecoruta"]

coleccion_unidades = db["unidades"]
coleccion_colonias = db["colonias"]
coleccion_horarios = db["horarios"]
coleccion_rutas = db["rutas"]
coleccion_reportes = db["reportes"]
coleccion_observaciones = db["observaciones"]
coleccion_usuarios = db["usuarios"]

# ==========================
# INICIO
# ==========================
@app.route("/")
def inicio():
    if "usuario" not in session:
        return redirect("/login")
    return render_template("index.html")


# ==========================
# LOGIN
# ==========================
@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        correo = request.form["correo"]
        password = request.form["password"]

        usuario_db = coleccion_usuarios.find_one({
            "correo": correo,
            "password": password
        })

        if usuario_db:

            session["usuario"] = usuario_db["nombre"]
            session["rol"] = usuario_db["rol"]

            # 🔹 SOLO ADMIN O USUARIO NORMAL
            if usuario_db["rol"] == "admin":
                return redirect("/horarios.html")

            else:
                return redirect("/horarios.html")

        return render_template("login.html", error="Credenciales incorrectas")

    return render_template("login.html")

# ==========================
# REGISTRO
# ==========================
@app.route("/registro", methods=["GET", "POST"])
def registro():

    if request.method == "POST":

        datos = {
            "nombre": request.form["nombre"],
            "correo": request.form["correo"],
            "password": request.form["password"],
            "rol": "ciudadano"   # 🔹 fijo como antes
        }

        coleccion_usuarios.insert_one(datos)
        return redirect("/login")

    return render_template("registro.html")

# ==========================
# LOGOUT
# ==========================
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


# ==========================
# UNIDADES
# ==========================
@app.route("/unidades.html", methods=["GET", "POST"])
def unidades():

    if "rol" not in session:
        return redirect("/login")

    if request.method == "POST":

        if session["rol"] != "admin":
            return redirect("/")

        datos = {
            "numero": request.form["numero"],
            "placas": request.form["placas"],
            "modelo": request.form["modelo"],
            "capacidad": request.form["capacidad"],
            "toneladas": request.form["toneladas"],
            "conductor": request.form["conductor"],
            "estado": request.form["estado"]
        }

        numero_existente = coleccion_unidades.find_one({
            "numero": request.form["numero"]
        })

        if numero_existente:
            return "Error: Ese número de unidad ya existe"

        placa_existente = coleccion_unidades.find_one({
            "placas": request.form["placas"]
        })

        if placa_existente:
            return "Error: Esa placa ya está registrada"

        coleccion_unidades.insert_one(datos)

        return redirect("/unidades.html")

    return render_template(
        "unidades.html",
        unidades=list(coleccion_unidades.find())
    )


@app.route("/eliminar_unidad/<id>")
def eliminar_unidad(id):
    if "rol" not in session:
        return redirect("/login")
    if session["rol"] != "admin":
        return redirect("/")

    coleccion_unidades.delete_one({"_id": ObjectId(id)})
    return redirect("/unidades.html")


@app.route("/editar_unidad/<id>", methods=["GET", "POST"])
def editar_unidad(id):
    if "rol" not in session:
        return redirect("/login")
    if session["rol"] != "admin":
        return redirect("/")

    unidad = coleccion_unidades.find_one({"_id": ObjectId(id)})

    if request.method == "POST":
        datos = {
            "numero": request.form["numero"],
            "placas": request.form["placas"],
            "modelo": request.form["modelo"],
            "capacidad": request.form["capacidad"],
            "toneladas": request.form["toneladas"],
            "conductor": request.form["conductor"],
            "estado": request.form["estado"]
        }
        coleccion_unidades.update_one(
            {"_id": ObjectId(id)},
            {"$set": datos}
        )
        return redirect("/unidades.html")

    return render_template("editar_unidad.html", unidad=unidad)


# ==========================
# COLONIAS
# ==========================
@app.route("/colonias.html", methods=["GET", "POST"])
def colonias():

    if "rol" not in session:
        return redirect("/login")

    if request.method == "POST":

        if session["rol"] != "admin":
            return redirect("/")

        colonia_existente = coleccion_colonias.find_one({
            "nombre": request.form["nombre"]
        })

        if colonia_existente:
            return "Error: Esta colonia ya existe"

        datos = {
            "nombre": request.form["nombre"],
            "cp": request.form["cp"],
            "zona": request.form["zona"],
            "habitantes": request.form["habitantes"],
            "unidad": request.form["unidad"]
        }

        coleccion_colonias.insert_one(datos)

        return redirect("/colonias.html")

    return render_template(
        "colonias.html",
        colonias=list(coleccion_colonias.find()),
        unidades=list(coleccion_unidades.find())
    )

@app.route("/eliminar_colonia/<id>")
def eliminar_colonia(id):
    if "rol" not in session:
        return redirect("/login")
    if session["rol"] != "admin":
        return redirect("/")

    coleccion_colonias.delete_one({"_id": ObjectId(id)})
    return redirect("/colonias.html")


@app.route("/editar_colonia/<id>", methods=["GET", "POST"])
def editar_colonia(id):
    if "rol" not in session:
        return redirect("/login")
    if session["rol"] != "admin":
        return redirect("/")

    colonia = coleccion_colonias.find_one({"_id": ObjectId(id)})

    if request.method == "POST":
        datos = {
            "nombre": request.form["nombre"],
            "cp": request.form["cp"],
            "zona": request.form["zona"],
            "habitantes": request.form["habitantes"],
            "unidad": request.form["unidad"]
        }
        coleccion_colonias.update_one(
            {"_id": ObjectId(id)},
            {"$set": datos}
        )
        return redirect("/colonias.html")

    return render_template(
        "editar_colonia.html",
        colonia=colonia,
        unidades=list(coleccion_unidades.find())
    )


# ==========================
# HORARIOS
# ==========================
@app.route("/horarios.html", methods=["GET", "POST"])
def horarios():

    if "rol" not in session:
        return redirect("/login")

    if request.method == "POST":

        if session["rol"] != "admin":
            return redirect("/")

        horario_existente = coleccion_horarios.find_one({
            "unidad": request.form["unidad"],
            "hora_inicio": request.form["hora_inicio"],
            "hora_fin": request.form["hora_fin"]
        })

        if horario_existente:
            return "Error: Esa unidad ya tiene un horario asignado."

        # Validar que se haya seleccionado al menos un día
        dias = request.form.getlist("dias")

        if not dias:
            return "Error: Debes seleccionar al menos un día de operación."


        datos = {
            "ruta": request.form["ruta"],
            "unidad": request.form["unidad"],
            "turno": request.form["turno"],
            "estado": request.form["estado"],
            "hora_inicio": request.form["hora_inicio"],
            "hora_fin": request.form["hora_fin"],
            "dias": request.form.getlist("dias")
        }

        coleccion_horarios.insert_one(datos)

        return redirect("/horarios.html")

    return render_template(
        "horarios.html",
        horarios=list(coleccion_horarios.find()),
        unidades=list(coleccion_unidades.find())
    )


@app.route("/eliminar_horario/<id>")
def eliminar_horario(id):
    if "rol" not in session:
        return redirect("/login")
    if session["rol"] != "admin":
        return redirect("/")

    coleccion_horarios.delete_one({"_id": ObjectId(id)})
    return redirect("/horarios.html")


@app.route("/editar_horario/<id>", methods=["GET", "POST"])
def editar_horario(id):
    if "rol" not in session:
        return redirect("/login")

    if session["rol"] != "admin":
        return redirect("/")

    horario = coleccion_horarios.find_one({"_id": ObjectId(id)})

    if request.method == "POST":

        dias = request.form.getlist("dias")

        if not dias:
            return "Error: Debes seleccionar al menos un día de operación."

        datos = {
            "ruta": request.form["ruta"],
            "unidad": request.form["unidad"],
            "turno": request.form["turno"],
            "estado": request.form["estado"],
            "hora_inicio": request.form["hora_inicio"],
            "hora_fin": request.form["hora_fin"],
            "dias": dias
        }

        coleccion_horarios.update_one(
            {"_id": ObjectId(id)},
            {"$set": datos}
        )

        return redirect("/horarios.html")

    return render_template(
        "editar_horario.html",
        horario=horario,
        unidades=list(coleccion_unidades.find()),
        rutas=list(coleccion_rutas.find())
    )


# ==========================
# RUTAS
# ==========================
@app.route("/rutas.html", methods=["GET", "POST"])
def rutas():

    if "rol" not in session:
        return redirect("/login")

    if request.method == "POST":

        if session["rol"] != "admin":
            return redirect("/")

        ruta_existente = coleccion_rutas.find_one({
            "numero_ruta": request.form["numero_ruta"]
        })

        if ruta_existente:
            return "Error: Ese número de ruta ya existe"

        datos = {
            "numero_ruta": request.form["numero_ruta"],
            "nombre_ruta": request.form["nombre_ruta"],
            "origen": request.form["origen"],
            "destino": request.form["destino"],
            "estado": request.form["estado"]
        }

        coleccion_rutas.insert_one(datos)

        return redirect("/rutas.html")

    return render_template(
        "rutas.html",
        rutas=list(coleccion_rutas.find())
    )


@app.route("/eliminar_ruta/<id>")
def eliminar_ruta(id):
    if "rol" not in session:
        return redirect("/login")
    if session["rol"] != "admin":
        return redirect("/")

    coleccion_rutas.delete_one({"_id": ObjectId(id)})
    return redirect("/rutas.html")


@app.route("/editar_ruta/<id>", methods=["GET", "POST"])
def editar_ruta(id):
    if "rol" not in session:
        return redirect("/login")
    if session["rol"] != "admin":
        return redirect("/")

    ruta = coleccion_rutas.find_one({"_id": ObjectId(id)})

    if request.method == "POST":
        datos = {
            "numero_ruta": request.form["numero_ruta"],
            "nombre_ruta": request.form["nombre_ruta"],
            "origen": request.form["origen"],
            "destino": request.form["destino"],
            "estado": request.form["estado"]
        }
        coleccion_rutas.update_one(
            {"_id": ObjectId(id)},
            {"$set": datos}
        )
        return redirect("/rutas.html")

    return render_template("editar_ruta.html", ruta=ruta)


# ==========================
# REPORTES
# ==========================
@app.route("/reportes_ciudadanos.html", methods=["GET", "POST"])
def reportes_ciudadanos():

    if "rol" not in session:
        return redirect("/login")

    if request.method == "POST":

        # El administrador no puede crear reportes
        if session["rol"] == "admin":
            return redirect("/reportes_ciudadanos.html")

        datos = {
            "usuario": session["usuario"],
            "problema": request.form["problema"],
            "descripcion": request.form["descripcion"],
            "fecha": datetime.now().strftime("%d/%m/%Y"),
            "colonia": request.form["colonia"]
        }

        coleccion_reportes.insert_one(datos)

        return redirect("/reportes_ciudadanos.html")

    return render_template(
        "reportes_ciudadanos.html",
        reportes=list(coleccion_reportes.find())
    )

@app.route("/eliminar_reporte/<id>")
def eliminar_reporte(id):

    if "usuario" not in session:
        return redirect("/login")

    reporte = coleccion_reportes.find_one({
        "_id": ObjectId(id)
    })

    if not reporte:
        return redirect("/reportes_ciudadanos.html")

    # SOLO EL DUEÑO DEL REPORTE
    if reporte["usuario"] != session["usuario"]:
        return redirect("/reportes_ciudadanos.html")

    coleccion_reportes.delete_one({
        "_id": ObjectId(id)
    })

    return redirect("/reportes_ciudadanos.html")

@app.route("/editar_reporte/<id>", methods=["GET", "POST"])
def editar_reporte(id):

    if "usuario" not in session:
        return redirect("/login")

    reporte = coleccion_reportes.find_one({
        "_id": ObjectId(id)
    })

    if not reporte:
        return redirect("/reportes_ciudadanos.html")

    # SOLO EL DUEÑO DEL REPORTE
    if reporte["usuario"] != session["usuario"]:
        return redirect("/reportes_ciudadanos.html")

    if request.method == "POST":

        datos = {
            "problema": request.form["problema"],
            "descripcion": request.form["descripcion"],
            "colonia": request.form["colonia"]
        }

        coleccion_reportes.update_one(
            {"_id": ObjectId(id)},
            {"$set": datos}
        )

        return redirect("/reportes_ciudadanos.html")

    return render_template(
        "editar_reporte.html",
        reporte=reporte
    )

# ==========================
# OBSERVACIONES
# ==========================
@app.route("/observaciones.html", methods=["GET", "POST"])
def observaciones():

    if "rol" not in session:
        return redirect("/login")

    # El administrador no puede crear observaciones
    if request.method == "POST":

        if session["rol"] == "admin":
            return redirect("/observaciones.html")

        datos = {
            "unidad": request.form["unidad"],
            "observacion": request.form["observacion"],
            "fecha": datetime.now().strftime("%d/%m/%Y"),
            "estado": "Activa",
            "usuario": session["usuario"]
        }

        coleccion_observaciones.insert_one(datos)

        return redirect("/observaciones.html")

    return render_template(
        "observaciones.html",
        observaciones=list(coleccion_observaciones.find()),
        unidades=list(coleccion_unidades.find())
    )

@app.route("/eliminar_observacion/<id>")
def eliminar_observacion(id):

    if "rol" not in session:
        return redirect("/login")

    observacion = coleccion_observaciones.find_one({
        "_id": ObjectId(id)
    })

    if session["rol"] != "admin" and observacion["usuario"] != session["usuario"]:
        return redirect("/observaciones.html")

    coleccion_observaciones.delete_one({
        "_id": ObjectId(id)
    })

    return redirect("/observaciones.html")
@app.route("/editar_observacion/<id>", methods=["GET","POST"])
def editar_observacion(id):

    if "rol" not in session:
        return redirect("/login")

    observacion = coleccion_observaciones.find_one({
        "_id": ObjectId(id)
    })

    if session["rol"] != "admin" and observacion["usuario"] != session["usuario"]:
        return redirect("/observaciones.html")

    if request.method == "POST":

        datos = {
            "unidad": request.form["unidad"],
            "observacion": request.form["observacion"],
            "fecha": request.form["fecha"],
            "estado": request.form["estado"]
        }

        coleccion_observaciones.update_one(
            {"_id": ObjectId(id)},
            {"$set": datos}
        )

        return redirect("/observaciones.html")

    return render_template(
        "editar_observacion.html",
        observacion=observacion
    )


@app.route("/conductor")
def conductor():

    if "rol" not in session:
        return redirect("/login")

    if session["rol"] != "conductor":
        return redirect("/")

    return render_template("conductor.html")

# ==========================
# EJECUTAR APP
# ==========================
if __name__ == "__main__":
    app.run(debug=True)