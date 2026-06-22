#!/bin/bash
set -e

# Si la BD fue montada como volumen y está vacía, la inicializamos
if [ ! -f /app/BD/Franquicias.db ]; then
    echo "[IoT] Inicializando base de datos..."
    mkdir -p /app/BD
    cp /app/Franquicias.db.init /app/BD/Franquicias.db
fi

exec python main.py
