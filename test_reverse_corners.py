#!/usr/bin/env python3
"""
Script de prueba para reverse geocoding con esquinas.

Prueba el endpoint de reverse geocoding para verificar que:
1. Devuelve calle y número de puerta
2. Devuelve las 2 esquinas más cercanas
3. Funciona con diferentes coordenadas de Montevideo
"""

import requests
import json

BASE_URL = "http://localhost:8080/api/v1"

def test_reverse_with_corners():
    """Prueba reverse geocoding con coordenadas de Montevideo"""
    print("=" * 70)
    print("  TEST: REVERSE GEOCODING CON ESQUINAS")
    print("=" * 70)
    print()
    
    # Coordenadas de prueba en Montevideo (cruces importantes)
    test_locations = [
        {
            "name": "18 de Julio y Ejido",
            "lat": -34.9055,
            "lon": -56.1889
        },
        {
            "name": "Av. Italia y Bvar. Artigas",
            "lat": -34.8920,
            "lon": -56.1580
        },
        {
            "name": "Colón y Rivera",
            "lat": -34.8980,
            "lon": -56.1750
        },
        {
            "name": "Mercedes y Convención",
            "lat": -34.9010,
            "lon": -56.1820
        }
    ]
    
    for i, location in enumerate(test_locations, 1):
        print(f"{i}. 📍 {location['name']}")
        print(f"   Coordenadas: ({location['lat']:.6f}, {location['lon']:.6f})")
        print()
        
        try:
            coords = {
                "lat": location["lat"],
                "lon": location["lon"],
                "address": "Montevideo, Uruguay"
            }
            
            response = requests.post(
                f"{BASE_URL}/reverse-geocode",
                json=coords,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                address = response.json()
                
                print("   ✅ REVERSE GEOCODING EXITOSO!")
                print()
                print(f"   📋 Resultado:")
                print(f"      Calle:          {address.get('street', 'N/A')}")
                print(f"      Ciudad:         {address.get('city', 'N/A')}")
                print(f"      País:           {address.get('country', 'N/A')}")
                
                # ESQUINAS (NUEVO)
                corner_1 = address.get('corner_1')
                corner_2 = address.get('corner_2')
                
                if corner_1 or corner_2:
                    print()
                    print(f"   🔀 ESQUINAS DETECTADAS:")
                    if corner_1:
                        print(f"      Esquina 1:      {corner_1}")
                    if corner_2:
                        print(f"      Esquina 2:      {corner_2}")
                    
                    # Formato tipo Montevideo
                    if corner_1 and corner_2:
                        street_name = address.get('street', '').split()[0] if address.get('street') else ''
                        print()
                        print(f"   📝 Formato MVD:    {street_name} entre {corner_1} y {corner_2}")
                else:
                    print()
                    print(f"   ⚠️  No se detectaron esquinas cercanas")
                
                print()
                print(f"   📍 Dirección completa:")
                print(f"      {address.get('full_address', 'N/A')}")
                
            else:
                print(f"   ❌ Error {response.status_code}: {response.text}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        print()
        print("-" * 70)
        print()


def test_corner_detection_quality():
    """Prueba calidad de detección de esquinas"""
    print()
    print("=" * 70)
    print("  TEST: CALIDAD DE DETECCIÓN DE ESQUINAS")
    print("=" * 70)
    print()
    
    # Coordenada conocida: 18 de Julio esquina Ejido
    coords = {
        "lat": -34.9055,
        "lon": -56.1889
    }
    
    print(f"📍 Ubicación de prueba: Esquina conocida (18 de Julio y Ejido)")
    print(f"   Coordenadas: ({coords['lat']}, {coords['lon']})")
    print()
    
    try:
        response = requests.post(
            f"{BASE_URL}/reverse-geocode",
            json=coords,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            address = response.json()
            
            street = address.get('street', '')
            corner_1 = address.get('corner_1')
            corner_2 = address.get('corner_2')
            
            print("✅ Respuesta recibida")
            print()
            
            # Evaluar calidad
            quality_score = 0
            
            if street:
                print("✓ Calle principal detectada")
                quality_score += 1
            
            if corner_1:
                print("✓ Primera esquina detectada")
                quality_score += 1
            
            if corner_2:
                print("✓ Segunda esquina detectada")
                quality_score += 1
            
            print()
            print(f"📊 Calidad de detección: {quality_score}/3")
            
            if quality_score == 3:
                print("   🌟 EXCELENTE - Todas las esquinas detectadas")
            elif quality_score == 2:
                print("   ✓ BUENO - Calle y 1 esquina detectadas")
            elif quality_score == 1:
                print("   ⚠️  REGULAR - Solo calle detectada")
            else:
                print("   ❌ MALO - No se detectó información")
            
            print()
            print("📝 Resultado:")
            if corner_1 and corner_2:
                print(f"   {street} entre {corner_1} y {corner_2}")
            elif corner_1:
                print(f"   {street} esquina {corner_1}")
            else:
                print(f"   {street}")
            
        else:
            print(f"❌ Error {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")


def main():
    """Ejecuta todas las pruebas"""
    print()
    print("🧪 PRUEBAS DE REVERSE GEOCODING CON ESQUINAS")
    print()
    
    # Verificar servidor
    try:
        response = requests.get("http://localhost:8080/health", timeout=2)
        if response.status_code != 200:
            print("❌ Servidor no disponible en http://localhost:8080")
            return
    except Exception:
        print("❌ Servidor no disponible en http://localhost:8080")
        return
    
    print("✅ Servidor activo")
    print()
    
    # Test 1: Múltiples ubicaciones
    test_reverse_with_corners()
    
    # Test 2: Calidad de detección
    test_corner_detection_quality()
    
    print()
    print("=" * 70)
    print("  ✅ TODAS LAS PRUEBAS COMPLETADAS")
    print("=" * 70)
    print()
    print("💡 Tip: Revisa los logs del servidor para ver más detalles")
    print()


if __name__ == "__main__":
    main()
