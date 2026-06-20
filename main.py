from flask import Flask,render_template
from BD.db import ConsultaTot
from simuladorAI import Simulador

app = Flask(__name__)

@app.route("/")
def Inicio():
	return render_template("index.html")

@app.route("/configuracion")
def configuracion():
	return render_template("configuracion.html")

@app.route("/historial")
def historial():
	datos = ConsultaTot()

	return render_template("historial.html",Dat=datos)

@app.route("/estadisticas")
def estadisticas():
	return render_template("Estadisticas.html")

@app.route("/simular")
def simular():
	Simulador()
	return "Simulacion realizada"

if __name__== "__main__":
	app.run(host="0.0.0.0", port=5000,debug=True)
