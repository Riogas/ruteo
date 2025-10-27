#!/usr/bin/env python3
"""
Script para iniciar el servidor de ruteo
Ejecutar: python start_server.py
"""
import uvicorn
import sys
import os

def main():
    """Iniciar el servidor FastAPI"""
    
    # Verificar que estemos en el directorio correcto
    if not os.path.exists("app/main.py"):
        print("❌ Error: No se encuentra app/main.py")
        print("   Ejecuta este script desde el directorio raíz del proyecto")
        sys.exit(1)
    
    # Verificar que existe .env
    if not os.path.exists(".env"):
        print("⚠️  Advertencia: No se encuentra .env")
        print("   Se usará la configuración por defecto")
    
    print("=" * 60)
    print("🚚 SISTEMA DE RUTEO INTELIGENTE")
    print("=" * 60)
    print()
    print("Iniciando servidor...")
    print("📍 URL: http://localhost:8080")
    print("📖 Documentación: http://localhost:8080/docs")
    print()
    print("Presiona Ctrl+C para detener el servidor")
    print("=" * 60)
    print()
    
    try:
        uvicorn.run(
            "app.main:app",
            host="0.0.0.0",
            port=8080,
            reload=True,  # Recarga automática al cambiar código
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n\n👋 Servidor detenido")
    except Exception as e:
        print(f"\n❌ Error al iniciar servidor: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
