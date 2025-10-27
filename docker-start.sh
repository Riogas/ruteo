#!/bin/bash
# ============================================
# Script de inicio rápido para Docker
# ============================================
# Uso: ./docker-start.sh [comando]
# Comandos: up, down, restart, logs, status

set -e

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Banner
echo -e "${BLUE}"
echo "╔════════════════════════════════════════╗"
echo "║   Sistema de Ruteo - Docker Manager   ║"
echo "╔════════════════════════════════════════╗"
echo -e "${NC}"

# Verificar que Docker está instalado
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker no está instalado${NC}"
    echo "Por favor instala Docker desde: https://docs.docker.com/get-docker/"
    exit 1
fi

if ! command -v docker compose &> /dev/null; then
    echo -e "${RED}❌ Docker Compose no está instalado${NC}"
    echo "Por favor instala Docker Compose desde: https://docs.docker.com/compose/install/"
    exit 1
fi

echo -e "${GREEN}✅ Docker y Docker Compose están instalados${NC}\n"

# Función para mostrar uso
show_usage() {
    echo "Uso: $0 [comando]"
    echo ""
    echo "Comandos disponibles:"
    echo "  up        - Levantar todos los servicios"
    echo "  down      - Detener todos los servicios"
    echo "  restart   - Reiniciar todos los servicios"
    echo "  logs      - Ver logs en tiempo real"
    echo "  status    - Ver estado de servicios"
    echo "  build     - Reconstruir imágenes"
    echo "  clean     - Limpiar contenedores y volúmenes"
    echo "  test      - Ejecutar tests básicos"
    echo ""
}

# Función para levantar servicios
start_services() {
    echo -e "${BLUE}🚀 Iniciando servicios...${NC}"
    
    # Crear directorios si no existen
    mkdir -p logs cache/osm
    
    # Levantar servicios
    docker compose up -d
    
    echo ""
    echo -e "${YELLOW}⏳ Esperando que los servicios estén listos...${NC}"
    sleep 10
    
    # Verificar health
    if docker compose ps | grep -q "healthy"; then
        echo -e "${GREEN}✅ Servicios iniciados correctamente${NC}"
        echo ""
        echo "📍 Servicios disponibles:"
        echo "   - API:          http://localhost:8080"
        echo "   - Documentación: http://localhost:8080/docs"
        echo "   - Health Check: http://localhost:8080/health"
        echo ""
        
        # Test básico
        echo -e "${BLUE}🧪 Probando API...${NC}"
        if curl -sf http://localhost:8080/health > /dev/null; then
            echo -e "${GREEN}✅ API respondiendo correctamente${NC}"
        else
            echo -e "${YELLOW}⚠️  API aún no responde, puede tardar un poco más${NC}"
        fi
    else
        echo -e "${YELLOW}⚠️  Servicios iniciados pero aún no están healthy${NC}"
        echo "Ejecuta 'docker compose logs -f' para ver el progreso"
    fi
}

# Función para detener servicios
stop_services() {
    echo -e "${BLUE}🛑 Deteniendo servicios...${NC}"
    docker compose down
    echo -e "${GREEN}✅ Servicios detenidos${NC}"
}

# Función para reiniciar servicios
restart_services() {
    echo -e "${BLUE}🔄 Reiniciando servicios...${NC}"
    docker compose restart
    echo -e "${GREEN}✅ Servicios reiniciados${NC}"
}

# Función para ver logs
show_logs() {
    echo -e "${BLUE}📋 Mostrando logs (Ctrl+C para salir)...${NC}"
    docker compose logs -f
}

# Función para ver status
show_status() {
    echo -e "${BLUE}📊 Estado de servicios:${NC}\n"
    docker compose ps
    echo ""
    echo -e "${BLUE}💾 Uso de recursos:${NC}"
    docker stats --no-stream ruteo-api ruteo-redis
}

# Función para rebuild
rebuild_services() {
    echo -e "${BLUE}🔨 Reconstruyendo imágenes...${NC}"
    docker compose build --no-cache
    echo -e "${GREEN}✅ Imágenes reconstruidas${NC}"
    echo ""
    echo "Ejecuta './docker-start.sh up' para iniciar con las nuevas imágenes"
}

# Función para limpiar
clean_all() {
    echo -e "${RED}⚠️  ADVERTENCIA: Esto eliminará contenedores, volúmenes y caché${NC}"
    read -p "¿Estás seguro? (s/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Ss]$ ]]; then
        echo -e "${BLUE}🧹 Limpiando...${NC}"
        docker compose down -v
        rm -rf cache/* logs/*
        echo -e "${GREEN}✅ Limpieza completada${NC}"
    else
        echo "Limpieza cancelada"
    fi
}

# Función para tests
run_tests() {
    echo -e "${BLUE}🧪 Ejecutando tests básicos...${NC}\n"
    
    # Health check
    echo "1. Health Check..."
    if curl -sf http://localhost:8080/health > /dev/null; then
        echo -e "${GREEN}   ✅ Health check OK${NC}"
    else
        echo -e "${RED}   ❌ Health check falló${NC}"
        exit 1
    fi
    
    # Geocoding forward
    echo "2. Geocoding Forward..."
    RESPONSE=$(curl -sf -X POST http://localhost:8080/api/v1/geocode \
        -H "Content-Type: application/json" \
        -d '{"address": "18 de Julio 1000, Montevideo"}' || echo "error")
    
    if [[ "$RESPONSE" != "error" ]]; then
        echo -e "${GREEN}   ✅ Geocoding forward OK${NC}"
    else
        echo -e "${RED}   ❌ Geocoding forward falló${NC}"
    fi
    
    # Geocoding reverse
    echo "3. Geocoding Reverse..."
    RESPONSE=$(curl -sf -X POST http://localhost:8080/api/v1/reverse-geocode \
        -H "Content-Type: application/json" \
        -d '{"lat": -34.9033, "lon": -56.1882}' || echo "error")
    
    if [[ "$RESPONSE" != "error" ]]; then
        echo -e "${GREEN}   ✅ Geocoding reverse OK${NC}"
    else
        echo -e "${RED}   ❌ Geocoding reverse falló${NC}"
    fi
    
    echo ""
    echo -e "${GREEN}✅ Tests completados${NC}"
}

# Procesar comando
COMMAND=${1:-up}

case $COMMAND in
    up|start)
        start_services
        ;;
    down|stop)
        stop_services
        ;;
    restart)
        restart_services
        ;;
    logs)
        show_logs
        ;;
    status|ps)
        show_status
        ;;
    build)
        rebuild_services
        ;;
    clean)
        clean_all
        ;;
    test)
        run_tests
        ;;
    help|--help|-h)
        show_usage
        ;;
    *)
        echo -e "${RED}❌ Comando desconocido: $COMMAND${NC}\n"
        show_usage
        exit 1
        ;;
esac

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}Para más información: ./docker-start.sh help${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
