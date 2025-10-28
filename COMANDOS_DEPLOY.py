"""
COMANDOS PARA APLICAR LOS CAMBIOS EN EL SERVIDOR
=================================================

El servidor ya tiene los archivos actualizados (git pull exitoso),
pero necesitas REINICIAR los contenedores de Docker para que la aplicación
cargue los archivos GeoJSON corregidos.

EJECUTA ESTOS COMANDOS EN EL SERVIDOR (vía SSH):
-------------------------------------------------

1. Reiniciar los contenedores:
   
   cd /home/riogas/ruteo
   docker compose down
   docker compose up -d --build

   O más rápido (sin rebuild si no cambiaste Dockerfile):
   
   docker compose restart

2. Verificar que los contenedores están corriendo:
   
   docker compose ps

3. Ver los logs para confirmar que cargó correctamente:
   
   docker compose logs -f --tail=100

   Deberías ver mensajes como:
   "Cargando zonas de flete desde app/data/ZONAS_F.geojson"
   "11 zonas de flete cargadas"

4. Probar el endpoint:
   
   curl "http://localhost:8000/zones?lat=-34.9149255&lon=-56.1601851"

   Debería retornar zona_flete con codigo: 0

IMPORTANTE:
-----------
El problema es que Python/FastAPI ya cargó los archivos GeoJSON en memoria
cuando inició el contenedor. Un simple "git pull" NO es suficiente - necesitas
REINICIAR la aplicación para que recargue los archivos.

"""

print(__doc__)
