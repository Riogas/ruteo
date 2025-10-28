"""
Middleware de logging detallado para la API de Ruteo
Registra todos los requests y responses con metadata completa
"""

import json
import time
from datetime import datetime
from pathlib import Path
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
import logging


class DetailedRequestLogger(BaseHTTPMiddleware):
    """
    Middleware que registra información detallada de cada request/response
    """
    
    def __init__(
        self,
        app: ASGIApp,
        log_dir: str = "/app/logs/requests",
        max_body_length: int = 10000
    ):
        super().__init__(app)
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.max_body_length = max_body_length
        
        # Configurar logger específico para requests
        self.logger = self._setup_logger()
    
    def _setup_logger(self) -> logging.Logger:
        """Configura el logger con formato JSON"""
        logger = logging.getLogger("request_logger")
        logger.setLevel(logging.INFO)
        
        # Evitar duplicados
        if logger.handlers:
            return logger
        
        # Handler para archivo actual
        log_file = self.log_dir / "requests.log"
        handler = logging.FileHandler(log_file, encoding='utf-8')
        handler.setLevel(logging.INFO)
        
        # Formato: una línea JSON por request
        handler.setFormatter(logging.Formatter('%(message)s'))
        logger.addHandler(handler)
        
        return logger
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Intercepta cada request y registra información detallada
        """
        # Timestamp de inicio
        start_time = time.time()
        request_time = datetime.now()
        
        # Información del request
        request_info = {
            "timestamp": request_time.isoformat(),
            "method": request.method,
            "path": request.url.path,
            "query_params": dict(request.query_params),
            "client_ip": self._get_client_ip(request),
            "user_agent": request.headers.get("user-agent", "unknown"),
            "referer": request.headers.get("referer", None),
        }
        
        # Capturar body del request (si existe)
        body = None
        if request.method in ["POST", "PUT", "PATCH"]:
            try:
                body_bytes = await request.body()
                if body_bytes:
                    body_str = body_bytes.decode('utf-8')
                    # Truncar si es muy largo
                    if len(body_str) > self.max_body_length:
                        body_str = body_str[:self.max_body_length] + "... (truncated)"
                    try:
                        body = json.loads(body_str)
                    except json.JSONDecodeError:
                        body = body_str
                
                # Recrear el body para que la app lo pueda leer
                async def receive():
                    return {"type": "http.request", "body": body_bytes}
                request._receive = receive
                
            except Exception as e:
                body = f"Error reading body: {str(e)}"
        
        request_info["request_body"] = body
        
        # Ejecutar el request
        response = await call_next(request)
        
        # Tiempo de ejecución
        duration_ms = (time.time() - start_time) * 1000
        
        # Información del response
        response_info = {
            "status_code": response.status_code,
            "duration_ms": round(duration_ms, 2),
        }
        
        # Intentar capturar el body del response (solo para JSON)
        # Nota: No podemos leer el body aquí sin consumirlo, 
        # así que solo registramos metadata
        
        # Log completo
        log_entry = {
            **request_info,
            **response_info,
            "success": 200 <= response.status_code < 400
        }
        
        # Escribir log en formato JSON (una línea por request)
        self.logger.info(json.dumps(log_entry, ensure_ascii=False))
        
        return response
    
    def _get_client_ip(self, request: Request) -> str:
        """
        Obtiene la IP real del cliente (considerando proxies)
        """
        # Intentar obtener IP real de headers de proxy
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip
        
        # Fallback a IP directa
        if request.client:
            return request.client.host
        
        return "unknown"


class EndpointLogger:
    """
    Logger específico para endpoints individuales (para logs más detallados)
    """
    
    def __init__(self, endpoint_name: str, log_dir: str = "/app/logs/endpoints"):
        self.endpoint_name = endpoint_name
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.logger = self._setup_logger()
    
    def _setup_logger(self) -> logging.Logger:
        """Configura logger específico por endpoint"""
        logger = logging.getLogger(f"endpoint_{self.endpoint_name}")
        logger.setLevel(logging.INFO)
        
        if logger.handlers:
            return logger
        
        # Archivo específico por endpoint
        log_file = self.log_dir / f"{self.endpoint_name}.log"
        handler = logging.FileHandler(log_file, encoding='utf-8')
        handler.setLevel(logging.INFO)
        handler.setFormatter(logging.Formatter('%(message)s'))
        logger.addHandler(handler)
        
        return logger
    
    def log_execution(
        self,
        request_data: dict,
        response_data: dict,
        client_ip: str,
        duration_ms: float,
        success: bool = True,
        error: str = None
    ):
        """
        Registra una ejecución completa del endpoint
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "endpoint": self.endpoint_name,
            "client_ip": client_ip,
            "request": request_data,
            "response": response_data if success else None,
            "error": error,
            "duration_ms": round(duration_ms, 2),
            "success": success
        }
        
        self.logger.info(json.dumps(log_entry, ensure_ascii=False, indent=2))


def setup_logging(app):
    """
    Configura el sistema de logging completo en la app
    """
    # Agregar middleware de logging
    app.add_middleware(
        DetailedRequestLogger,
        log_dir="/app/logs/requests",
        max_body_length=10000
    )
