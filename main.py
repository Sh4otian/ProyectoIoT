from flask import Flask,render_template, request
from BD.db import ConsultaTot,GuardarRes,EstadoDB
from ModelIA.PruebaIA import clasificar_img
from mqtt.mqtt_client import PublicarCat,EstadoMQTT

import os
import random

Carpeta = "ModelIA/Pruebas"

def SysEdo():
	mqtt=EstadoMQTT()
	return {"mqtt":mqtt,"BD":EstadoDB(),"Camara":{"Estado":"INEXISTENTE"}, "Flask":"ACTIVO"}

def ImgAle():
	archivos = [f for f in os.listdir(Carpeta)
	if f.lower().endswith((".jpg", ".jpeg", ".png"))]

	if not archivos:
		return None
	seleccion = random.choice(archivos)
	return os.path.join(Carpeta, seleccion)

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
@app.route("/")
def Inicio():
	return render_template("index.html")

@app.route("/EstadoSis")
def configuracion():
	estado= SysEdo()
	return render_template("EstadoSis.html", estado=estado)

@app.route("/historial")
def historial():
	datos = ConsultaTot()

	return render_template("historial.html",Dat=datos)

@app.route("/simular", methods=["POST"])
def simular():

    if "imagen" not in request.files:
        return "No se recibio ninguna imagen"

    archivo = request.files["imagen"]

    if archivo.filename == "":
        return "No se selecciono archivo"

    ruta = os.path.join(
        UPLOAD_FOLDER,
        archivo.filename
    )

    archivo.save(ruta)

    categoria, confianza = clasificar_img(ruta)

    PublicarCat(categoria)

    GuardarRes(
        ruta,
        categoria,
        confianza
    )

    return f"""
        Clasificacion realizada<br><br>

        Archivo: {archivo.filename}<br>
        Categoroa: {categoria}<br>
        Confianza: {confianza:.2f}%<br>
    """
if __name__== "__main__":
	app.run(host="0.0.0.0", port=5000,debug=True)
