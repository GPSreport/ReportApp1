# 📊 Documentación - Sistema de Aforo para Lugares de Interés

## 🎯 Resumen

Sistema independiente para monitoreo de aforo en lugares de interés usando procesamiento de imágenes con YOLOv8. Los datos se almacenan en una tabla separada (`aforo_lugares`) sin afectar la funcionalidad de reportes existente.

---

## 📐 Arquitectura

```
ESP32-CAM (Lugar de Interés)
        ↓
        │ POST: foto_base64 + timestamp + lugar_id
        ↓
Servidor de Procesamiento (18.116.117.140:8000)
        │ /procesar-imagen
        ↓
        │ YOLOv8 detecta personas → calcula aforo
        ↓
        │ POST: foto_base64 + aforo + timestamp + lugar_id
        ↓
API Principal (main.py:5000)
        │ /aforo/registrar
        ↓
MySQL → Tabla: aforo_lugares
        ├── foto_ruta
        ├── timestamp_captura
        ├── aforo
        ├── latitud/longitud
        └── lugar_id
```

---

## 🗄️ Esquema de Base de Datos

### Tabla: `aforo_lugares`

```sql
CREATE TABLE aforo_lugares (
    id INT AUTO_INCREMENT PRIMARY KEY,
    foto_ruta VARCHAR(500) NOT NULL COMMENT 'Ruta de la imagen procesada',
    timestamp_captura DATETIME NOT NULL COMMENT 'Timestamp de la captura original',
    aforo INT NOT NULL COMMENT 'Número de personas detectadas',
    latitud DECIMAL(10, 8) NULL,
    longitud DECIMAL(11, 8) NULL,
    lugar_id VARCHAR(100) NULL COMMENT 'Identificador del lugar de interés',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_timestamp (timestamp_captura),
    INDEX idx_lugar (lugar_id),
    INDEX idx_aforo (aforo)
);
```

**Ejemplo de registro:**
```json
{
    "id": 1,
    "foto_ruta": "imagenes_reportes/aforo/aforo_1_biblioteca.jpg",
    "timestamp_captura": "2025-12-02T14:30:00",
    "aforo": 12,
    "latitud": -12.0464,
    "longitud": -77.0428,
    "lugar_id": "biblioteca",
    "created_at": "2025-12-02T14:30:15"
}
```

---

## 🔌 Endpoints de la API Principal

### 1️⃣ **POST /aforo/registrar**

**URL completa para mainIMG.py:**
```
http://TU-SERVIDOR-PRINCIPAL:5000/aforo/registrar
```

**Descripción:** Recibe datos de aforo desde el servidor de procesamiento de imágenes.

**Request Body:**
```json
{
    "foto_base64": "iVBORw0KGgoAAAANS...",
    "timestamp": "2025-12-02T14:30:00",
    "aforo": 12,
    "latitud": -12.0464,
    "longitud": -77.0428,
    "lugar_id": "biblioteca"
}
```

**Response (200 OK):**
```json
{
    "success": true,
    "message": "Aforo registrado exitosamente. 12 persona(s) detectada(s)",
    "id": 1,
    "aforo": 12,
    "timestamp": "2025-12-02T14:30:00"
}
```

**Campos:**
- `foto_base64` (string, requerido): Imagen procesada con bounding boxes en base64
- `timestamp` (string, requerido): Timestamp ISO 8601 de la captura
- `aforo` (int, requerido): Número de personas detectadas
- `latitud` (float, opcional): Coordenada de latitud
- `longitud` (float, opcional): Coordenada de longitud
- `lugar_id` (string, opcional): Identificador del lugar (ej: "biblioteca", "cafeteria")

---

### 2️⃣ **GET /aforo/historial**

**Descripción:** Obtener historial de registros de aforo.

**Parámetros Query:**
- `lugar_id` (opcional): Filtrar por lugar específico
- `limite` (opcional, default=50, max=500): Número de registros
- `orden` (opcional, default="desc"): "asc" o "desc"

**Ejemplos:**
```bash
# Todos los registros (últimos 50)
GET http://localhost:5000/aforo/historial

# Historial de un lugar específico
GET http://localhost:5000/aforo/historial?lugar_id=biblioteca&limite=100

# Orden ascendente (más antiguos primero)
GET http://localhost:5000/aforo/historial?orden=asc&limite=20
```

**Response:**
```json
{
    "success": true,
    "total": 50,
    "registros": [
        {
            "id": 25,
            "foto_ruta": "imagenes_reportes/aforo/aforo_25_biblioteca.jpg",
            "timestamp_captura": "2025-12-02T14:30:00",
            "aforo": 12,
            "latitud": -12.0464,
            "longitud": -77.0428,
            "lugar_id": "biblioteca",
            "created_at": "2025-12-02T14:30:15"
        }
    ]
}
```

---

### 3️⃣ **GET /aforo/estadisticas**

**Descripción:** Obtener estadísticas agregadas de aforo.

**Parámetros Query:**
- `lugar_id` (opcional): Estadísticas de un lugar específico

**Ejemplos:**
```bash
# Estadísticas globales
GET http://localhost:5000/aforo/estadisticas

# Estadísticas de un lugar
GET http://localhost:5000/aforo/estadisticas?lugar_id=biblioteca
```

**Response:**
```json
{
    "success": true,
    "lugar_id": "biblioteca",
    "estadisticas": {
        "total_registros": 150,
        "aforo_promedio": 18.5,
        "aforo_maximo": 45,
        "aforo_minimo": 0,
        "ultimo_registro": "2025-12-02T14:30:00",
        "total_lugares": 1
    }
}
```

---

## 🚀 Configuración

### 1. Actualizar Base de Datos

**En el servidor principal:**
```bash
cd /ruta/a/reportes-gps-api
python update_db_aforo.py
```

O ejecutar manualmente:
```sql
ALTER TABLE aforo_lugares 
ADD COLUMN IF NOT EXISTS aforo INT DEFAULT NULL;

-- La tabla aforo_lugares ya se crea automáticamente en init_database()
```

### 2. Configurar mainIMG.py (.env)

**En el servidor de procesamiento (18.116.117.140):**
```env
# Archivo: /home/ubuntu/gps-image-processor/.env

PUERTO_IMG=8000
API_PRINCIPAL_URL=http://TU-SERVIDOR-PRINCIPAL:5000
MODELO_YOLO=yolov8n.pt
CONFIANZA_MIN=0.45
```

⚠️ **Importante:** Cambiar `TU-SERVIDOR-PRINCIPAL` por la IP o dominio real.

### 3. Reiniciar Servicios

**Servidor principal:**
```bash
# Si usas systemd
sudo systemctl restart gps-reporter

# O directamente
python main.py
```

**Servidor de procesamiento:**
```bash
sudo systemctl restart gps-image-processor
```

---

## 📡 Flujo Completo de Procesamiento

### Paso 1: ESP32-CAM Captura y Envía
```cpp
// Código ESP32 (ejemplo)
POST http://18.116.117.140:8000/procesar-imagen
{
    "foto_base64": "...",
    "timestamp": "2025-12-02T14:30:00",
    "latitud": -12.0464,
    "longitud": -77.0428,
    "lugar_id": "biblioteca"
}
```

### Paso 2: mainIMG.py Procesa
1. Recibe imagen
2. Decodifica base64 → numpy array
3. Ejecuta YOLOv8 → detecta personas
4. Dibuja bounding boxes
5. Calcula aforo = número de personas
6. Codifica imagen procesada a base64

### Paso 3: mainIMG.py Envía a API Principal
```python
POST http://TU-SERVIDOR:5000/aforo/registrar
{
    "foto_base64": "...imagen con boxes...",
    "timestamp": "2025-12-02T14:30:00",
    "aforo": 12,
    "latitud": -12.0464,
    "longitud": -77.0428,
    "lugar_id": "biblioteca"
}
```

### Paso 4: main.py Almacena
1. Valida datos
2. Guarda imagen en `imagenes_reportes/aforo/`
3. Inserta registro en `aforo_lugares`
4. Retorna confirmación

---

## 📂 Estructura de Archivos

```
reportes-gps-api/
├── imagenes_reportes/
│   ├── aforo/                          # ← Imágenes de aforo
│   │   ├── aforo_1_biblioteca.jpg
│   │   ├── aforo_2_cafeteria.jpg
│   │   └── aforo_3_general.jpg
│   └── [otras imágenes de reportes]
├── main.py                             # ← API principal (modificado)
└── update_db_aforo.py                  # ← Script de migración BD
```

---

## 🧪 Pruebas

### Test 1: Verificar Endpoint desde Terminal

```bash
curl -X POST http://localhost:5000/aforo/registrar \
  -H "Content-Type: application/json" \
  -d '{
    "foto_base64": "iVBORw0KGgoAAAANS...",
    "timestamp": "2025-12-02T14:30:00",
    "aforo": 12,
    "lugar_id": "test"
  }'
```

### Test 2: Verificar Historial

```bash
curl http://localhost:5000/aforo/historial?limite=5
```

### Test 3: Verificar Estadísticas

```bash
curl http://localhost:5000/aforo/estadisticas
```

### Test 4: Desde Python

```python
import requests
import base64

# Leer imagen
with open("test.jpg", "rb") as f:
    img_b64 = base64.b64encode(f.read()).decode()

# Enviar
response = requests.post(
    "http://localhost:5000/aforo/registrar",
    json={
        "foto_base64": img_b64,
        "timestamp": "2025-12-02T14:30:00",
        "aforo": 5,
        "lugar_id": "biblioteca"
    }
)

print(response.json())
```

---

## 📊 Consultas SQL Útiles

### Aforo promedio por hora
```sql
SELECT 
    DATE_FORMAT(timestamp_captura, '%Y-%m-%d %H:00') as hora,
    AVG(aforo) as aforo_promedio,
    COUNT(*) as mediciones
FROM aforo_lugares
WHERE lugar_id = 'biblioteca'
GROUP BY hora
ORDER BY hora DESC;
```

### Top 10 picos de aforo
```sql
SELECT 
    timestamp_captura,
    aforo,
    lugar_id
FROM aforo_lugares
ORDER BY aforo DESC
LIMIT 10;
```

### Comparar lugares
```sql
SELECT 
    lugar_id,
    COUNT(*) as total_mediciones,
    AVG(aforo) as aforo_promedio,
    MAX(aforo) as aforo_maximo
FROM aforo_lugares
GROUP BY lugar_id
ORDER BY aforo_promedio DESC;
```

---

## 🔐 Seguridad

### Recomendaciones:

1. **Autenticación (futuro):**
   - Añadir API key para `/aforo/registrar`
   - Solo permitir IPs conocidas (servidor de procesamiento)

2. **Rate Limiting:**
   ```python
   # Añadir a main.py
   from slowapi import Limiter
   limiter = Limiter(key_func=get_remote_address)
   
   @app.post("/aforo/registrar")
   @limiter.limit("60/minute")
   async def registrar_aforo(...):
       ...
   ```

3. **Validación de tamaño:**
   - Limitar tamaño de `foto_base64` (ej: max 5 MB)

---

## 🐛 Troubleshooting

### Error: "foto_base64 es requerida"
**Causa:** Campo vacío o None  
**Solución:** Verificar que mainIMG.py envía la imagen procesada

### Error: "Formato de timestamp inválido"
**Causa:** Timestamp no está en formato ISO 8601  
**Solución:** Usar formato: `2025-12-02T14:30:00` o `2025-12-02T14:30:00Z`

### Imágenes no se guardan
**Causa:** Carpeta `imagenes_reportes/aforo/` no existe  
**Solución:** Se crea automáticamente, verificar permisos de escritura

### No recibe datos desde mainIMG.py
**Verificar:**
1. URL en `.env` de mainIMG.py es correcta
2. Puerto 5000 abierto en firewall
3. Logs de mainIMG.py: `sudo journalctl -u gps-image-processor -f`

---

## 📈 Mejoras Futuras

- [ ] Dashboard web para visualizar aforo en tiempo real
- [ ] Alertas cuando aforo > umbral
- [ ] Exportar datos a CSV/Excel
- [ ] Gráficos de tendencias por hora/día
- [ ] Comparación entre lugares
- [ ] API REST para apps móviles

---

## ✅ Checklist de Implementación

- [x] Tabla `aforo_lugares` creada
- [x] Endpoint `/aforo/registrar` implementado
- [x] Endpoint `/aforo/historial` implementado
- [x] Endpoint `/aforo/estadisticas` implementado
- [x] mainIMG.py actualizado para enviar a nuevo endpoint
- [ ] BD migrada con `update_db_aforo.py`
- [ ] Configurar `.env` en mainIMG.py
- [ ] Reiniciar servicios
- [ ] Probar flujo completo ESP32 → mainIMG → main.py

---

## 📞 Endpoints de Referencia Rápida

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/aforo/registrar` | POST | Registrar nuevo aforo |
| `/aforo/historial` | GET | Obtener historial |
| `/aforo/estadisticas` | GET | Estadísticas agregadas |

**URL base servidor principal:** `http://TU-SERVIDOR:5000`

**URL para mainIMG.py (.env):**
```env
API_PRINCIPAL_URL=http://TU-SERVIDOR:5000
```

El endpoint específico se construye automáticamente en mainIMG.py:
```python
f"{API_PRINCIPAL_URL}/aforo/registrar"
```
