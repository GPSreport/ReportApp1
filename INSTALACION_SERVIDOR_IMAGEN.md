# Guía de Instalación - Servidor de Procesamiento de Imágenes
# EC2: c7i-flex.large (18.116.117.140)

## 📋 Prerrequisitos

### 1. Conectar a la instancia EC2
```bash
ssh -i tu-clave.pem ubuntu@18.116.117.140
```

### 2. Actualizar el sistema
```bash
sudo apt update
sudo apt upgrade -y
```

### 3. Instalar Python 3.10+
```bash
sudo apt install python3.10 python3.10-venv python3-pip -y
python3.10 --version
```

### 4. Instalar dependencias del sistema para OpenCV
```bash
sudo apt install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libgstreamer1.0-0 \
    ffmpeg
```

## 🚀 Instalación del Servidor

### 1. Crear directorio del proyecto
```bash
mkdir -p /home/ubuntu/gps-image-processor
cd /home/ubuntu/gps-image-processor
```

### 2. Copiar archivos al servidor
```bash
# Desde tu máquina local (en el directorio del proyecto):
scp -i tu-clave.pem mainIMG.py ubuntu@18.116.117.140:/home/ubuntu/gps-image-processor/
scp -i tu-clave.pem requirements_img.txt ubuntu@18.116.117.140:/home/ubuntu/gps-image-processor/
scp -i tu-clave.pem .env.imagen ubuntu@18.116.117.140:/home/ubuntu/gps-image-processor/.env
```

### 3. Crear entorno virtual
```bash
cd /home/ubuntu/gps-image-processor
python3.10 -m venv venv
source venv/bin/activate
```

### 4. Instalar dependencias Python
```bash
pip install --upgrade pip
pip install -r requirements_img.txt
```

**⏱️ Tiempo estimado:** 5-10 minutos (PyTorch es pesado)

### 5. Configurar variables de entorno
```bash
nano .env
```

Editar:
```env
PUERTO_IMG=8000
API_PRINCIPAL_URL=http://IP-SERVIDOR-PRINCIPAL:5000
MODELO_YOLO=yolov8n.pt
CONFIANZA_MIN=0.45
```

### 6. Descargar modelo YOLO (primera vez)
```bash
# El modelo se descarga automáticamente en el primer uso
# Para pre-descargar:
python3 -c "from ultralytics import YOLO; YOLO('yolov8n.pt')"
```

**📦 Tamaño del modelo:**
- yolov8n.pt: ~6 MB
- yolov8s.pt: ~22 MB
- yolov8m.pt: ~50 MB

## 🔧 Configuración del Firewall (Security Group)

### Reglas de entrada necesarias:
```
Puerto 8000 (TCP) - Origen: 0.0.0.0/0 (o IP del ESP32)
Puerto 22 (SSH) - Origen: Tu IP
```

Configurar en AWS Console:
1. EC2 → Instancias → Security Groups
2. Editar reglas de entrada
3. Agregar regla personalizada TCP puerto 8000

## ▶️ Ejecución del Servidor

### Modo de prueba (terminal):
```bash
cd /home/ubuntu/gps-image-processor
source venv/bin/activate
python mainIMG.py
```

### Modo producción con systemd (recomendado):

#### 1. Crear servicio systemd
```bash
sudo nano /etc/systemd/system/gps-image-processor.service
```

Contenido:
```ini
[Unit]
Description=GPS Image Processor - YOLO Aforo Detection
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/gps-image-processor
Environment="PATH=/home/ubuntu/gps-image-processor/venv/bin"
ExecStart=/home/ubuntu/gps-image-processor/venv/bin/python mainIMG.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

#### 2. Activar y arrancar el servicio
```bash
sudo systemctl daemon-reload
sudo systemctl enable gps-image-processor
sudo systemctl start gps-image-processor
```

#### 3. Verificar estado
```bash
sudo systemctl status gps-image-processor
```

#### 4. Ver logs
```bash
sudo journalctl -u gps-image-processor -f
```

## 🧪 Pruebas

### 1. Verificar servidor activo
```bash
curl http://localhost:8000/health
```

### 2. Verificar desde internet
```bash
curl http://18.116.117.140:8000/health
```

### 3. Test con imagen de prueba (desde Python)
```python
import requests
import base64

# Leer imagen
with open("test.jpg", "rb") as f:
    img_b64 = base64.b64encode(f.read()).decode()

# Enviar a servidor
response = requests.post(
    "http://18.116.117.140:8000/procesar-imagen",
    json={
        "foto_base64": img_b64,
        "timestamp": "2025-12-02T10:30:00",
        "latitud": -12.0464,
        "longitud": -77.0428
    }
)

print(response.json())
```

## 📊 Monitoreo

### Ver uso de CPU y RAM
```bash
htop
```

### Ver logs en tiempo real
```bash
sudo journalctl -u gps-image-processor -f --since "5 minutes ago"
```

### Verificar estadísticas del servidor
```bash
curl http://18.116.117.140:8000/stats
```

## 🔄 Actualización del código

```bash
# Detener servicio
sudo systemctl stop gps-image-processor

# Actualizar código (desde tu máquina local)
scp -i tu-clave.pem mainIMG.py ubuntu@18.116.117.140:/home/ubuntu/gps-image-processor/

# Reiniciar servicio
sudo systemctl start gps-image-processor
```

## 🐛 Troubleshooting

### Error: "CUDA not available"
**Normal en CPU.** YOLO usará CPU automáticamente.

### Error: "Model download failed"
```bash
# Descargar manualmente
cd /home/ubuntu/gps-image-processor
source venv/bin/activate
python3 -c "from ultralytics import YOLO; YOLO('yolov8n.pt')"
```

### Error: "Cannot connect to API principal"
Verificar:
1. IP correcta en `.env` → `API_PRINCIPAL_URL`
2. Puerto 5000 abierto en servidor principal
3. Ping al servidor: `ping IP-SERVIDOR-PRINCIPAL`

### Alta latencia en detección
Opciones:
1. Usar modelo más ligero: `MODELO_YOLO=yolov5n.pt`
2. Reducir resolución de imagen antes de procesar
3. Aumentar `CONFIANZA_MIN` para menos detecciones

## 📈 Rendimiento Esperado

**En c7i-flex.large (2 vCPU, 4GB RAM):**
- Modelo: YOLOv8n
- Resolución: 640x480
- Tiempo por imagen: 0.5 - 1.5 segundos
- Imágenes/minuto: 40-120

## 🔐 Seguridad

### 1. Configurar firewall local (UFW)
```bash
sudo ufw allow 8000/tcp
sudo ufw allow 22/tcp
sudo ufw enable
```

### 2. Limitar acceso por IP (opcional)
Editar Security Group para permitir solo IPs específicas.

## 📝 Notas Importantes

1. **Primera ejecución:** Descarga automática del modelo (~6 MB)
2. **Warming up:** Primera detección tarda ~3-5 segundos (luego normaliza)
3. **Memoria:** YOLOv8n usa ~500-800 MB RAM
4. **CPU:** Uso típico 40-60% durante procesamiento
5. **Red:** ~200 KB por imagen procesada enviada a API principal

## ✅ Checklist de Instalación

- [ ] Python 3.10+ instalado
- [ ] Dependencias del sistema instaladas (OpenCV)
- [ ] Entorno virtual creado
- [ ] requirements_img.txt instalado
- [ ] .env configurado con URL de API principal
- [ ] Puerto 8000 abierto en Security Group
- [ ] Servicio systemd configurado
- [ ] Servidor arrancado y respondiendo en /health
- [ ] Test de detección exitoso

## 🆘 Soporte

Ver logs detallados:
```bash
sudo journalctl -u gps-image-processor -n 100 --no-pager
```

Reiniciar completamente:
```bash
sudo systemctl restart gps-image-processor
```
