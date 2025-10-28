#!/bin/bash

# ============================================
# Script de Auto-Deploy para Ruteo API
# ============================================

# Configuración
REPO_DIR="/home/riogas/ruteo"
LOG_FILE="/home/riogas/ruteo/deploy.log"
BRANCH="main"

# Función de logging
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log "=========================================="
log "🚀 Iniciando auto-deploy..."
log "=========================================="

# Ir al directorio del proyecto
cd "$REPO_DIR" || exit 1

# Guardar el commit actual
OLD_COMMIT=$(git rev-parse HEAD)
log "📌 Commit actual: $OLD_COMMIT"

# Hacer pull de los cambios
log "📥 Descargando cambios desde GitHub..."
git fetch origin "$BRANCH"
git reset --hard "origin/$BRANCH"

# Verificar si hubo cambios
NEW_COMMIT=$(git rev-parse HEAD)
log "📌 Nuevo commit: $NEW_COMMIT"

if [ "$OLD_COMMIT" = "$NEW_COMMIT" ]; then
    log "✅ No hay cambios nuevos. Deploy cancelado."
    exit 0
fi

log "🔄 Cambios detectados. Iniciando redeploy..."

# Rotar logs antes del deploy
log "📋 Rotando logs antiguos..."
bash "$REPO_DIR/app/rotate-logs.sh"

# Detener contenedores
log "🛑 Deteniendo contenedores..."
docker compose down

# Reconstruir imagen
log "🏗️  Reconstruyendo imagen Docker..."
docker compose build --no-cache

# Iniciar contenedores
log "▶️  Iniciando contenedores..."
docker compose up -d

# Esperar 10 segundos
sleep 10

# Verificar salud de la API
log "🏥 Verificando salud de la API..."
if curl -f http://localhost:8080/health > /dev/null 2>&1; then
    log "✅ Deploy exitoso. API funcionando correctamente."
else
    log "❌ Error: API no responde en /health"
    exit 1
fi

# Limpiar imágenes viejas
log "🧹 Limpiando imágenes antiguas..."
docker image prune -f

log "=========================================="
log "🎉 Auto-deploy completado exitosamente"
log "=========================================="