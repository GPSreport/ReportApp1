# 🎯 RESUMEN RÁPIDO - Implementación de Fechas para Eventos

## ✅ Archivos Modificados

### Backend (Python/FastAPI)
- ✏️ `main.py` - Modelos y endpoints actualizados

### Frontend (Flutter/Dart)  
- ✏️ `main.dart` - UI con selectores de fecha/hora

## 📁 Archivos SQL Creados

1. **actualizar_tabla_eventos.sql** *(Seguro - No borra datos)*
   ```sql
   ALTER TABLE reportes 
   ADD COLUMN fecha_inicio_evento DATETIME NULL,
   ADD COLUMN fecha_fin_evento DATETIME NULL;
   ```

2. **LIMPIAR_BASE_DATOS.sql** *(⚠️ PELIGROSO - Borra todo)*
   ```sql
   DELETE FROM reportes;
   ALTER TABLE reportes AUTO_INCREMENT = 1;
   ```

## 🐍 Script Python Creado

- **gestionar_db.py** - Herramienta interactiva para:
  - Ver estadísticas de la DB
  - Agregar columnas automáticamente
  - Limpiar DB de forma segura con confirmación

## 🚀 Cómo Usar (Inicio Rápido)

### 1️⃣ Actualizar Base de Datos
```bash
# Opción A: Usando el script Python (RECOMENDADO)
python gestionar_db.py
# Seleccionar opción 2: "Agregar columnas de eventos"

# Opción B: Manualmente con SQL
mysql -u root -p gps_reportes < actualizar_tabla_eventos.sql
```

### 2️⃣ Actualizar Backend
```bash
# Subir main.py al servidor
scp -i "key.pem" main.py ubuntu@3.148.29.34:/home/ubuntu/reportes-gps-api/

# Reiniciar servicio
ssh -i "key.pem" ubuntu@3.148.29.34
sudo systemctl restart reportes-api
```

### 3️⃣ Actualizar App Flutter
```bash
cd gps_reporter
flutter run
# o
flutter build apk --release
```

## 📱 Cómo se Ve en la App

### Antes (todos los tipos de reporte):
```
┌─────────────────────────────┐
│ Cámara   Galería            │
└─────────────────────────────┘
```

### Después (solo para eventos):
```
┌─────────────────────────────┐
│ Cámara   Galería            │
├─────────────────────────────┤
│ 📅 Inicio del Evento        │
│    10/12/2025 - 06:00 PM    │
├─────────────────────────────┤
│ ⏰ Fin del Evento           │
│    10/12/2025 - 11:00 PM    │
└─────────────────────────────┘
```

## 🎨 Lógica de Visualización

| Tipo de Reporte              | Selectores Visibles |
|------------------------------|---------------------|
| Daños en Planta Urbanísticas | ❌ No               |
| **Eventos Culturales**       | ✅ **Sí**           |
| **Eventos Deportivos**       | ✅ **Sí**           |
| Obras en Proceso             | ❌ No               |

## 🔄 Flujo de Datos

```
Flutter App
    ↓ (Selecciona fecha/hora)
    ↓ (Convierte a ISO 8601)
    ↓
FastAPI Backend
    ↓ (Recibe "2025-12-10T18:00:00")
    ↓ (Convierte a Bogotá UTC-5)
    ↓ (Guarda como DATETIME)
    ↓
MySQL Database
    ↓ (Almacena: 2025-12-10 18:00:00)
```

## 📊 Estructura de Tabla Actualizada

```sql
CREATE TABLE reportes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    latitud DECIMAL(10, 8) NOT NULL,
    longitud DECIMAL(11, 8) NOT NULL,
    timestamp DATETIME NOT NULL,
    foto_base64 LONGTEXT NOT NULL,
    descripcion TEXT,
    tipo_reporte VARCHAR(50) DEFAULT 'general',
    fecha_inicio_evento DATETIME NULL,  -- ⭐ NUEVA
    fecha_fin_evento DATETIME NULL,     -- ⭐ NUEVA
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 🧪 Prueba Rápida

### Desde la App:
1. Login
2. Tipo: "Eventos Culturales"
3. Seleccionar inicio: 10/12/2025 6:00 PM
4. Seleccionar fin: 10/12/2025 11:00 PM
5. Tomar foto
6. Enviar

### Verificar en MySQL:
```sql
SELECT 
    id, 
    tipo_reporte, 
    fecha_inicio_evento, 
    fecha_fin_evento 
FROM reportes 
ORDER BY id DESC 
LIMIT 1;
```

### Resultado Esperado:
```
+----+-------------------+---------------------+---------------------+
| id | tipo_reporte      | fecha_inicio_evento | fecha_fin_evento    |
+----+-------------------+---------------------+---------------------+
|  1 | Eventos Culturales| 2025-12-10 18:00:00 | 2025-12-10 23:00:00 |
+----+-------------------+---------------------+---------------------+
```

## ⚡ Comandos Más Usados

```bash
# Ver logs del backend
sudo journalctl -u reportes-api -f

# Reiniciar backend
sudo systemctl restart reportes-api

# Conectar a MySQL
mysql -u root -p gps_reportes

# Hot reload Flutter
flutter run

# Ver estadísticas DB
python gestionar_db.py
```

## 🐛 Problemas Comunes

| Problema | Solución |
|----------|----------|
| Column doesn't exist | Ejecutar `actualizar_tabla_eventos.sql` |
| No aparecen selectores | Verificar tipo = "Eventos Culturales/Deportivos" |
| Fechas en UTC | Backend ya convierte a Bogotá automáticamente |
| Error 500 al enviar | Revisar logs con `journalctl -u reportes-api -f` |

## 📞 Ayuda

- 📄 Instrucciones completas: `INSTRUCCIONES_ACTUALIZACION_EVENTOS.md`
- 🔧 Script interactivo: `python gestionar_db.py`
- 🗂️ SQL manual: `actualizar_tabla_eventos.sql`

---
✨ **Todo listo para crear eventos con fechas** ✨
