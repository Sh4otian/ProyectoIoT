from flask import Flask,render_template
from BD.db import ConsultaTot
from ModelIA.PruebaIA import clasificar_img
from mqtt.mqtt_client import PublicarCat
from BD.db import GuardarRes

import os
import random

Carpeta = "ModelIA/Pruebas"

def ImgAle():
	archivos = [f for f in os.listdir(Carpeta)
	if f.lower().endswith((".jpg", ".jpeg", ".png"))]

	if not archivos:
		return None
	seleccion = random.choice(archivos)
	return os.path.join(Carpeta, seleccion)

app = Flask(__name__)

@app.route("/")
def Inicio():
	return render_template("index.html")

@app.route("/EstadoSis")
def configuracion():
	return render_template("EstadoSis.html")

@app.route("/historial")
def historial():
	datos = ConsultaTot()

	return render_template("historial.html",Dat=datos)

@app.route("/simular")
def simular():
	path = ImgAle()
	
	if path is None:
		return "No hay Imagenes en la carpeta"

	categoria, confianza = clasificar_img(path)

	PublicarCat(categoria)
	GuardarRes(path,categoria,confianza)
	return f"""Simulacion realizada
		Imagen: {path}<br>
		Resultado: {categoria} ({confianza:.2f}%)"""

if __name__== "__main__":
	app.run(host="0.0.0.0", port=5000,debug=True)
