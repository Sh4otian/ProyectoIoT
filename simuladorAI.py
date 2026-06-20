from BD.db import GuardarRes
from mqtt.mqtt_client import PublicarCat
import random 

def Simulador():
	categorias =["Pokemon","Naruto","Dragon Ball", "Bleach"]

	resultado = random.choice(categorias)

	confianza = round(random.uniform(50,99),2)
	
	print(resultado)
	print(confianza)
	GuardarRes(resultado,confianza)
	PublicarCat(resultado)
	print("Guardado")
