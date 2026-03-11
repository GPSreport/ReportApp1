#!/usr/bin/env python3
"""
Script para probar el procesamiento de fechas de eventos
"""
import json
from datetime import datetime
from zoneinfo import ZoneInfo

# Simular datos que llegarían desde la app
test_data = {
    "latitud": 4.7110,
    "longitud": -74.0721,
    "timestamp": "2025-12-04T15:30:00.000",
    "foto_base64": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO2dZb8AAAAASUVORK5CYII=",
    "descripcion": "Evento de prueba",
    "tipo_reporte": "Eventos Culturales",
    "fecha_inicio_evento": "2025-12-10T10:00:00.000",
    "fecha_fin_evento": "2025-12-10T18:00:00.000"
}

print("=" * 60)
print("PRUEBA DE PROCESAMIENTO DE FECHAS DE EVENTOS")
print("=" * 60)

print("\n📥 Datos recibidos (simulados desde app):")
print(json.dumps(test_data, indent=2, ensure_ascii=False))

print("\n🔍 Analizando fechas de eventos...")

# Procesar fecha_inicio_evento
if test_data.get('fecha_inicio_evento'):
    try:
        fecha_inicio_str = test_data['fecha_inicio_evento']
        print(f"\n✓ fecha_inicio_evento recibida: {fecha_inicio_str}")
        
        fecha_inicio_dt = datetime.fromisoformat(fecha_inicio_str.replace('Z', '+00:00'))
        print(f"  - Parseada: {fecha_inicio_dt}")
        print(f"  - Tiene timezone: {fecha_inicio_dt.tzinfo is not None}")
        
        if fecha_inicio_dt.tzinfo is not None:
            fecha_inicio = fecha_inicio_dt.astimezone(ZoneInfo("America/Bogota")).replace(tzinfo=None)
            print(f"  - Convertida a Bogotá: {fecha_inicio}")
        else:
            fecha_inicio = fecha_inicio_dt
            print(f"  - Sin timezone, usando directamente: {fecha_inicio}")
        
        print(f"  ✅ Valor a guardar en MySQL: {fecha_inicio}")
        
    except Exception as e:
        print(f"  ❌ Error procesando fecha_inicio_evento: {e}")
        fecha_inicio = None
else:
    print("\n⚠️  fecha_inicio_evento NO fue enviada")
    fecha_inicio = None

# Procesar fecha_fin_evento
if test_data.get('fecha_fin_evento'):
    try:
        fecha_fin_str = test_data['fecha_fin_evento']
        print(f"\n✓ fecha_fin_evento recibida: {fecha_fin_str}")
        
        fecha_fin_dt = datetime.fromisoformat(fecha_fin_str.replace('Z', '+00:00'))
        print(f"  - Parseada: {fecha_fin_dt}")
        print(f"  - Tiene timezone: {fecha_fin_dt.tzinfo is not None}")
        
        if fecha_fin_dt.tzinfo is not None:
            fecha_fin = fecha_fin_dt.astimezone(ZoneInfo("America/Bogota")).replace(tzinfo=None)
            print(f"  - Convertida a Bogotá: {fecha_fin}")
        else:
            fecha_fin = fecha_fin_dt
            print(f"  - Sin timezone, usando directamente: {fecha_fin}")
        
        print(f"  ✅ Valor a guardar en MySQL: {fecha_fin}")
        
    except Exception as e:
        print(f"  ❌ Error procesando fecha_fin_evento: {e}")
        fecha_fin = None
else:
    print("\n⚠️  fecha_fin_evento NO fue enviada")
    fecha_fin = None

print("\n" + "=" * 60)
print("RESULTADO DEL PROCESAMIENTO")
print("=" * 60)
print(f"Tipo de reporte: {test_data['tipo_reporte']}")
print(f"Fecha inicio a guardar: {fecha_inicio}")
print(f"Fecha fin a guardar: {fecha_fin}")

if fecha_inicio is None or fecha_fin is None:
    print("\n⚠️  ADVERTENCIA: Una o ambas fechas son NULL")
    print("   Esto causará que las columnas en MySQL estén vacías")
else:
    print("\n✅ Ambas fechas tienen valores válidos")

print("\n💡 Consulta SQL que se ejecutaría:")
sql = """
INSERT INTO reportes (latitud, longitud, timestamp, foto_base64, descripcion, tipo_reporte, fecha_inicio_evento, fecha_fin_evento)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
"""
print(sql)
print(f"Valores: ({test_data['latitud']}, {test_data['longitud']}, ..., '{test_data['tipo_reporte']}', {fecha_inicio}, {fecha_fin})")
