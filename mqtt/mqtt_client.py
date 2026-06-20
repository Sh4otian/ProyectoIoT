import paho.mqtt.client as mqtt

cliente = mqtt.Client()

cliente.connect("localhost",1883,60)

def PublicarCat(categoria):
	cliente.publish("IoT/LED", categoria)
