"""
Test simple para ver qué devuelve intersection() con MultiLineString
"""

from shapely.geometry import LineString, Point
from shapely.ops import unary_union

# Crear dos segmentos de "Río Negro"
segment1 = LineString([(-56.194, -34.906), (-56.193, -34.906)])
segment2 = LineString([(-56.193, -34.906), (-56.192, -34.906)])

# Combinar con unary_union
rio_negro_combined = unary_union([segment1, segment2])

print(f"Tipo combinado: {type(rio_negro_combined).__name__}")
print(f"Contenido: {rio_negro_combined}")

# Crear 18 de Julio que cruza Río Negro
av_18_julio = LineString([(-56.195, -34.905), (-56.195, -34.907)])

# Calcular intersección
intersection = av_18_julio.intersection(rio_negro_combined)

print(f"\nTipo intersección: {type(intersection).__name__}")
print(f"Contenido: {intersection}")
print(f"¿Está vacío?: {intersection.is_empty}")

# Extraer puntos
points = []
if isinstance(intersection, Point):
    points = [intersection]
    print(f"\nEs un Point: {intersection}")
elif hasattr(intersection, 'geoms'):
    points = [p for p in intersection.geoms if isinstance(p, Point)]
    print(f"\nTiene geoms: {len(points)} puntos")
    for i, p in enumerate(points, 1):
        print(f"  Punto {i}: {p}")

print(f"\n✅ Total puntos extraídos: {len(points)}")
