# Debug: Fechas de Eventos No se Guardan en Base de Datos

## 🔍 Problema Reportado

Las columnas `fecha_inicio_evento` y `fecha_fin_evento` están vacías (NULL) en la base de datos, a pesar de haber creado un reporte de evento de prueba.

## 🛠️ Cambios Realizados para Debug

### 1. Backend (`main.py`)

Se agregó logging detallado en el endpoint `/reportes/` para ver:
- Qué tipo de reporte se recibe
- Si las fechas vienen en el payload JSON
- Si se procesan correctamente
- Valores finales que se guardan en MySQL

**Ubicación**: Líneas ~1295-1335

```python
# Debug: Imprimir tipo de reporte recibido
print(f"📋 Tipo de reporte recibido: '{reporte.tipo_reporte}'")
print(f"   fecha_inicio_evento: {reporte.fecha_inicio_evento}")
print(f"   fecha_fin_evento: {reporte.fecha_fin_evento}")
```

### 2. App Móvil (`main.dart`)

Se agregó logging detallado en `_sendDataToServer()` para ver:
- Tipo de reporte seleccionado
- Estado de las variables de fecha
- Si se agregan al payload
- Payload completo antes de enviar

**Ubicación**: Líneas ~867-900

```dart
debugPrint('📋 Tipo de reporte: $_tipoReporte');
debugPrint('   Fecha inicio evento: $_fechaInicioEvento');
debugPrint('   Fecha fin evento: $_fechaFinEvento');
```

## 🧪 Pasos para Diagnosticar el Problema

### Opción A: Verificar desde la App Móvil

1. **Abrir la app en modo debug** (desde Android Studio o VS Code)

2. **Crear un reporte de evento**:
   ```
   - Iniciar sesión
   - Cambiar tipo de reporte a "Eventos Culturales" o "Eventos Deportivos"
   - IMPORTANTE: Seleccionar fecha y hora de inicio
   - IMPORTANTE: Seleccionar fecha y hora de fin
   - Agregar ubicación
   - Enviar reporte
   ```

3. **Revisar logs en la consola** (buscar los mensajes con emojis):
   ```
   📋 Tipo de reporte: Eventos Culturales
      Fecha inicio evento: 2025-12-10 10:00:00.000
      Fecha fin evento: 2025-12-10 18:00:00.000
   ✓ Es un evento cultural/deportivo
     ✅ Agregando fecha_inicio_evento: 2025-12-10T15:00:00.000
     ✅ Agregando fecha_fin_evento: 2025-12-10T23:00:00.000
   📤 Datos a enviar: {"latitud":...,"fecha_inicio_evento":"..."}
   ```

4. **Posibles escenarios**:

   **Escenario 1**: Las fechas son NULL en la app
   ```
   ⚠️  fecha_inicio_evento es null
   ⚠️  fecha_fin_evento es null
   ```
   **Causa**: El usuario NO seleccionó las fechas
   **Solución**: Asegurarse de tocar los selectores de fecha/hora

   **Escenario 2**: El tipo de reporte no coincide
   ```
   ✗ No es un evento cultural/deportivo, no se agregan fechas
   ```
   **Causa**: El tipo de reporte seleccionado no es exactamente "Eventos Culturales" o "Eventos Deportivos"
   **Solución**: Verificar opciones del dropdown

   **Escenario 3**: Las fechas se agregan correctamente
   ```
   ✅ Agregando fecha_inicio_evento: 2025-12-10T15:00:00.000
   ✅ Agregando fecha_fin_evento: 2025-12-10T23:00:00.000
   ```
   **Resultado**: El problema está en el backend

### Opción B: Verificar desde el Backend

1. **Conectarse al servidor**:
   ```bash
   ssh -i "KeyServer1.pem" ubuntu@3.148.29.34
   ```

2. **Ver logs del servicio en tiempo real**:
   ```bash
   sudo journalctl -u reportes-api -f
   ```

3. **Desde la app, crear un reporte de evento**

4. **Revisar logs del backend** (buscar mensajes con emojis):
   ```
   📋 Tipo de reporte recibido: 'Eventos Culturales'
      fecha_inicio_evento: 2025-12-10T15:00:00.000
      fecha_fin_evento: 2025-12-10T23:00:00.000
   ✓ Es un evento cultural/deportivo, procesando fechas...
     ✅ fecha_inicio procesada: 2025-12-10 10:00:00
     ✅ fecha_fin procesada: 2025-12-10 18:00:00
   ```

5. **Posibles escenarios**:

   **Escenario 1**: Las fechas NO llegan al backend
   ```
   📋 Tipo de reporte recibido: 'Eventos Culturales'
      fecha_inicio_evento: None
      fecha_fin_evento: None
   ⚠️  fecha_inicio_evento es None/vacía
   ⚠️  fecha_fin_evento es None/vacía
   ```
   **Causa**: La app no está enviando las fechas (ver Opción A)

   **Escenario 2**: El tipo de reporte no coincide
   ```
   📋 Tipo de reporte recibido: 'Evento Cultural'  ← ¡sin 's'!
   ✗ No es un evento, tipo_reporte no coincide
   ```
   **Causa**: Hay una diferencia en la cadena de texto
   **Solución**: Corregir el valor exacto en app o backend

   **Escenario 3**: Error al procesar fechas
   ```
   ✓ Es un evento cultural/deportivo, procesando fechas...
   ❌ Error procesando fecha_inicio_evento: ...
   ```
   **Causa**: Formato de fecha inválido
   **Solución**: Revisar conversión de timezone

### Opción C: Verificar en la Base de Datos

1. **Conectarse a MySQL**:
   ```bash
   mysql -u admin -p gps_reportes
   # Contraseña: tu_password
   ```

2. **Verificar estructura de la tabla**:
   ```sql
   DESCRIBE reportes;
   ```
   
   Debe mostrar:
   ```
   +---------------------+--------------+------+-----+---------+
   | Field               | Type         | Null | Key | Default |
   +---------------------+--------------+------+-----+---------+
   | fecha_inicio_evento | datetime     | YES  |     | NULL    |
   | fecha_fin_evento    | datetime     | YES  |     | NULL    |
   +---------------------+--------------+------+-----+---------+
   ```

3. **Ver último reporte creado**:
   ```sql
   SELECT id, tipo_reporte, timestamp, fecha_inicio_evento, fecha_fin_evento 
   FROM reportes 
   ORDER BY id DESC 
   LIMIT 1;
   ```

4. **Ver todos los reportes de eventos con fechas**:
   ```sql
   SELECT id, tipo_reporte, fecha_inicio_evento, fecha_fin_evento
   FROM reportes
   WHERE tipo_reporte IN ('Eventos Culturales', 'Eventos Deportivos')
   ORDER BY id DESC;
   ```

## 🎯 Posibles Causas Raíz

### Causa 1: Usuario no seleccionó las fechas
**Síntoma**: Variables `_fechaInicioEvento` y `_fechaFinEvento` son `null` en la app

**Verificación**:
- Los selectores de fecha/hora se muestran correctamente cuando se selecciona un evento
- El usuario tocó ambos selectores (inicio y fin)
- Las fechas aparecen en los campos (no dice "Seleccionar fecha y hora")

**Solución**:
- Asegurarse de seleccionar ambas fechas antes de enviar

### Causa 2: Las fechas se reinician antes de enviar
**Síntoma**: Las fechas se seleccionan pero luego se ponen a `null`

**Ubicaciones donde se reinician**:
1. Al cambiar tipo de reporte (línea ~1360)
2. Después de enviar exitosamente (línea ~897)

**Verificación**:
- No cambiar el tipo de reporte después de seleccionar las fechas
- Las fechas no deben reiniciarse ANTES del envío

**Solución**:
- Ya está implementado correctamente, solo se reinician DESPUÉS del envío exitoso

### Causa 3: Tipo de reporte no coincide exactamente
**Síntoma**: El if en el backend no se cumple

**Valores esperados** (case-sensitive):
- `"Eventos Culturales"` ✅
- `"Eventos Deportivos"` ✅

**Valores que NO funcionarían**:
- `"Evento Cultural"` ❌ (sin 's')
- `"eventos culturales"` ❌ (minúsculas)
- `"Eventos culturales"` ❌ (primera palabra capitalizada, segunda no)

**Verificación**:
```dart
// En main.dart, buscar el dropdown de tipo_reporte
// Valores deben coincidir EXACTAMENTE
```

**Solución**:
- Asegurar que los valores del dropdown coincidan exactamente

### Causa 4: Conversión de timezone errónea
**Síntoma**: Error al parsear las fechas ISO

**Formato esperado**: `2025-12-10T15:00:00.000`

**Verificación**:
- La app envía ISO 8601 válido
- El backend puede parsear con `datetime.fromisoformat()`

**Solución**:
- Ya está corregido en el código actual

## 📊 Checklist de Verificación

Antes de crear un reporte de evento, verificar:

- [ ] Backend actualizado con código de debug
- [ ] App móvil actualizada con código de debug
- [ ] Usuario inició sesión correctamente
- [ ] Tipo de reporte seleccionado: "Eventos Culturales" o "Eventos Deportivos"
- [ ] **Fecha y hora de INICIO seleccionadas** (no dice "Seleccionar fecha y hora")
- [ ] **Fecha y hora de FIN seleccionadas** (no dice "Seleccionar fecha y hora")
- [ ] Fecha fin es posterior a fecha inicio
- [ ] Ubicación obtenida correctamente
- [ ] Logs activados (consola de debug para app, journalctl para backend)

## 🚀 Deployment de Cambios de Debug

### Backend
```bash
# Copiar main.py actualizado
scp -i "KeyServer1.pem" main.py ubuntu@3.148.29.34:/home/ubuntu/reportes-gps-api/

# Reiniciar servicio
ssh -i "KeyServer1.pem" ubuntu@3.148.29.34
sudo systemctl restart reportes-api

# Ver logs
sudo journalctl -u reportes-api -f
```

### App Móvil
```bash
# Ejecutar en modo debug desde Android Studio/VS Code
flutter run

# O generar APK debug
flutter build apk --debug
# APK: build/app/outputs/flutter-apk/app-debug.apk
```

## 📝 Próximos Pasos

1. **Desplegar código con debug** en backend y app
2. **Crear reporte de evento de prueba** siguiendo el checklist
3. **Revisar logs** tanto en app como backend
4. **Identificar** en qué punto del flujo las fechas se pierden
5. **Reportar hallazgos** con capturas de logs
6. **Aplicar corrección** específica según la causa identificada

---

**Fecha de creación**: 4 de diciembre de 2025  
**Archivos modificados**:
- `main.py` (logging de debug en endpoint /reportes/)
- `main.dart` (logging de debug en _sendDataToServer())
- `test_fechas_eventos.py` (script de prueba standalone)
