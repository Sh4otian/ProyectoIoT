import paho.mqtt.client as mqtt
import socket;

cliente = mqtt.Client()

try:
	cliente.connect("localhost",1883,60)
	mqtt_conectado = True
except:
	mqtt_conectado = False

def PublicarCat(categoria):
	cliente.publish("IoT/LED", categoria)

def EstadoMQTT():
	try:
		sock = socket.create_connection(("localhost",1883), timeout=3)
		sock.close()
		return {"estado":"Conectado", "ip":"localhost","puerto":1883}
	except:
		return {"estado":"Desconectado","ip":"localhost","puerto":1883}
