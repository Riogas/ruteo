#!/bin/bash

# ============================================
# Script de Rotación de Logs
# Se ejecuta ANTES de cada deploy para archivar logs
# ============================================

LOG_BASE="/home/riogas/ruteo/logs"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

echo "🔄 Rotando logs antes del deploy..."

# Función para rotar un archivo de log
rotate_log() {
    local log_file=$1
    local log_dir=$(dirname "$log_file")
    local log_name=$(basename "$log_file" .log)
    
    if [ -f "$log_file" ]; then
        local new_name="${log_dir}/${log_name}_${TIMESTAMP}.log"
        mv "$log_file" "$new_name"
        echo "  ✅ Rotado: $(basename $log_file) → $(basename $new_name)"
        
        # Comprimir logs antiguos (más de 1 día)
        gzip "$new_name" 2>/dev/null || true
        if [ -f "${new_name}.gz" ]; then
            echo "  📦 Comprimido: $(basename $new_name).gz"
        fi
    fi
}

# Rotar log principal de deployment
if [ -f "${LOG_BASE}/deploy.log" ]; then
    rotate_log "${LOG_BASE}/deploy.log"
fi

# Rotar logs de requests
if [ -d "${LOG_BASE}/requests" ]; then
    for log_file in ${LOG_BASE}/requests/*.log; do
        [ -f "$log_file" ] && rotate_log "$log_file"
    done
fi

# Rotar logs de endpoints
if [ -d "${LOG_BASE}/endpoints" ]; then
    for log_file in ${LOG_BASE}/endpoints/*.log; do
        [ -f "$log_file" ] && rotate_log "$log_file"
    done
fi

# Rotar log de API (FastAPI)
if [ -f "${LOG_BASE}/api.log" ]; then
    rotate_log "${LOG_BASE}/api.log"
fi

# Limpiar logs muy antiguos (más de 30 días)
echo "🧹 Limpiando logs antiguos (>30 días)..."
find "$LOG_BASE" -name "*.log.gz" -type f -mtime +30 -delete 2>/dev/null || true
find "$LOG_BASE" -name "*.log" -type f -mtime +30 -delete 2>/dev/null || true

echo "✅ Rotación de logs completada"
