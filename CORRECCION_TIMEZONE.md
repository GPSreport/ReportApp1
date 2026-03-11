# Corrección de Zona Horaria - Timestamps de Reportes

## 🐛 Problema Identificado

Los timestamps de los reportes **NO se estaban guardando correctamente en la zona horaria de Bogotá** en la base de datos MySQL.

### Análisis de la Cadena de Envío

1. **App Móvil (main.dart - línea 842)**:
   ```dart
   final timestamp = DateTime.now().toIso8601String();
   ```
   - Enviaba `DateTime.now()` que usa la **hora local del dispositivo**
   - No especificaba zona horaria explícita

2. **Backend API (main.py - líneas 1254-1260)**:
   ```python
   if temp_time.tzinfo is None:
       current_time = temp_time.replace(tzinfo=ZoneInfo("UTC")).astimezone(ZoneInfo("America/Bogota"))
   ```
   - **ERROR**: Asumía que timestamps sin timezone info eran UTC
   - Aplicaba conversión incorrecta: interpretaba hora local como UTC y convertía a Bogotá
   - **Ejemplo del bug**: 
     - Dispositivo en Bogotá envía: `2025-12-04T10:00:00` (hora local)
     - Backend lo interpreta como: `2025-12-04T10:00:00 UTC`
     - Backend lo convierte a Bogotá: `2025-12-04T05:00:00` (UTC-5)
     - **Resultado**: 5 horas de diferencia incorrecta

3. **Base de Datos MySQL**:
   - Recibía timestamps con 5 horas de diferencia
   - Columna `timestamp` tipo `DATETIME` (sin timezone)

## ✅ Solución Implementada

### 1. Cambios en App Móvil (`main.dart`)

**Antes:**
```dart
final timestamp = DateTime.now().toIso8601String();
```

**Después:**
```dart
// Obtener timestamp actual en zona horaria de Bogotá (UTC-5)
final now = DateTime.now();
final bogotaOffset = const Duration(hours: -5);
final bogotaTime = now.toUtc().add(bogotaOffset);
final timestamp = bogotaTime.toIso8601String();
```

**Proceso:**
1. Obtiene hora actual del dispositivo
2. Convierte a UTC
3. Aplica offset de Bogotá (UTC-5)
4. Envía timestamp en hora de Bogotá sin información de timezone

**Aplica también a fechas de eventos:**
```dart
if (_fechaInicioEvento != null) {
  final inicioUtc = _fechaInicioEvento!.toUtc();
  final inicioBogota = inicioUtc.add(bogotaOffset);
  data['fecha_inicio_evento'] = inicioBogota.toIso8601String();
}
```

### 2. Cambios en Backend API (`main.py`)

**Antes:**
```python
if temp_time.tzinfo is None:
    # INCORRECTO: asume UTC
    current_time = temp_time.replace(tzinfo=ZoneInfo("UTC")).astimezone(ZoneInfo("America/Bogota"))
```

**Después:**
```python
if temp_time.tzinfo is not None:
    # Si tiene timezone, convertir a Bogotá
    current_time = temp_time.astimezone(ZoneInfo("America/Bogota")).replace(tzinfo=None)
else:
    # Si no tiene timezone, ya viene en hora de Bogotá desde la app
    current_time = temp_time
```

**Lógica corregida:**
- Si el timestamp tiene información de timezone → convertir a Bogotá
- Si no tiene timezone info → usar directamente (ya viene en hora de Bogotá)
- Siempre remover timezone info antes de guardar en MySQL (`replace(tzinfo=None)`)

## 🔄 Flujo Corregido

```
📱 App Móvil (cualquier timezone)
    ↓
    1. DateTime.now() → hora local dispositivo
    ↓
    2. .toUtc() → convertir a UTC
    ↓
    3. .add(Duration(hours: -5)) → aplicar offset Bogotá
    ↓
    4. .toIso8601String() → "2025-12-04T10:00:00.000"
    ↓
🌐 HTTP POST /reportes/
    ↓
🐍 Backend Python
    ↓
    5. datetime.fromisoformat() → parsear timestamp
    ↓
    6. Si no tiene tzinfo → usar directamente (hora Bogotá)
    ↓
    7. Si tiene tzinfo → convertir a Bogotá
    ↓
💾 MySQL Database
    ↓
    8. Guardar en columna DATETIME → "2025-12-04 10:00:00"
```

## 📊 Ejemplo Comparativo

### Escenario: Usuario en Bogotá crea reporte a las 10:00 AM

| Componente | Antes (❌ Bug) | Después (✅ Correcto) |
|------------|----------------|----------------------|
| Dispositivo | 10:00 AM | 10:00 AM |
| App envía | `2025-12-04T10:00:00` | `2025-12-04T10:00:00` |
| Backend interpreta | 10:00 AM UTC | 10:00 AM Bogotá |
| Backend convierte | 10:00 UTC → 05:00 Bogotá | N/A (ya está en Bogotá) |
| MySQL guarda | `2025-12-04 05:00:00` ❌ | `2025-12-04 10:00:00` ✅ |
| **Diferencia** | **-5 horas** | **Correcto** |

## 🚀 Deployment

### 1. Backend
```bash
# Copiar main.py al servidor
scp -i "KeyServer1.pem" main.py ubuntu@3.148.29.34:/home/ubuntu/reportes-gps-api/

# Reiniciar servicio
ssh -i "KeyServer1.pem" ubuntu@3.148.29.34
sudo systemctl restart reportes-api
sudo systemctl status reportes-api
```

### 2. App Móvil
```bash
# En el directorio de la app Flutter
cd gps_reporter
flutter clean
flutter pub get
flutter build apk --release

# El APK estará en:
# build/app/outputs/flutter-apk/app-release.apk
```

### 3. Verificación
```bash
# Ver logs del backend
sudo journalctl -u reportes-api -f

# Crear un reporte de prueba desde la app
# Verificar en MySQL:
mysql -u admin -p gps_reportes
SELECT id, timestamp, tipo_reporte FROM reportes ORDER BY id DESC LIMIT 5;

# La hora debe coincidir con la hora actual de Bogotá
```

## 🧪 Pruebas Recomendadas

1. **Prueba básica**: Crear reporte y verificar que el timestamp en BD = hora actual Bogotá
2. **Prueba de eventos**: Crear evento con fechas futuras y verificar que se guardan correctamente
3. **Prueba multi-dispositivo**: Probar desde dispositivos en diferentes zonas horarias
4. **Prueba histórica**: Verificar que reportes antiguos se muestran correctamente en el mapa

## 📝 Notas Técnicas

- **MySQL DATETIME**: No almacena información de timezone, asume hora local
- **ZoneInfo**: Requiere Python 3.9+ (usando IANA timezone database)
- **UTC-5**: Bogotá está permanentemente en UTC-5 (sin horario de verano)
- **ISO 8601**: Formato estándar `YYYY-MM-DDTHH:mm:ss.sss` sin sufijo 'Z'

## 🔍 Validación del Fix

Para confirmar que la corrección funciona:

```python
# Script de prueba (test_timezone.py)
from datetime import datetime
from zoneinfo import ZoneInfo

# Simular timestamp desde app (sin timezone)
timestamp_from_app = "2025-12-04T10:00:00.000"
dt = datetime.fromisoformat(timestamp_from_app)

print(f"Timestamp recibido: {dt}")
print(f"Tiene timezone: {dt.tzinfo is not None}")

# Aplicar lógica corregida
if dt.tzinfo is not None:
    current_time = dt.astimezone(ZoneInfo("America/Bogota")).replace(tzinfo=None)
else:
    current_time = dt  # Ya viene en hora de Bogotá

print(f"Timestamp a guardar en MySQL: {current_time}")
# Debe mostrar: 2025-12-04 10:00:00 ✅
```

## 🎯 Impacto de la Corrección

- ✅ Reportes se guardan con timestamp correcto de Bogotá
- ✅ Eventos culturales/deportivos muestran fechas correctas
- ✅ Filtro de eventos de 12 horas funciona correctamente
- ✅ Mapa web muestra información temporal precisa
- ✅ Estadísticas de reportes por día/semana son precisas

---

**Fecha de corrección**: 4 de diciembre de 2025  
**Archivos modificados**: 
- `main.py` (líneas 1247-1264)
- `main.dart` (líneas 841-876)
