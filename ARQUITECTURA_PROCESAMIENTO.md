# Arquitectura del Sistema de Procesamiento de Imágenes GPS Reporter

## 📐 Diagrama de Arquitectura

```
┌──────────────┐
│   ESP32-CAM  │ (Captura imagen)
└──────┬───────┘
       │ HTTP POST (base64 + coords + timestamp)
       ▼
┌─────────────────────────────────────────────────┐
│   Servidor de Procesamiento (18.116.117.140)   │
│   ─────────────────────────────────────────     │
│                                                 │
│   mainIMG.py (Puerto 8000)                     │
│   ├── FastAPI                                  │
│   ├── YOLOv8n (Detección de personas)         │
│   ├── OpenCV (Procesamiento)                  │
│   └── HTTP Client (Envío a API principal)     │
│                                                 │
│   Recursos: c7i-flex.large                     │
│   ├── 2 vCPU                                   │
│   ├── 4 GB RAM                                 │
│   └── ~500 MB para modelo YOLO                │
└─────────────┬───────────────────────────────────┘
              │ HTTP POST (base64 + aforo + coords)
              ▼
┌─────────────────────────────────────────────────┐
│   Servidor Principal (tu servidor actual)      │
│   ─────────────────────────────────────────     │
│                                                 │
│   main.py (Puerto 5000)                        │
│   ├── FastAPI                                  │
│   ├── MySQL (Almacenamiento)                   │
│   ├── AWS SES (Emails)                         │
│   └── Sistema de autenticación                 │
│                                                 │
│   Tablas:                                       │
│   ├── reportes (lat, lng, timestamp,           │
│   │              foto_ruta, aforo)             │
│   └── usuarios (auth + verificación)           │
└─────────────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────────┐
│   App Flutter (gps_reporter)                    │
│   Consulta reportes con aforo                   │
└─────────────────────────────────────────────────┘
```

## 🔄 Flujo de Procesamiento

### 1️⃣ Captura desde ESP32
```
ESP32-CAM captura imagen
  ↓
Codifica a base64
  ↓
Envía POST a http://18.116.117.140:8000/procesar-imagen
  JSON: {
    "foto_base64": "...",
    "timestamp": "2025-12-02T10:30:00",
    "latitud": -12.0464,
    "longitud": -77.0428
  }
```

### 2️⃣ Procesamiento en mainIMG.py
```
Recibe imagen base64
  ↓
Decodifica a numpy array (OpenCV)
  ↓
Ejecuta YOLOv8.predict()
  ↓
Detecta personas (clase 0 en COCO)
  ↓
Dibuja bounding boxes
  ↓
Calcula aforo = len(personas)
  ↓
Codifica imagen procesada a base64
  ↓
Envía a API principal
```

### 3️⃣ Almacenamiento en main.py
```
Recibe de mainIMG.py:
  - foto_base64 (con boxes)
  - aforo (int)
  - timestamp
  - coordenadas
  ↓
Guarda imagen en disco (imagenes_reportes/)
  ↓
Inserta en MySQL:
  INSERT INTO reportes 
  (latitud, longitud, timestamp, 
   foto_base64, aforo, tipo_reporte)
  ↓
Retorna 200 OK
```

## 📊 Características del Sistema

### Servidor de Procesamiento (18.116.117.140)
- **Modelo:** YOLOv8n (nano) - 6 MB
- **Precisión:** ~45% confianza mínima
- **Velocidad:** 0.5-1.5 seg/imagen
- **Capacidad:** 40-120 imágenes/minuto
- **RAM:** ~800 MB usados (modelo + procesamiento)
- **CPU:** 40-60% durante procesamiento

### Ventajas de Arquitectura Distribuida
✅ **Escalabilidad:** Procesamiento separado de la lógica de negocio
✅ **Rendimiento:** main.py no se satura con procesamiento pesado
✅ **Especialización:** Instancia optimizada para ML (c7i-flex)
✅ **Tolerancia a fallos:** Si falla detección, API principal sigue operativa
✅ **Flexibilidad:** Fácil cambiar modelo YOLO sin tocar main.py

## 🔧 Configuración de Red

### Puertos Requeridos

**Servidor de Procesamiento (18.116.117.140):**
- Puerto 8000 (TCP) - API de procesamiento
- Puerto 22 (SSH) - Administración

**Servidor Principal:**
- Puerto 5000 (TCP) - API principal
- Puerto 3306 (TCP) - MySQL (interno)

### Security Groups

```
# Servidor de Procesamiento
Entrada:
  - 8000/tcp desde 0.0.0.0/0 (o IP ESP32)
  - 22/tcp desde tu IP
  
Salida:
  - Todo el tráfico (para enviar a API principal)

# Servidor Principal  
Entrada:
  - 5000/tcp desde IP del servidor de procesamiento
  - 5000/tcp desde 0.0.0.0/0 (app Flutter)
  - 3306/tcp desde localhost (MySQL interno)
```

## 📁 Estructura de Archivos

### Servidor de Procesamiento
```
/home/ubuntu/gps-image-processor/
├── mainIMG.py              # API FastAPI
├── requirements_img.txt    # Dependencias
├── .env                    # Configuración
├── venv/                   # Entorno virtual
├── temp_procesadas/        # Imágenes temporales
└── yolov8n.pt             # Modelo descargado
```

### Servidor Principal
```
reportes-gps-api/
├── main.py                 # API principal (actualizada)
├── requirements.txt        # Dependencias
├── .env                    # Config DB + AWS
├── imagenes_reportes/      # Imágenes con aforo
├── update_db_aforo.py      # Script de migración BD
└── test_servidor_imagen.py # Tests
```

## 🚀 Pasos de Deployment

### 1. En el Servidor Principal
```bash
# Actualizar base de datos
python update_db_aforo.py

# Reiniciar API
python main.py
```

### 2. En el Servidor de Procesamiento
```bash
# Ver INSTALACION_SERVIDOR_IMAGEN.md
ssh ubuntu@18.116.117.140
cd /home/ubuntu/gps-image-processor

# Instalar dependencias
pip install -r requirements_img.txt

# Configurar .env
nano .env
# API_PRINCIPAL_URL=http://IP-PRINCIPAL:5000

# Iniciar servicio
python mainIMG.py
```

### 3. Pruebas
```bash
# Desde tu máquina local
python test_servidor_imagen.py
```

## 🔍 Monitoreo

### Endpoints de Salud

**Servidor de Procesamiento:**
```bash
curl http://18.116.117.140:8000/health
curl http://18.116.117.140:8000/stats
```

**Servidor Principal:**
```bash
curl http://IP-PRINCIPAL:5000/debug/health
curl http://IP-PRINCIPAL:5000/stats
```

### Logs
```bash
# Servidor de procesamiento
sudo journalctl -u gps-image-processor -f

# Servidor principal
# Ver logs de uvicorn/FastAPI
```

## 📈 Métricas Esperadas

| Métrica | Valor |
|---------|-------|
| Latencia total (ESP32 → BD) | 2-4 seg |
| Procesamiento YOLO | 0.5-1.5 seg |
| Transferencia red | 0.2-0.5 seg |
| Guardado BD | 0.1-0.3 seg |
| Precisión detección | 75-85% |
| Imágenes/hora | 900-3600 |

## 🔐 Seguridad

1. **Autenticación:** Sin auth en mainIMG.py (red interna)
2. **API Principal:** Mantiene su sistema de auth
3. **Firewall:** UFW configurado en ambos servidores
4. **HTTPS:** Recomendado para producción (nginx + Let's Encrypt)

## 🛠️ Mantenimiento

### Actualizar Modelo YOLO
```bash
# En servidor de procesamiento
cd /home/ubuntu/gps-image-processor
source venv/bin/activate

# Cambiar en .env
MODELO_YOLO=yolov8s.pt  # Modelo más preciso

# Reiniciar
sudo systemctl restart gps-image-processor
```

### Limpiar Imágenes Temporales
```bash
# Cada 7 días (cron job)
find /home/ubuntu/gps-image-processor/temp_procesadas -mtime +7 -delete
```

## ❓ FAQ

**P: ¿Puedo usar GPU?**
R: Sí, cambia a instancia con GPU (g4dn.xlarge). YOLO detectará automáticamente CUDA.

**P: ¿Qué pasa si mainIMG.py falla?**
R: ESP32 puede enviar directamente a main.py sin aforo (campo opcional).

**P: ¿Puedo procesar video?**
R: Sí, pero requiere cambios. Mejor usar frames individuales.

**P: ¿Cómo escalar horizontalmente?**
R: Múltiples instancias mainIMG.py con load balancer.

## 📝 Notas de Versión

**v1.0.0** (2025-12-02)
- ✅ Procesamiento con YOLOv8n
- ✅ Integración con main.py
- ✅ Detección de múltiples personas
- ✅ Dibujo de bounding boxes
- ✅ Estadísticas en tiempo real
