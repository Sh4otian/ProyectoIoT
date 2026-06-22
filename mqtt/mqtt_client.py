import paho.mqtt.client as mqtt
import socket
import os

# En Docker usa la variable de entorno MQTT_HOST (nombre del servicio).
# En local sigue funcionando con "localhost".
MQTT_HOST = os.environ.get("MQTT_HOST", "localhost")

cliente = mqtt.Client()

try:
    cliente.connect(MQTT_HOST, 1883, 60)
    mqtt_conectado = True
except:
    mqtt_conectado = False

def PublicarCat(categoria):
    cliente.publish("IoT/LED", categoria)

def EstadoMQTT():
    try:
        sock = socket.create_connection((MQTT_HOST, 1883), timeout=3)
        sock.close()
        return {"estado": "Conectado", "ip": MQTT_HOST, "puerto": 1883}
    except:
        return {"estado": "Desconectado", "ip": MQTT_HOST, "puerto": 1883}
