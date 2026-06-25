FROM python:3.11-slim

WORKDIR /app

# ── Dependencias del sistema ───────────────────────────────────────────────
# Pillow: libjpeg-dev, zlib1g-dev
# OpenCV headless: libglib2.0-0, libgl1
# Captura V4L2 (cámara USB/integrada): libv4l-dev, v4l-utils
RUN apt-get update && apt-get install -y --no-install-recommends \
    libjpeg-dev \
    zlib1g-dev \
    libglib2.0-0 \
    libgl1 \
    libv4l-dev \
    v4l-utils \
    && rm -rf /var/lib/apt/lists/*

# ── Copiar requirements antes del código (caché de capas) ─────────────────
COPY requerements.txt .

# ── 1) PyTorch CPU (índice especial de PyTorch) ───────────────────────────
RUN pip install --no-cache-dir \
    torch==2.12.1+cpu \
    torchvision==0.27.1+cpu \
    --index-url https://download.pytorch.org/whl/cpu

# ── 2) Resto de dependencias (sin torch/torchvision) ─────────────────────
RUN grep -vE "^torch" requerements.txt > requirements_base.txt && \
    pip install --no-cache-dir -r requirements_base.txt

# ── Copiar todo el proyecto ───────────────────────────────────────────────
COPY . .

# Guardar DB inicial fuera de la carpeta BD (para el entrypoint)
RUN cp BD/Franquicias.db /app/Franquicias.db.init

# Crear carpeta de uploads
RUN mkdir -p uploads

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 5000

ENTRYPOINT ["/entrypoint.sh"]
