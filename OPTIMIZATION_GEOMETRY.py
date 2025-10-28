"""
OPTIMIZACIÓN APLICADA - Exclusión de campo geometry
====================================================

PROBLEMA:
---------
El endpoint /api/v1/zones-montevideo devolvía el campo 'geometry' completo
para zona_flete y zona_global, lo cual hace las respuestas MUY PESADAS:

- geometry de zona 0: 12,216 coordenadas = ~500 KB solo para un polígono
- geometry de zona 1: Similar o más grande
- Total por request: Podía ser >1 MB de JSON innecesario

SOLUCIÓN APLICADA:
------------------
Ahora el endpoint excluye el campo 'geometry' antes de devolver la respuesta.

Respuesta ANTES (pesada):
{
  "zona_flete": {
    "id": "9",
    "codigo": 0,
    "name": "Zona 0",
    "properties": {...},
    "geometry": {                    ← ❌ Miles de coordenadas
      "type": "MultiPolygon",
      "coordinates": [[[[...12,216 puntos...]]]]]
    }
  }
}

Respuesta AHORA (ligera):
{
  "zona_flete": {
    "id": "9",
    "codigo": 0,
    "name": "Zona 0",
    "properties": {
      "OBJECTID_1": 1,
      "OBJECTID": 9,
      "AREA": 70711160.4975,
      "Codigo": 0,
      "Shape_Area": 526603325.9262096
    }
  },                                 ← ✅ Sin geometry
  "zona_global": {
    "id": "86",
    "codigo": 22,
    "name": "Zona 22",
    "properties": {...}
  }                                  ← ✅ Sin geometry
}

BENEFICIOS:
-----------
✅ Respuestas 100-1000 veces más pequeñas (~1-5 KB en lugar de ~1 MB)
✅ Carga más rápida en el cliente
✅ Menos ancho de banda usado
✅ Mejor performance del API
✅ Mantiene toda la información útil (id, codigo, name, properties)

CAMBIOS EN EL CÓDIGO:
----------------------

1. app/main.py - Endpoint zones-montevideo (líneas ~1275-1285):
   
   # Remover campo geometry para respuesta más ligera
   zona_flete = zones_result.get('flete')
   zona_global = zones_result.get('global')
   
   if zona_flete and 'geometry' in zona_flete:
       zona_flete = {k: v for k, v in zona_flete.items() if k != 'geometry'}
   
   if zona_global and 'geometry' in zona_global:
       zona_global = {k: v for k, v in zona_global.items() if k != 'geometry'}

2. app/models.py - Documentación actualizada:
   
   class ZoneInfo(BaseModel):
       """
       Información detallada de una zona.
       
       Nota: El campo 'geometry' se excluye en los endpoints por defecto 
       para mantener las respuestas ligeras, ya que puede contener miles 
       de coordenadas de polígonos.
       """

COMMIT:
-------
✅ Commit e97b8a4 - "Optimize: Excluir campo geometry en respuestas de zones-montevideo"
✅ Push exitoso a GitHub

PRÓXIMO PASO:
-------------
En el servidor (después del auto-deploy o manual):

1. El webhook debería detectar el push automáticamente
2. Si los permisos están corregidos (chmod +x), auto-deploy se ejecutará
3. Si no, ejecutar manualmente:
   cd /home/riogas/ruteo
   git pull origin main
   docker compose restart

VERIFICACIÓN:
-------------
curl "https://tu-dominio/api/v1/zones-montevideo" \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{"coordinates": {"lat": -34.9149255, "lon": -56.1601851}}'

Debe retornar zona_flete y zona_global SIN el campo geometry.

"""

print(__doc__)
