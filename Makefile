# ============================================
# Makefile para Sistema de Ruteo
# ============================================
# Uso: make [comando]
# Ejemplo: make up

.PHONY: help up down restart logs status build clean test ps exec shell

# Colores
BLUE := \033[0;34m
GREEN := \033[0;32m
RED := \033[0;31m
NC := \033[0m # No Color

# Variables
DOCKER_COMPOSE := docker compose
API_CONTAINER := ruteo-api
API_PORT := 8080

help: ## Mostrar ayuda
	@echo "$(BLUE)════════════════════════════════════════$(NC)"
	@echo "$(GREEN)  Sistema de Ruteo - Comandos Make$(NC)"
	@echo "$(BLUE)════════════════════════════════════════$(NC)"
	@echo ""
	@echo "Comandos disponibles:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  $(GREEN)%-15s$(NC) %s\n", $$1, $$2}'
	@echo ""

up: ## Levantar servicios
	@echo "$(BLUE)🚀 Iniciando servicios...$(NC)"
	@mkdir -p logs cache/osm
	@$(DOCKER_COMPOSE) up -d
	@echo "$(GREEN)✅ Servicios iniciados$(NC)"
	@echo ""
	@echo "📍 Servicios disponibles:"
	@echo "   - API:          http://localhost:$(API_PORT)"
	@echo "   - Docs:         http://localhost:$(API_PORT)/docs"
	@echo "   - Health:       http://localhost:$(API_PORT)/health"

down: ## Detener servicios
	@echo "$(BLUE)🛑 Deteniendo servicios...$(NC)"
	@$(DOCKER_COMPOSE) down
	@echo "$(GREEN)✅ Servicios detenidos$(NC)"

restart: ## Reiniciar servicios
	@echo "$(BLUE)🔄 Reiniciando servicios...$(NC)"
	@$(DOCKER_COMPOSE) restart
	@echo "$(GREEN)✅ Servicios reiniciados$(NC)"

logs: ## Ver logs en tiempo real
	@$(DOCKER_COMPOSE) logs -f

logs-api: ## Ver logs solo de la API
	@$(DOCKER_COMPOSE) logs -f $(API_CONTAINER)

status: ## Ver estado de servicios
	@echo "$(BLUE)📊 Estado de servicios:$(NC)"
	@$(DOCKER_COMPOSE) ps
	@echo ""
	@echo "$(BLUE)💾 Uso de recursos:$(NC)"
	@docker stats --no-stream $(API_CONTAINER) ruteo-redis || true

ps: ## Ver procesos
	@$(DOCKER_COMPOSE) ps

build: ## Reconstruir imágenes
	@echo "$(BLUE)🔨 Reconstruyendo imágenes...$(NC)"
	@$(DOCKER_COMPOSE) build --no-cache
	@echo "$(GREEN)✅ Imágenes reconstruidas$(NC)"

rebuild: build up ## Reconstruir e iniciar

clean: ## Limpiar contenedores y volúmenes
	@echo "$(RED)⚠️  Esto eliminará contenedores, volúmenes y caché$(NC)"
	@read -p "¿Continuar? (s/N): " confirm && [ "$$confirm" = "s" ] || exit 1
	@echo "$(BLUE)🧹 Limpiando...$(NC)"
	@$(DOCKER_COMPOSE) down -v
	@rm -rf cache/* logs/* || true
	@echo "$(GREEN)✅ Limpieza completada$(NC)"

test: ## Ejecutar tests básicos
	@echo "$(BLUE)🧪 Ejecutando tests...$(NC)"
	@echo ""
	@echo "1. Health Check..."
	@curl -sf http://localhost:$(API_PORT)/health > /dev/null && \
		echo "$(GREEN)   ✅ Health OK$(NC)" || \
		echo "$(RED)   ❌ Health falló$(NC)"
	@echo ""
	@echo "2. Geocoding Forward..."
	@curl -sf -X POST http://localhost:$(API_PORT)/api/v1/geocode \
		-H "Content-Type: application/json" \
		-d '{"address": "18 de Julio 1000, Montevideo"}' > /dev/null && \
		echo "$(GREEN)   ✅ Forward OK$(NC)" || \
		echo "$(RED)   ❌ Forward falló$(NC)"
	@echo ""
	@echo "3. Geocoding Reverse..."
	@curl -sf -X POST http://localhost:$(API_PORT)/api/v1/reverse-geocode \
		-H "Content-Type: application/json" \
		-d '{"lat": -34.9033, "lon": -56.1882}' > /dev/null && \
		echo "$(GREEN)   ✅ Reverse OK$(NC)" || \
		echo "$(RED)   ❌ Reverse falló$(NC)"
	@echo ""
	@echo "$(GREEN)✅ Tests completados$(NC)"

exec: ## Entrar al contenedor de la API
	@$(DOCKER_COMPOSE) exec $(API_CONTAINER) bash || \
		$(DOCKER_COMPOSE) exec $(API_CONTAINER) sh

shell: exec ## Alias de exec

health: ## Verificar health check
	@curl -s http://localhost:$(API_PORT)/health | jq . || \
		curl -s http://localhost:$(API_PORT)/health

dev: ## Modo desarrollo (logs en tiempo real)
	@$(DOCKER_COMPOSE) up

prod: ## Modo producción (background)
	@$(DOCKER_COMPOSE) up -d

pull: ## Actualizar imágenes base
	@$(DOCKER_COMPOSE) pull

backup: ## Backup de datos
	@echo "$(BLUE)💾 Creando backup...$(NC)"
	@mkdir -p backups
	@tar -czf backups/backup-$$(date +%Y%m%d-%H%M%S).tar.gz logs cache
	@echo "$(GREEN)✅ Backup creado en backups/$(NC)"

stats: ## Ver estadísticas de recursos
	@docker stats $(API_CONTAINER) ruteo-redis

top: ## Ver procesos dentro del contenedor
	@$(DOCKER_COMPOSE) top

version: ## Ver versiones
	@echo "$(BLUE)Versiones instaladas:$(NC)"
	@docker --version
	@$(DOCKER_COMPOSE) version
	@echo ""
	@$(DOCKER_COMPOSE) exec $(API_CONTAINER) python --version || true

prune: ## Limpiar recursos Docker no usados
	@echo "$(RED)⚠️  Esto limpiará imágenes, contenedores y redes no usadas$(NC)"
	@docker system prune -a --volumes

install: ## Primera instalación
	@echo "$(BLUE)📦 Instalando Sistema de Ruteo...$(NC)"
	@mkdir -p logs cache/osm
	@$(DOCKER_COMPOSE) build
	@$(DOCKER_COMPOSE) up -d
	@echo ""
	@echo "$(GREEN)✅ Instalación completada$(NC)"
	@echo ""
	@make test

update: ## Actualizar sistema
	@echo "$(BLUE)🔄 Actualizando sistema...$(NC)"
	@git pull
	@$(DOCKER_COMPOSE) down
	@$(DOCKER_COMPOSE) build
	@$(DOCKER_COMPOSE) up -d
	@echo "$(GREEN)✅ Sistema actualizado$(NC)"
