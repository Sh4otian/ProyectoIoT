from flask import Flask, render_template, request, Response, jsonify
from BD.db import ConsultaTot, GuardarRes, EstadoDB
from ModelIA.PruebaIA import clasificar_img
from mqtt.mqtt_client import PublicarCat, EstadoMQTT

import os
import time
import threading
import numpy as np
import cv2

# ─── Clase de cámara thread-safe ─────────────────────────────────────────────

class CamaraIoT:
    def __init__(self, indice: int = 0):
        self._lock = threading.Lock()
        self.cap = cv2.VideoCapture(indice)

    def disponible(self) -> bool:
        return self.cap.isOpened()

    def capturar(self):
        """Devuelve un frame BGR o None si la cámara no está disponible."""
        if not self.disponible():
            return None
        with self._lock:
            ok, frame = self.cap.read()
            return frame if ok else None

    def _frame_placeholder(self) -> bytes:
        """Frame negro con mensaje cuando no hay cámara conectada."""
        img = np.zeros((480, 640, 3), dtype=np.uint8)
        cv2.putText(img, "Camara no disponible",
                    (80, 230), cv2.FONT_HERSHEY_SIMPLEX,
                    1, (80, 80, 255), 2, cv2.LINE_AA)
        cv2.putText(img, "Revisa /dev/video0 en docker-compose",
                    (30, 275), cv2.FONT_HERSHEY_SIMPLEX,
                    0.55, (160, 160, 160), 1, cv2.LINE_AA)
        _, buf = cv2.imencode(".jpg", img)
        return buf.tobytes()

    def gen_frames(self):
        """Generador MJPEG para streaming continuo al navegador."""
        while True:
            frame = self.capturar()
            if frame is not None:
                _, buf = cv2.imencode(".jpg", frame)
                data = buf.tobytes()
                delay = 0.04   # ~25 FPS con cámara
            else:
                data = self._frame_placeholder()
                delay = 1.0    # Placeholder cada 1 s para ahorrar CPU

            yield (b"--frame\r\n"
                   b"Content-Type: image/jpeg\r\n\r\n"
                   + data
                   + b"\r\n")
            time.sleep(delay)

    def liberar(self):
        self.cap.release()


# Instancia global (se inicializa al arrancar el servidor)
camara = CamaraIoT()

# ─── Estado del sistema ───────────────────────────────────────────────────────

def SysEdo():
    mqtt = EstadoMQTT()
    cam_estado = "ACTIVA" if camara.disponible() else "SIN CÁMARA"
    return {
        "mqtt":   mqtt,
        "BD":     EstadoDB(),
        "Camara": {"Estado": cam_estado},
        "Flask":  "ACTIVO",
    }

# ─── App Flask ────────────────────────────────────────────────────────────────

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ── Páginas ─────────────────────────────────────────────────────────────────

@app.route("/")
def Inicio():
    return render_template("index.html")

@app.route("/EstadoSis")
def configuracion():
    estado = SysEdo()
    return render_template("EstadoSis.html", estado=estado)

@app.route("/historial")
def historial():
    datos = ConsultaTot()
    return render_template("historial.html", Dat=datos)

# ── Stream de cámara en vivo ─────────────────────────────────────────────────

@app.route("/video_feed")
def video_feed():
    return Response(
        camara.gen_frames(),
        mimetype="multipart/x-mixed-replace; boundary=frame",
    )

# ── Capturar frame y clasificar con IA ──────────────────────────────────────

@app.route("/capturar", methods=["POST"])
def capturar():
    frame = camara.capturar()
    if frame is None:
        return jsonify({"error": "Cámara no disponible o sin señal"}), 503

    ruta = os.path.join(UPLOAD_FOLDER, "captura_camara.jpg")
    cv2.imwrite(ruta, frame)

    categoria, confianza = clasificar_img(ruta)
    PublicarCat(categoria)
    GuardarRes(ruta, categoria, confianza)

    return jsonify({"categoria": categoria, "confianza": round(confianza, 2)})

# ── Subida manual de imagen (mantiene funcionalidad original) ────────────────

@app.route("/simular", methods=["POST"])
def simular():
    if "imagen" not in request.files:
        return "No se recibió ninguna imagen", 400

    archivo = request.files["imagen"]
    if archivo.filename == "":
        return "No se seleccionó archivo", 400

    ruta = os.path.join(UPLOAD_FOLDER, archivo.filename)
    archivo.save(ruta)

    categoria, confianza = clasificar_img(ruta)
    PublicarCat(categoria)
    GuardarRes(ruta, categoria, confianza)

    return f"""
        <b>Clasificación realizada</b><br><br>
        Archivo: {archivo.filename}<br>
        Categoría: {categoria}<br>
        Confianza: {confianza:.2f}%<br>
        <br><a href="/">← Volver</a>
    """

if __name__ == "__main__":
    # threaded=True (defecto) permite el stream MJPEG y peticiones simultáneas
    # use_reloader=False evita que el proceso se duplique y libere la cámara
    app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False)
