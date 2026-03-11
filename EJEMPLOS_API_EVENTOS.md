# 📡 Ejemplos de API - Eventos con Fechas

## 🎯 Crear Reporte de Evento Cultural

### Request
```bash
curl -X POST http://3.148.29.34/reportes/ \
  -H "Content-Type: application/json" \
  -d '{
    "latitud": 10.9639,
    "longitud": -74.7964,
    "tipo_reporte": "Eventos Culturales",
    "descripcion": "Festival de Música Vallenata 2025",
    "foto_base64": "",
    "fecha_inicio_evento": "2025-12-15T18:00:00",
    "fecha_fin_evento": "2025-12-15T23:30:00"
  }'
```

### Response (200 OK)
```json
{
  "id": 1,
  "latitud": 10.9639,
  "longitud": -74.7964,
  "timestamp": "2025-12-04T10:30:00",
  "foto_base64": "imagenes_reportes/1.jpg",
  "descripcion": "Festival de Música Vallenata 2025",
  "tipo_reporte": "Eventos Culturales",
  "fecha_inicio_evento": "2025-12-15T18:00:00",
  "fecha_fin_evento": "2025-12-15T23:30:00"
}
```

## ⚽ Crear Reporte de Evento Deportivo

### Request
```bash
curl -X POST http://3.148.29.34/reportes/ \
  -H "Content-Type: application/json" \
  -d '{
    "latitud": 10.9850,
    "longitud": -74.8100,
    "tipo_reporte": "Eventos Deportivos",
    "descripcion": "Torneo de Fútbol Inter-Universidades",
    "foto_base64": "",
    "fecha_inicio_evento": "2025-12-20T08:00:00",
    "fecha_fin_evento": "2025-12-20T17:00:00"
  }'
```

### Response (200 OK)
```json
{
  "id": 2,
  "latitud": 10.9850,
  "longitud": -74.8100,
  "timestamp": "2025-12-04T10:35:00",
  "foto_base64": "imagenes_reportes/2.jpg",
  "descripcion": "Torneo de Fútbol Inter-Universidades",
  "tipo_reporte": "Eventos Deportivos",
  "fecha_inicio_evento": "2025-12-20T08:00:00",
  "fecha_fin_evento": "2025-12-20T17:00:00"
}
```

## 🏗️ Crear Reporte Sin Fechas (Otros Tipos)

### Request
```bash
curl -X POST http://3.148.29.34/reportes/ \
  -H "Content-Type: application/json" \
  -d '{
    "latitud": 10.9700,
    "longitud": -74.7850,
    "tipo_reporte": "Obras en Proceso",
    "descripcion": "Reparación de vía principal",
    "foto_base64": ""
  }'
```

### Response (200 OK)
```json
{
  "id": 3,
  "latitud": 10.9700,
  "longitud": -74.7850,
  "timestamp": "2025-12-04T10:40:00",
  "foto_base64": "imagenes_reportes/3.jpg",
  "descripcion": "Reparación de vía principal",
  "tipo_reporte": "Obras en Proceso",
  "fecha_inicio_evento": null,
  "fecha_fin_evento": null
}
```

## 📋 Obtener Todos los Reportes

### Request
```bash
curl http://3.148.29.34/reportes/
```

### Response (200 OK)
```json
[
  {
    "id": 3,
    "latitud": 10.9700,
    "longitud": -74.7850,
    "timestamp": "2025-12-04T10:40:00",
    "foto_base64": "imagenes_reportes/3.jpg",
    "descripcion": "Reparación de vía principal",
    "tipo_reporte": "Obras en Proceso",
    "fecha_inicio_evento": null,
    "fecha_fin_evento": null
  },
  {
    "id": 2,
    "latitud": 10.9850,
    "longitud": -74.8100,
    "timestamp": "2025-12-04T10:35:00",
    "foto_base64": "imagenes_reportes/2.jpg",
    "descripcion": "Torneo de Fútbol Inter-Universidades",
    "tipo_reporte": "Eventos Deportivos",
    "fecha_inicio_evento": "2025-12-20T08:00:00",
    "fecha_fin_evento": "2025-12-20T17:00:00"
  },
  {
    "id": 1,
    "latitud": 10.9639,
    "longitud": -74.7964,
    "timestamp": "2025-12-04T10:30:00",
    "foto_base64": "imagenes_reportes/1.jpg",
    "descripcion": "Festival de Música Vallenata 2025",
    "tipo_reporte": "Eventos Culturales",
    "fecha_inicio_evento": "2025-12-15T18:00:00",
    "fecha_fin_evento": "2025-12-15T23:30:00"
  }
]
```

## 🔍 Filtrar Eventos con SQL

### Eventos Activos (En Curso)
```sql
SELECT * FROM reportes 
WHERE tipo_reporte IN ('Eventos Culturales', 'Eventos Deportivos')
  AND NOW() BETWEEN fecha_inicio_evento AND fecha_fin_evento;
```

### Próximos Eventos (Futuros)
```sql
SELECT * FROM reportes 
WHERE tipo_reporte IN ('Eventos Culturales', 'Eventos Deportivos')
  AND fecha_inicio_evento > NOW()
ORDER BY fecha_inicio_evento ASC;
```

### Eventos Pasados
```sql
SELECT * FROM reportes 
WHERE tipo_reporte IN ('Eventos Culturales', 'Eventos Deportivos')
  AND fecha_fin_evento < NOW()
ORDER BY fecha_inicio_evento DESC;
```

### Eventos de Esta Semana
```sql
SELECT * FROM reportes 
WHERE tipo_reporte IN ('Eventos Culturales', 'Eventos Deportivos')
  AND YEARWEEK(fecha_inicio_evento) = YEARWEEK(NOW())
ORDER BY fecha_inicio_evento ASC;
```

## 📱 Formato de Fecha en Flutter

```dart
// Convertir DateTime a ISO 8601 para la API
String fechaISO = fechaInicioEvento.toIso8601String();
// Resultado: "2025-12-15T18:00:00.000"

// Formatear para mostrar en UI
String fechaFormateada = DateFormat('dd/MM/yyyy - hh:mm a', 'es_CO')
    .format(fechaInicioEvento);
// Resultado: "15/12/2025 - 06:00 PM"
```

## 🌍 Zona Horaria

Todas las fechas se convierten automáticamente a **Bogotá (America/Bogota, UTC-5)**:

```
Usuario envía: 2025-12-15T18:00:00
Backend guarda: 2025-12-15 18:00:00 (sin timezone)
MySQL almacena: 2025-12-15 18:00:00
```

## ✅ Validaciones Automáticas

### En Flutter
- ✓ Fecha de fin no puede ser anterior a fecha de inicio
- ✓ Solo permite fechas futuras (hasta 1 año)
- ✓ Formato validado antes de enviar

### En Backend
- ✓ Conversión automática a Bogotá
- ✓ Acepta con o sin timezone
- ✓ NULL si no es evento cultural/deportivo

## 🎨 Ejemplo Completo con Python

```python
import requests
from datetime import datetime, timedelta

# Crear evento que empieza mañana a las 7 PM
inicio = datetime.now() + timedelta(days=1)
inicio = inicio.replace(hour=19, minute=0, second=0, microsecond=0)

fin = inicio + timedelta(hours=4)  # Dura 4 horas

data = {
    "latitud": 10.9639,
    "longitud": -74.7964,
    "tipo_reporte": "Eventos Culturales",
    "descripcion": "Concierto de Rock",
    "foto_base64": "",
    "fecha_inicio_evento": inicio.isoformat(),
    "fecha_fin_evento": fin.isoformat()
}

response = requests.post(
    "http://3.148.29.34/reportes/",
    json=data
)

print(response.json())
```

## 🧪 Testing con Postman

### 1. Crear Collection: "Reportes GPS - Eventos"

### 2. Agregar Request: "Crear Evento Cultural"
- Method: POST
- URL: `http://3.148.29.34/reportes/`
- Headers:
  - `Content-Type: application/json`
- Body (raw JSON):
```json
{
  "latitud": 10.9639,
  "longitud": -74.7964,
  "tipo_reporte": "Eventos Culturales",
  "descripcion": "{{$randomLoremSentence}}",
  "foto_base64": "",
  "fecha_inicio_evento": "{{$isoTimestamp}}",
  "fecha_fin_evento": "{{$isoTimestamp}}"
}
```

### 3. Agregar Request: "Obtener Reportes"
- Method: GET
- URL: `http://3.148.29.34/reportes/`

---

**💡 Tip**: Usa variables de entorno en Postman para cambiar fácilmente entre dev/prod
