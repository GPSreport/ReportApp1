# Corrección de Manejo de Timestamps en Envío de Reportes

**Fecha**: 4 de diciembre de 2025  
**Archivos modificados**:
- `gps_reporter/lib/main.dart` (App móvil)
- `reportes-gps-api/main.py` (Backend)

---

## 🔍 Problemas Identificados

### 1. **Conversión de Timezone Redundante e Incorrecta**

**Problema en `main.dart`**:
```dart
// ❌ ANTES - Conversión confusa y redundante
final now = DateTime.now();
final bogotaOffset = const Duration(hours: -5);
final bogotaTime = now.toUtc().add(bogotaOffset);
```

**Explicación del error**:
- `DateTime.now()` ya retorna la hora local del dispositivo
- Convertir a UTC y luego sumar -5 horas NO garantiza hora de Bogotá
- Ignora el timezone real del dispositivo configurado por el usuario

**✅ SOLUCIÓN**:
```dart
// Usar hora local directamente (el usuario debe tener configurado UTC-5)
final now = DateTime.now();
final timestamp = now.toIso8601String().split('.')[0]; // Sin milisegundos
```

### 2. **Backend Intentaba Re-convertir Timestamps**

**Problema en `main.py`**:
```python
# ❌ ANTES - Lógica compleja e innecesaria
if temp_time.tzinfo is not None:
    current_time = temp_time.astimezone(ZoneInfo("America/Bogota"))
else:
    current_time = temp_time
```

**Explicación del error**:
- La app enviaba hora local sin timezone
- El backend intentaba detectar y convertir timezone
- Causaba confusión y errores de interpretación

**✅ SOLUCIÓN**:
```python
# Interpretar directamente como hora de Bogotá (sin conversión)
timestamp_str = reporte.timestamp.replace('Z', '').strip()
current_time = datetime.fromisoformat(timestamp_str)
```

### 3. **Falta de Timeout en Requests HTTP**

**Problema**:
```dart
// ❌ ANTES - Sin timeout, la app podía quedarse esperando indefinidamente
final response = await http.post(Uri.parse(kApiUrl), ...);
```

**✅ SOLUCIÓN**:
```dart
final response = await http.post(
  Uri.parse(kApiUrl),
  headers: {'Content-Type': 'application/json'},
  body: jsonEncode(data),
).timeout(
  const Duration(seconds: 30),
  onTimeout: () {
    throw Exception('Tiempo de espera agotado. Verifica tu conexión a internet.');
  },
);
```

### 4. **Manejo de Errores HTTP Poco Específico**

**Problema**:
```dart
// ❌ ANTES - Mensaje genérico
if (response.statusCode == 200) {
  // success
} else {
  throw Exception("Error del servidor: ${response.statusCode}");
}
```

**✅ SOLUCIÓN**:
```dart
if (response.statusCode == 200) {
  // success
} else {
  // Extraer mensaje de error del servidor
  String errorMsg = "Error del servidor (${response.statusCode})";
  try {
    final errorData = jsonDecode(response.body);
    if (errorData['detail'] != null) {
      errorMsg = errorData['detail'];
    }
  } catch (_) {}
  throw Exception(errorMsg);
}
```

### 5. **Mensajes de Error Genéricos**

**Problema**:
```dart
// ❌ ANTES - Un solo mensaje para todos los errores
catch (e) {
  _showMessage("Error al enviar datos");
}
```

**✅ SOLUCIÓN**:
```dart
catch (e) {
  String errorMessage = "Error al enviar datos";
  
  if (e.toString().contains('SocketException')) {
    errorMessage = "Sin conexión a internet";
  } else if (e.toString().contains('TimeoutException')) {
    errorMessage = "Tiempo de espera agotado";
  } else if (e.toString().contains('FormatException')) {
    errorMessage = "Error en formato de datos";
  } else if (e.toString().contains('Exception: ')) {
    errorMessage = e.toString().split('Exception: ')[1];
  }
  
  _showMessage(errorMessage);
}
```

---

## ✅ Cambios Realizados

### En `main.dart` (`_sendDataToServer()`)

#### 1. Timestamp Principal
```dart
// ✅ NUEVO - Uso directo de hora local
final now = DateTime.now();

final timestamp = '${now.year.toString().padLeft(4, '0')}-'
    '${now.month.toString().padLeft(2, '0')}-'
    '${now.day.toString().padLeft(2, '0')}T'
    '${now.hour.toString().padLeft(2, '0')}:'
    '${now.minute.toString().padLeft(2, '0')}:'
    '${now.second.toString().padLeft(2, '0')}';

debugPrint('🕐 Timestamp generado: $timestamp');
```

#### 2. Fechas de Eventos
```dart
// ✅ NUEVO - Uso directo sin conversión UTC
if (_fechaInicioEvento != null) {
  final inicio = _fechaInicioEvento!; // Ya está en hora local
  final fechaInicioStr = '${inicio.year.toString().padLeft(4, '0')}-'
      '${inicio.month.toString().padLeft(2, '0')}-'
      '${inicio.day.toString().padLeft(2, '0')}T'
      '${inicio.hour.toString().padLeft(2, '0')}:'
      '${inicio.minute.toString().padLeft(2, '0')}:'
      '${inicio.second.toString().padLeft(2, '0')}';
  data['fecha_inicio_evento'] = fechaInicioStr;
}
```

#### 3. Request HTTP con Timeout
```dart
final response = await http.post(
  Uri.parse(kApiUrl),
  headers: {'Content-Type': 'application/json'},
  body: jsonEncode(data),
).timeout(
  const Duration(seconds: 30),
  onTimeout: () {
    throw Exception('Tiempo de espera agotado. Verifica tu conexión a internet.');
  },
);

debugPrint('📥 Respuesta del servidor: ${response.statusCode}');
```

#### 4. Manejo de Errores HTTP Mejorado
```dart
if (response.statusCode == 200) {
  debugPrint('✅ Reporte enviado exitosamente');
  // ... limpiar campos
} else {
  String errorMsg = "Error del servidor (${response.statusCode})";
  try {
    final errorData = jsonDecode(response.body);
    if (errorData['detail'] != null) {
      errorMsg = errorData['detail'];
    }
  } catch (_) {}
  debugPrint('❌ Error del servidor: $errorMsg');
  throw Exception(errorMsg);
}
```

#### 5. Captura de Excepciones Específica
```dart
catch (e) {
  debugPrint('❌ Error en envío de datos: $e');
  
  String errorMessage = "Error al enviar datos";
  
  if (e.toString().contains('SocketException') || e.toString().contains('NetworkException')) {
    errorMessage = "Sin conexión a internet";
  } else if (e.toString().contains('TimeoutException') || e.toString().contains('agotado')) {
    errorMessage = "Tiempo de espera agotado";
  } else if (e.toString().contains('FormatException')) {
    errorMessage = "Error en formato de datos";
  } else if (e.toString().contains('Exception: ')) {
    final parts = e.toString().split('Exception: ');
    if (parts.length > 1) {
      errorMessage = parts[1];
    }
  }
  
  setState(() {
    _statusMessage = errorMessage;
    _isLoading = false;
  });
  _showMessage(errorMessage);
}
```

### En `main.py` (Endpoint `/reportes/`)

#### 1. Procesamiento de Timestamp
```python
# ✅ NUEVO - Interpretación directa sin conversión
if not reporte.timestamp:
    current_time = datetime.now(ZoneInfo("America/Bogota")).replace(tzinfo=None)
    print(f"   ✅ timestamp generado (hora actual Bogotá): {current_time}")
else:
    try:
        # La app envía hora local (Bogotá) sin timezone
        timestamp_str = reporte.timestamp.replace('Z', '').strip()
        current_time = datetime.fromisoformat(timestamp_str)
        print(f"   ✅ timestamp parseado (hora Bogotá): {current_time}")
    except (ValueError, AttributeError) as e:
        print(f"   ⚠️ Error parseando timestamp '{reporte.timestamp}': {e}")
        current_time = datetime.now(ZoneInfo("America/Bogota")).replace(tzinfo=None)
        print(f"   ✅ usando hora actual Bogotá: {current_time}")
```

#### 2. Procesamiento de Fechas de Eventos
```python
if reporte.tipo_reporte in ['Eventos Culturales', 'Eventos Deportivos']:
    print(f"✓ Es un evento cultural/deportivo, procesando fechas...")
    
    if reporte.fecha_inicio_evento:
        try:
            # La app envía hora local (Bogotá) sin timezone
            fecha_inicio_str = reporte.fecha_inicio_evento.replace('Z', '').strip()
            fecha_inicio = datetime.fromisoformat(fecha_inicio_str)
            print(f"  ✅ fecha_inicio procesada (hora Bogotá): {fecha_inicio}")
        except Exception as e:
            print(f"  ❌ Error procesando fecha_inicio_evento '{reporte.fecha_inicio_evento}': {e}")
            fecha_inicio = None
    else:
        print(f"  ⚠️  fecha_inicio_evento es None/vacía")
    
    # Similar para fecha_fin_evento...
```

---

## 🎯 Flujo Correcto de Timestamps

### Escenario: Usuario en Bogotá (UTC-5) envía reporte

#### 1️⃣ **En el Dispositivo Móvil** (main.dart)
```
Hora del dispositivo: 2025-12-04 14:30:00 (configurado en UTC-5)
                       ↓
DateTime.now() retorna: 2025-12-04 14:30:00
                       ↓
Formato ISO sin TZ:    "2025-12-04T14:30:00"
                       ↓
Envío a servidor:      {"timestamp": "2025-12-04T14:30:00", ...}
```

#### 2️⃣ **En el Servidor** (main.py)
```
Recibe:               "2025-12-04T14:30:00"
                       ↓
datetime.fromisoformat("2025-12-04T14:30:00")
                       ↓
Resultado:            datetime(2025, 12, 4, 14, 30, 0)  # sin tzinfo
                       ↓
Guarda en MySQL:      2025-12-04 14:30:00  # DATETIME (hora de Bogotá)
```

#### 3️⃣ **Ventajas de este Enfoque**
- ✅ **Simplicidad**: No hay conversiones complejas
- ✅ **Consistencia**: Toda la aplicación trabaja en hora de Bogotá
- ✅ **Confiabilidad**: Depende de la configuración del usuario
- ✅ **Depuración**: Logs claros y entendibles
- ✅ **Formato correcto**: DATETIME en MySQL sin problemas de timezone

---

## 🧪 Pruebas Recomendadas

### 1. Prueba de Reporte Normal
```bash
# Ejecutar app en debug
flutter run

# Crear reporte:
# - Iniciar sesión
# - Obtener ubicación
# - Seleccionar tipo "Daños en Planta Urbanísticas"
# - Enviar reporte

# Verificar en logs:
# App: 🕐 Timestamp generado: 2025-12-04T14:30:00
#      📤 Datos a enviar: {...}
#      📥 Respuesta del servidor: 200
#      ✅ Reporte enviado exitosamente

# Backend: 🔵 Recibiendo nuevo reporte...
#          ✅ timestamp parseado (hora Bogotá): 2025-12-04 14:30:00
#          ✅ Reporte X guardado exitosamente
```

### 2. Prueba de Evento con Fechas
```bash
# Crear evento cultural:
# - Seleccionar tipo "Eventos Culturales"
# - Fecha inicio: 10 dic 2025 10:00 AM
# - Fecha fin: 10 dic 2025 6:00 PM
# - Enviar

# Verificar en logs:
# App: ✓ Es un evento cultural/deportivo
#      ✅ Agregando fecha_inicio_evento: 2025-12-10T10:00:00
#      ✅ Agregando fecha_fin_evento: 2025-12-10T18:00:00

# Backend: ✓ Es un evento cultural/deportivo, procesando fechas...
#          ✅ fecha_inicio procesada (hora Bogotá): 2025-12-10 10:00:00
#          ✅ fecha_fin procesada (hora Bogotá): 2025-12-10 18:00:00
```

### 3. Prueba de Manejo de Errores

#### Sin conexión a internet
```bash
# Desactivar WiFi/datos móviles
# Intentar enviar reporte
# Verificar mensaje: "Sin conexión a internet"
```

#### Timeout
```bash
# Red muy lenta o servidor caído
# Esperar 30 segundos
# Verificar mensaje: "Tiempo de espera agotado"
```

#### Error del servidor
```bash
# Servidor retorna 400/500
# Verificar mensaje específico del servidor
```

### 4. Verificación en Base de Datos
```sql
-- Último reporte creado
SELECT id, tipo_reporte, timestamp, fecha_inicio_evento, fecha_fin_evento
FROM reportes
ORDER BY id DESC
LIMIT 1;

-- Verificar que timestamp coincide con hora de envío
-- Verificar que fechas de evento son correctas
```

---

## 📋 Checklist de Deployment

### Backend (main.py)
```bash
# 1. Copiar archivo actualizado al servidor
scp -i "KeyServer1.pem" main.py ubuntu@3.148.29.34:/home/ubuntu/reportes-gps-api/

# 2. Reiniciar servicio
ssh -i "KeyServer1.pem" ubuntu@3.148.29.34
sudo systemctl restart reportes-api

# 3. Verificar logs
sudo journalctl -u reportes-api -f

# 4. Prueba rápida
curl -X POST http://3.148.29.34/reportes/ \
  -H "Content-Type: application/json" \
  -d '{
    "latitud": 4.60971,
    "longitud": -74.08175,
    "timestamp": "2025-12-04T14:30:00",
    "foto_base64": "iVBORw0KG...",
    "descripcion": "Prueba timestamp",
    "tipo_reporte": "general"
  }'
```

### App Móvil (main.dart)
```bash
# 1. Compilar APK debug
cd gps_reporter
flutter build apk --debug

# 2. Instalar en dispositivo
flutter install

# O ejecutar directamente
flutter run

# 3. Verificar logs en consola
# Buscar mensajes: 🕐, 📤, 📥, ✅, ❌
```

---

## 🚨 Puntos Importantes

### ⚠️ Prerequisito: Configuración de Timezone del Usuario
- **La app asume que el usuario tiene configurado UTC-5 (Bogotá) en su dispositivo**
- Si el usuario está en otra zona horaria, los timestamps no serán correctos
- **Mejora futura**: Detectar timezone automáticamente o permitir configuración manual

### ⚠️ Formato de Fecha Consistente
- **SIEMPRE usar**: `YYYY-MM-DDTHH:mm:ss` (sin milisegundos, sin timezone)
- **NO usar**: 
  - `YYYY-MM-DDTHH:mm:ss.SSS` (con milisegundos)
  - `YYYY-MM-DDTHH:mm:ssZ` (con 'Z')
  - `YYYY-MM-DDTHH:mm:ss+00:00` (con offset)

### ⚠️ Validación de Datos
- El backend siempre debe validar que el timestamp sea parseable
- Si falla el parseo, usar hora actual como fallback
- Registrar el error en logs para debugging

---

## 📊 Comparación Antes/Después

| Aspecto | ❌ Antes | ✅ Después |
|---------|----------|-------------|
| **Conversión timezone** | Confusa, doble conversión | Directa, sin conversión |
| **Timeout HTTP** | Sin timeout | 30 segundos |
| **Mensajes de error** | Genéricos | Específicos por tipo |
| **Extracción error servidor** | No | Sí, parsea `detail` |
| **Logs de debugging** | Básicos | Detallados con emojis |
| **Complejidad código** | Alta | Baja |
| **Mantenibilidad** | Difícil | Fácil |
| **Confiabilidad** | Media | Alta |

---

## 🔄 Próximos Pasos Sugeridos

1. **Validar en producción** con reportes reales
2. **Monitorear logs** del servidor por 1 semana
3. **Recopilar feedback** de usuarios sobre timestamps
4. **Considerar agregar**:
   - Selector de timezone en configuración de app
   - Validación de formato de fecha en frontend
   - Endpoints de debug para verificar timestamps
5. **Actualizar documentación** de API

---

**Estado**: ✅ Implementado y listo para pruebas  
**Última actualización**: 4 de diciembre de 2025
