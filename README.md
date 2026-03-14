## Technologies Used

### Programming and markup languages
<img src="https://img.shields.io/badge/python-%233776AB.svg?style=for-the-badge&logo=python&logoColor=white"/>
<img src="https://img.shields.io/badge/html5-%23E34F26.svg?style=for-the-badge&logo=html5&logoColor=white"/>
<img src="https://img.shields.io/badge/css3-%231572B6.svg?style=for-the-badge&logo=css3&logoColor=white"/>
<img src="https://img.shields.io/badge/sql-%234479A1.svg?style=for-the-badge&logo=mysql&logoColor=white"/>
<img src="https://img.shields.io/badge/markdown-%23000000.svg?style=for-the-badge&logo=markdown&logoColor=white"/>

### 🧰 Frameworks and libraries
<img src="https://img.shields.io/badge/fastapi-%23009688.svg?style=for-the-badge&logo=fastapi&logoColor=white"/>
<img src="https://img.shields.io/badge/uvicorn-%23499848.svg?style=for-the-badge&logo=gunicorn&logoColor=white"/>
<img src="https://img.shields.io/badge/pydantic-%23E92063.svg?style=for-the-badge&logo=pydantic&logoColor=white"/>
<img src="https://img.shields.io/badge/opencv-%235C3EE8.svg?style=for-the-badge&logo=opencv&logoColor=white"/>
<img src="https://img.shields.io/badge/pytorch-%23EE4C2C.svg?style=for-the-badge&logo=pytorch&logoColor=white"/>
<img src="https://img.shields.io/badge/leaflet-%23199B4A.svg?style=for-the-badge&logo=leaflet&logoColor=white"/>
<img src="https://img.shields.io/badge/bootstrap-%237952B3.svg?style=for-the-badge&logo=bootstrap&logoColor=white"/>

### Databases and cloud hosting
<img src="https://img.shields.io/badge/mysql-%234479A1.svg?style=for-the-badge&logo=mysql&logoColor=white"/>
<img src="https://img.shields.io/badge/aws_ec2-%23FF9900.svg?style=for-the-badge&logo=amazonec2&logoColor=white"/>
<img src="https://img.shields.io/badge/aws_ses-%23FF9900.svg?style=for-the-badge&logo=amazonsimpleemailservice&logoColor=white"/>

### Software and tools
<img src="https://img.shields.io/badge/git-%23F05033.svg?style=for-the-badge&logo=git&logoColor=white"/>
<img src="https://img.shields.io/badge/pip-%233775A9.svg?style=for-the-badge&logo=pypi&logoColor=white"/>
<img src="https://img.shields.io/badge/swagger-%2385EA2D.svg?style=for-the-badge&logo=swagger&logoColor=black"/>
<img src="https://img.shields.io/badge/postman-%23FF6C37.svg?style=for-the-badge&logo=postman&logoColor=white"/>

# 🗺️ Reportes GPS API - Backend del Sistema

## 📋 Resumen del Proyecto

Este componente constituye el **núcleo del sistema de reportes GPS**, un backend desarrollado con **FastAPI** que actúa como servidor principal para la gestión de reportes geolocalizados, autenticación de usuarios y procesamiento de imágenes con detección de aforo mediante inteligencia artificial.

---

## 🏗️ Arquitectura del Sistema

<img width="1260" height="982" alt="image" src="https://github.com/user-attachments/assets/af4506c0-777f-4137-8ebe-a056973ae20b" />


```
┌──────────────────────────────────────────────────────────────────────┐
│                    ARQUITECTURA GENERAL                               │
├──────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  ┌─────────────┐     ┌─────────────────────┐     ┌─────────────────┐ │
│  │  ESP32-CAM  │────▶│  Servidor Imágenes  │────▶│  API Principal  │ │
│  │ (Captura)   │     │  mainIMG.py:8000    │     │  main.py:5000   │ │
│  └─────────────┘     │  + YOLOv8 (Aforo)   │     └────────┬────────┘ │
│                      └─────────────────────┘              │          │
│                                                           │          │
│  ┌─────────────┐                                          │          │
│  │ App Flutter │──────────────────────────────────────────┤          │
│  │ gps_reporter│     Reportes GPS + Fotos                 │          │
│  └─────────────┘                                          │          │
│                                                           ▼          │
│                                                ┌─────────────────────┐│
│                                                │      MySQL DB       ││
│                                                │  + AWS SES (Email)  ││
│                                                └─────────────────────┘│
└──────────────────────────────────────────────────────────────────────┘
```

---

## 📁 Estructura de Archivos

| Archivo                     | Descripción                                                    |
|-----------------------------|----------------------------------------------------------------|
| `main.py`                   | API principal FastAPI (puerto 5000) Servidor 1                 |
| `mainIMG.py`                | Procesamiento de imágenes con YOLOv8 (puerto 8000) Servidor 2  |
| `mapa.html`                 | Interfaz web con mapa interactivo Leaflet                      |
| `requirements.txt`          | Dependencias de Python para API principal                      |
| `requirements_img.txt`      | Dependencias para servidor de procesamiento de imágenes        |

---

## 🔌 API Principal (main.py)

### Endpoints de Autenticación

| Método | Endpoint                          | Descripción                                     |
|--------|-----------------------------------|-------------------------------------------------|
| POST   | `/login`                          | Autenticación de usuarios                       |
| POST   | `/usuarios/crear`                 | Registro de nuevos usuarios                     |
| GET    | `/verificar-email`                | Verificación por enlace en email                |
| POST   | `/enviar-codigo`                  | Envía código de 6 dígitos para verificación     |
| POST   | `/verificar-codigo`               | Valida código de verificación                   |
| GET    | `/usuario-estado/{email}`         | Obtiene estado de verificación del usuario      |
| POST   | `/recuperar-usuario/enviar-codigo`| Envía código para recuperar contraseña          |
| POST   | `/recuperar-usuario/verificar`    | Verifica código y actualiza contraseña          |

### Endpoints de Reportes

| Método | Endpoint          | Descripción                                    |
|--------|-------------------|------------------------------------------------|
| GET    | `/reportes/`      | Obtiene todos los reportes                     |
| POST   | `/reportes/`      | Crea un nuevo reporte con coordenadas y foto   |
| GET    | `/stats`          | Estadísticas de reportes                       |
| GET    | `/mapa`           | Visualización en mapa interactivo              |

### Endpoints de Aforo (Sistema de Visión por Computadora)

| Método | Endpoint              | Descripción                                    |
|--------|-----------------------|------------------------------------------------|
| POST   | `/aforo/registrar`    | Recibe datos de aforo desde servidor de imágenes|
| GET    | `/aforo/`             | Lista historial de aforo por lugares           |

---

## 🖼️ Servidor de Procesamiento de Imágenes (mainIMG.py)

Este servidor especializado corre en una instancia AWS separada (c7i-flex.large) optimizada para procesamiento de ML.

### Características

- **Modelo:** YOLOv8n (nano) - 6 MB
- **Función:** Detección de personas en imágenes
- **Precisión:** 45% confianza mínima
- **Velocidad:** 0.5-1.5 segundos/imagen
- **IP:** 18.116.117.140:8000

### Flujo de Procesamiento

```
ESP32-CAM captura imagen
        ↓
POST /procesar-imagen (base64 + coordenadas + timestamp)
        ↓
Decodifica imagen → OpenCV
        ↓
YOLOv8.predict() → Detecta personas (clase 0 COCO)
        ↓
Dibuja bounding boxes + cuenta personas
        ↓
Envía a API principal: /aforo/registrar
```

### Endpoints del Servidor de Imágenes

| Método | Endpoint            | Descripción                                    |
|--------|---------------------|------------------------------------------------|
| POST   | `/procesar-imagen`  | Recibe imagen del ESP32, procesa y reenvía     |
| GET    | `/health`           | Estado del servidor y modelo YOLO              |
| GET    | `/stats`            | Estadísticas de procesamiento                  |

---

## 🗄️ Base de Datos MySQL

### Tablas Principales

#### `reportes`
```sql
- id INT PRIMARY KEY AUTO_INCREMENT
- latitud DECIMAL(10, 8)
- longitud DECIMAL(11, 8)
- timestamp DATETIME
- foto_base64 LONGTEXT (ruta de imagen)
- descripcion TEXT
- tipo_reporte VARCHAR(50)
- fecha_inicio_evento DATETIME
- fecha_fin_evento DATETIME
- created_at TIMESTAMP
```

#### `usuarios`
```sql
- id INT PRIMARY KEY AUTO_INCREMENT
- usuario VARCHAR(50) UNIQUE
- clave_hash VARCHAR(64) (SHA-256)
- nombres VARCHAR(100)
- telefono VARCHAR(20)
- correo VARCHAR(255) UNIQUE
- activo TINYINT (1=registrado, 3=verificado)
- created_at TIMESTAMP
- last_login TIMESTAMP
```

#### `aforo_lugares`
```sql
- id INT PRIMARY KEY AUTO_INCREMENT
- foto_ruta VARCHAR(500)
- timestamp_captura DATETIME
- aforo INT (número de personas)
- latitud DECIMAL(10, 8)
- longitud DECIMAL(11, 8)
- lugar_id VARCHAR(100)
- created_at TIMESTAMP
```

#### `verification_tokens`
```sql
- id INT PRIMARY KEY
- usuario_id INT (FK → usuarios)
- token VARCHAR(255) UNIQUE
- codigo VARCHAR(6) (código de 6 dígitos)
- expires_at TIMESTAMP
- code_expires_at TIMESTAMP (15 minutos)
- used BOOLEAN
```

---

## 📧 Sistema de Emails (AWS SES)

El sistema utiliza **Amazon Simple Email Service (SES)** para:

- ✉️ Envío de emails de verificación de cuenta
- 🔐 Códigos de verificación de 6 dígitos
- 🔄 Recuperación de contraseña

### Configuración
```env
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
AWS_SES_SENDER_EMAIL=noreply@tudominio.com
```

### Modo Desarrollo
```env
SKIP_EMAIL_VERIFICATION=1  # Simula envío de emails
```

---

## 🗺️ Mapa Interactivo (mapa.html)

Interfaz web que visualiza todos los reportes en un mapa usando:

- **Leaflet.js** - Biblioteca de mapas interactivos
- **OpenStreetMap** - Tiles del mapa
- **Bootstrap** - Estilos responsivos

### Funcionalidades
- Marcadores agrupados por ubicación
- Popups con información y foto del reporte
- Actualización automática cada 30 segundos
- Estadísticas en tiempo real
- Galería de últimas 5 fotos
  
<img width="1895" height="950" alt="image" src="https://github.com/user-attachments/assets/579685ad-a1e3-4206-9f1e-6f70179700da" />

---

## 🔗 Articulación con Otros Componentes

### ← Desde ESP32-CAM
```
ESP32 → POST http://18.116.117.140:8000/procesar-imagen
        {
          "foto_base64": "...",
          "timestamp": "2025-MM-DDTHH:mm:ss",
          "latitud": float,
          "longitud": float,
          "lugar_id": "string"
        }
```

### ← Desde App Flutter
```
Flutter → POST http://API_URL/reportes/
          {
            "latitud": float,
            "longitud": float,
            "timestamp": "ISO8601",
            "foto_base64": "...",
            "descripcion": "...",
            "tipo_reporte": "Eventos Culturales|Deportivos|Daños|..."
          }
```

### → Hacia Base de Datos
Toda la información se almacena en MySQL con las imágenes guardadas en disco (`/imagenes_reportes/`).

---

## ⚙️ Configuración y Despliegue

### Variables de Entorno (.env)
```env
# Base de datos
DB_HOST=localhost
DB_PORT=3306
DB_NAME=reportes_gps
DB_USER=usuario
DB_PASSWORD=contraseña

# AWS SES
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
AWS_SES_SENDER_EMAIL=noreply@tudominio.com

# Servidor de imágenes (mainIMG.py)
API_PRINCIPAL_URL=http://3.148.29.34
MODELO_YOLO=yolov8n.pt
CONFIANZA_MIN=0.45
```

### Instalación
```bash
# API Principal
pip install -r requirements.txt
python init_db.py
uvicorn main:app --host 0.0.0.0 --port 5000

# Servidor de Imágenes
pip install -r requirements_img.txt
uvicorn mainIMG:app --host 0.0.0.0 --port 8000
```

---

## 📊 Tipos de Reportes Soportados

| Tipo                           | Descripción                                    |
|--------------------------------|------------------------------------------------|
| `Daños en Planta Urbanisticas` | Daños en infraestructura urbana                |
| `Eventos Culturales`           | Eventos con fechas de inicio/fin               |
| `Eventos Deportivos`           | Eventos deportivos con programación            |
| `Incidentes de Seguridad`      | Reportes de seguridad ciudadana                |
| `Aforo`                        | Conteo automático de personas (ESP32+YOLO)     |

---

## 🔒 Seguridad

- Contraseñas hasheadas con SHA-256
- Validación de emails con regex
- Tokens UUID únicos para verificación
- Códigos de 6 dígitos con expiración de 15 minutos
- CORS configurado para acceso controlado

---

*Última actualización: Marzo 2026*
