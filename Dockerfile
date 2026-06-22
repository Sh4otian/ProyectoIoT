FROM python:3.11-slim

WORKDIR /app

# Dependencias del sistema para Pillow
RUN apt-get update && apt-get install -y \
    libjpeg-dev \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements antes del código (aprovecha la caché de capas)
COPY requerements.txt .

# 1) Instalar PyTorch CPU (índice especial de PyTorch)
RUN pip install --no-cache-dir \
    torch==2.12.1+cpu \
    torchvision==0.27.1+cpu \
    --index-url https://download.pytorch.org/whl/cpu

# 2) Instalar el resto de dependencias (excluyendo torch/torchvision)
RUN grep -vE "^torch" requerements.txt > requirements_base.txt && \
    pip install --no-cache-dir -r requirements_base.txt

# Copiar todo el proyecto
COPY . .

# Guardar DB inicial fuera de la carpeta BD (para el entrypoint)
RUN cp BD/Franquicias.db /app/Franquicias.db.init

# Crear carpeta de uploads
RUN mkdir -p uploads

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 5000

ENTRYPOINT ["/entrypoint.sh"]
