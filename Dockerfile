# ============================================
# Multi-stage Docker build para optimizar tamaño
# ============================================

# Stage 1: Builder
FROM python:3.11-slim as builder

# Variables de entorno para build
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Instalar dependencias de compilación
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libspatialindex-dev \
    libgeos-dev \
    libproj-dev \
    && rm -rf /var/lib/apt/lists/*

# Crear directorio de trabajo
WORKDIR /app

# Copiar y instalar dependencias de Python
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Stage 2: Runtime
FROM python:3.11-slim

# Metadatos
LABEL maintainer="Riogas"
LABEL description="Sistema de Ruteo con Geocodificación y Detección de Esquinas"
LABEL version="1.0.0"

# Variables de entorno
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH=/root/.local/bin:$PATH \
    TZ=America/Montevideo

# Instalar dependencias runtime necesarias
RUN apt-get update && apt-get install -y \
    libspatialindex-c6 \
    libgeos-c1v5 \
    libproj25 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Crear usuario no-root para seguridad
RUN useradd -m -u 1000 ruteo && \
    mkdir -p /app/logs /app/cache/osm && \
    chown -R ruteo:ruteo /app

# Cambiar a usuario no-root
USER ruteo

# Directorio de trabajo
WORKDIR /app

# Copiar dependencias de Python desde builder
COPY --from=builder --chown=ruteo:ruteo /root/.local /home/ruteo/.local

# Copiar código de la aplicación
COPY --chown=ruteo:ruteo . .

# Exponer puerto
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Comando para ejecutar la aplicación
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
