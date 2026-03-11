# 📅 Actualización: Fechas para Eventos Culturales y Deportivos

## 🎯 Cambios Implementados

### 1. Base de Datos (MySQL)
Se agregaron dos nuevas columnas a la tabla `reportes`:
- `fecha_inicio_evento` - Fecha y hora de inicio del evento
- `fecha_fin_evento` - Fecha y hora de finalización del evento

### 2. Backend (FastAPI - main.py)
- ✅ Modelos `ReporteCreate` y `ReporteResponse` actualizados
- ✅ Tabla `reportes` incluye las nuevas columnas
- ✅ Endpoint `/reportes/` POST procesa fechas de eventos
- ✅ Endpoint `/reportes/` GET retorna fechas de eventos
- ✅ Conversión automática a zona horaria de Bogotá

### 3. Aplicación Móvil (Flutter - main.dart)
- ✅ Variables `_fechaInicioEvento` y `_fechaFinEvento` agregadas
- ✅ Selectores de fecha/hora que aparecen solo para eventos
- ✅ UI con DatePicker y TimePicker nativos
- ✅ Formato de fecha: dd/MM/yyyy - hh:mm a
- ✅ Validación: fecha de fin no puede ser anterior a inicio
- ✅ Limpieza automática de fechas al enviar o cambiar tipo de reporte

## 📋 Pasos para Aplicar los Cambios

### PASO 1: Actualizar la Base de Datos

#### Opción A: Solo agregar columnas (RECOMENDADO)
```bash
# Conectarse al servidor
ssh -i "ruta/a/tu/clave.pem" ubuntu@3.148.29.34

# Entrar a MySQL
mysql -u root -p

# Seleccionar la base de datos
USE gps_reportes;

# Ejecutar el script de actualización
source /home/ubuntu/reportes-gps-api/actualizar_tabla_eventos.sql;

# O copiar y pegar directamente:
ALTER TABLE reportes 
ADD COLUMN fecha_inicio_evento DATETIME NULL COMMENT 'Fecha y hora de inicio del evento',
ADD COLUMN fecha_fin_evento DATETIME NULL COMMENT 'Fecha y hora de fin del evento';

# Verificar cambios
DESCRIBE reportes;

exit;
```

#### Opción B: Limpiar base de datos (⚠️ DESTRUCTIVO)
**ADVERTENCIA: Esto eliminará TODOS los reportes existentes**

```bash
# Conectarse al servidor
ssh -i "ruta/a/tu/clave.pem" ubuntu@3.148.29.34

# Entrar a MySQL
mysql -u root -p

# Seleccionar la base de datos
USE gps_reportes;

# Ejecutar script destructivo
source /home/ubuntu/reportes-gps-api/LIMPIAR_BASE_DATOS.sql;

# Verificar
SELECT COUNT(*) FROM reportes;  # Debe retornar 0

exit;
```

### PASO 2: Actualizar el Backend

```bash
# En el servidor (ya conectado por SSH)
cd /home/ubuntu/reportes-gps-api

# Detener el servicio
sudo systemctl stop reportes-api

# Hacer backup del archivo actual
cp main.py main.py.backup

# Subir el nuevo main.py desde tu máquina local
# (Ejecutar esto en tu máquina local, no en el servidor)
# scp -i "ruta/a/tu/clave.pem" main.py ubuntu@3.148.29.34:/home/ubuntu/reportes-gps-api/

# Reiniciar el servicio
sudo systemctl start reportes-api

# Verificar que esté funcionando
sudo systemctl status reportes-api

# Ver logs en tiempo real
sudo journalctl -u reportes-api -f
```

### PASO 3: Actualizar la Aplicación Flutter

```bash
# En tu máquina local, en el directorio del proyecto Flutter
cd gps_reporter

# Verificar que los cambios estén en main.dart

# Compilar e instalar en dispositivo Android conectado
flutter run

# O generar APK para distribución
flutter build apk --release

# El APK estará en: build/app/outputs/flutter-apk/app-release.apk
```

## 🧪 Pruebas

### 1. Probar Backend
```bash
# Crear un reporte de evento con fechas
curl -X POST http://3.148.29.34/reportes/ \
  -H "Content-Type: application/json" \
  -d '{
    "latitud": 10.9639,
    "longitud": -74.7964,
    "tipo_reporte": "Eventos Culturales",
    "descripcion": "Festival de música",
    "foto_base64": "",
    "fecha_inicio_evento": "2025-12-10T18:00:00",
    "fecha_fin_evento": "2025-12-10T23:00:00"
  }'

# Obtener reportes y verificar fechas
curl http://3.148.29.34/reportes/ | jq
```

### 2. Probar App Móvil
1. Abrir la app
2. Iniciar sesión
3. Seleccionar tipo de reporte: **"Eventos Culturales"** o **"Eventos Deportivos"**
4. Verificar que aparezcan los selectores de fecha
5. Seleccionar fecha/hora de inicio
6. Seleccionar fecha/hora de fin
7. Tomar foto
8. Enviar reporte
9. Verificar en http://reportapp.ddns.net/mapa que el reporte se guardó

### 3. Verificar Base de Datos
```sql
-- Ver últimos reportes con fechas de eventos
SELECT 
    id, 
    tipo_reporte, 
    descripcion,
    fecha_inicio_evento, 
    fecha_fin_evento,
    timestamp
FROM reportes 
WHERE tipo_reporte IN ('Eventos Culturales', 'Eventos Deportivos')
ORDER BY id DESC 
LIMIT 5;
```

## 📁 Archivos SQL Creados

1. **actualizar_tabla_eventos.sql** - Agrega columnas sin borrar datos
2. **LIMPIAR_BASE_DATOS.sql** - ⚠️ Borra todos los registros y reinicia IDs

## 🔧 Comandos Útiles

### Git (Subir cambios al repositorio)
```bash
cd reportes-gps-api
git add main.py actualizar_tabla_eventos.sql LIMPIAR_BASE_DATOS.sql
git commit -m "Agregar soporte para fechas de eventos culturales y deportivos"
git push origin devsec
```

### Verificar servicio en el servidor
```bash
# Ver estado
sudo systemctl status reportes-api

# Ver logs
sudo journalctl -u reportes-api -n 50 --no-pager

# Reiniciar
sudo systemctl restart reportes-api
```

## ⚠️ Notas Importantes

1. **Zona Horaria**: Todas las fechas se convierten automáticamente a Bogotá (UTC-5)
2. **Validación**: La app permite seleccionar fechas futuras (hasta 1 año)
3. **Opcional**: Las fechas solo se guardan si el tipo es "Eventos Culturales" o "Eventos Deportivos"
4. **Formato**: El backend acepta formato ISO 8601 (YYYY-MM-DDTHH:MM:SS)
5. **NULL**: Los reportes que no son eventos tendrán NULL en estas columnas

## 📱 Capturas de UI

Cuando seleccionas **"Eventos Culturales"** o **"Eventos Deportivos"**:
- ✅ Aparecen 2 selectores debajo de los botones de cámara/galería
- 📅 Selector 1: "Inicio del Evento" con icono de calendario
- ⏰ Selector 2: "Fin del Evento" con icono de calendario
- 🎨 Diseño: Cajas con bordes grises, formato dd/MM/yyyy - hh:mm a

## 🐛 Troubleshooting

### Error: Column 'fecha_inicio_evento' doesn't exist
**Solución**: Ejecutar el script `actualizar_tabla_eventos.sql` en MySQL

### La app no muestra los selectores de fecha
**Solución**: Verificar que el código de `main.dart` esté actualizado y recompilar

### Las fechas se guardan en UTC
**Solución**: El backend ya convierte a Bogotá automáticamente

### Error al enviar reporte con fechas
**Solución**: Verificar que el backend esté actualizado y reiniciado

## ✅ Checklist de Implementación

- [ ] Ejecutar script SQL en la base de datos
- [ ] Actualizar main.py en el servidor
- [ ] Reiniciar servicio reportes-api
- [ ] Actualizar main.dart en el proyecto Flutter
- [ ] Recompilar la app Flutter
- [ ] Probar crear evento con fechas
- [ ] Verificar en el mapa web
- [ ] Verificar en la base de datos

---

**Última actualización**: 4 de diciembre de 2025
**Versión**: 1.1.0 - Soporte para fechas de eventos
