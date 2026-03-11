# 🔧 Instrucciones para MySQL Workbench

## 📝 Modificaciones Manuales en la Base de Datos

### 🎯 Opción 1: Agregar Columnas SIN Borrar Datos (RECOMENDADO)

#### Paso 1: Conectar a la Base de Datos

1. Abre **MySQL Workbench**
2. Haz clic en tu conexión a la base de datos (ej: `gps_reportes @ 3.148.29.34`)
3. Ingresa la contraseña cuando se solicite
4. Espera a que se establezca la conexión

#### Paso 2: Seleccionar la Base de Datos

En el panel de consultas SQL, escribe:

```sql
USE gps_reportes;
```

Presiona el ícono de **rayo ⚡** (Execute) o presiona `Ctrl + Enter`

#### Paso 3: Verificar Estructura Actual

Ejecuta este comando para ver las columnas actuales:

```sql
DESCRIBE reportes;
```

**Resultado esperado:**
```
+---------------+---------------+------+-----+-------------------+
| Field         | Type          | Null | Key | Default           |
+---------------+---------------+------+-----+-------------------+
| id            | int           | NO   | PRI | NULL              |
| latitud       | decimal(10,8) | NO   |     | NULL              |
| longitud      | decimal(11,8) | NO   |     | NULL              |
| timestamp     | datetime      | NO   |     | NULL              |
| foto_base64   | longtext      | NO   |     | NULL              |
| descripcion   | text          | YES  |     | NULL              |
| tipo_reporte  | varchar(50)   | YES  |     | general           |
| created_at    | timestamp     | YES  |     | CURRENT_TIMESTAMP |
+---------------+---------------+------+-----+-------------------+
```

#### Paso 4: Agregar Columnas para Eventos

Copia y pega el siguiente código en el editor SQL:

```sql
-- Agregar columna para fecha de inicio del evento
ALTER TABLE reportes 
ADD COLUMN fecha_inicio_evento DATETIME NULL 
COMMENT 'Fecha y hora de inicio del evento';

-- Agregar columna para fecha de fin del evento
ALTER TABLE reportes 
ADD COLUMN fecha_fin_evento DATETIME NULL 
COMMENT 'Fecha y hora de fin del evento';
```

Presiona el **rayo ⚡** para ejecutar

**Mensaje esperado:**
```
✓ Affected rows: 0
✓ Records: 0  Duplicates: 0  Warnings: 0
```

#### Paso 5: Verificar que se Agregaron las Columnas

```sql
DESCRIBE reportes;
```

**Resultado esperado (debe incluir las nuevas columnas):**
```
+---------------------+---------------+------+-----+-------------------+
| Field               | Type          | Null | Key | Default           |
+---------------------+---------------+------+-----+-------------------+
| id                  | int           | NO   | PRI | NULL              |
| latitud             | decimal(10,8) | NO   |     | NULL              |
| longitud            | decimal(11,8) | NO   |     | NULL              |
| timestamp           | datetime      | NO   |     | NULL              |
| foto_base64         | longtext      | NO   |     | NULL              |
| descripcion         | text          | YES  |     | NULL              |
| tipo_reporte        | varchar(50)   | YES  |     | general           |
| fecha_inicio_evento | datetime      | YES  |     | NULL              | ⭐ NUEVA
| fecha_fin_evento    | datetime      | YES  |     | NULL              | ⭐ NUEVA
| created_at          | timestamp     | YES  |     | CURRENT_TIMESTAMP |
+---------------------+---------------+------+-----+-------------------+
```

#### Paso 6: Verificar Datos Existentes (Opcional)

```sql
SELECT COUNT(*) as total_reportes FROM reportes;
```

Todos tus reportes anteriores seguirán intactos, solo tendrán `NULL` en las nuevas columnas.

---

## ⚠️ Opción 2: Limpiar Base de Datos (BORRAR TODO)

### ⚠️⚠️⚠️ ADVERTENCIA IMPORTANTE ⚠️⚠️⚠️

**Esta opción ELIMINARÁ todos los reportes existentes de forma PERMANENTE.**
**No hay forma de recuperarlos después.**
**Usa esto SOLO si estás completamente seguro.**

#### Paso 1: Ver Estadísticas Antes de Borrar

```sql
-- Ver total de reportes
SELECT COUNT(*) as total FROM reportes;

-- Ver reportes por tipo
SELECT tipo_reporte, COUNT(*) as cantidad 
FROM reportes 
GROUP BY tipo_reporte;

-- Ver último ID
SELECT MAX(id) as ultimo_id FROM reportes;
```

#### Paso 2: Hacer Backup (RECOMENDADO)

Antes de borrar, haz un respaldo:

```sql
-- Crear tabla de backup
CREATE TABLE reportes_backup AS SELECT * FROM reportes;

-- Verificar que se copió todo
SELECT COUNT(*) FROM reportes_backup;
```

#### Paso 3: Eliminar Todos los Registros

```sql
-- ⚠️ ESTO BORRARÁ TODO ⚠️
DELETE FROM reportes;
```

**Mensaje esperado:**
```
✓ Affected rows: [número de registros borrados]
```

#### Paso 4: Reiniciar Contador AUTO_INCREMENT

```sql
-- Reiniciar el ID a 1
ALTER TABLE reportes AUTO_INCREMENT = 1;
```

**Mensaje esperado:**
```
✓ Affected rows: 0
✓ Records: 0  Duplicates: 0  Warnings: 0
```

#### Paso 5: Verificar que Está Vacía

```sql
-- Debe retornar 0
SELECT COUNT(*) FROM reportes;

-- Ver el próximo ID (debe ser 1)
SHOW TABLE STATUS LIKE 'reportes';
```

En la columna `Auto_increment` debe aparecer **1**.

#### Paso 6: Probar Inserción

```sql
-- Insertar un reporte de prueba
INSERT INTO reportes (
    latitud, 
    longitud, 
    timestamp, 
    foto_base64, 
    descripcion, 
    tipo_reporte,
    fecha_inicio_evento,
    fecha_fin_evento
) VALUES (
    10.9639,
    -74.7964,
    NOW(),
    'imagenes_reportes/test.jpg',
    'Reporte de prueba',
    'Eventos Culturales',
    '2025-12-15 18:00:00',
    '2025-12-15 23:00:00'
);

-- Verificar que se insertó con ID = 1
SELECT * FROM reportes;
```

**Resultado esperado:**
El reporte debe tener `id = 1`

---

## 🔍 Consultas Útiles Después de las Modificaciones

### Ver Todos los Eventos con Fechas

```sql
SELECT 
    id,
    tipo_reporte,
    descripcion,
    fecha_inicio_evento,
    fecha_fin_evento,
    timestamp as fecha_creacion
FROM reportes
WHERE tipo_reporte IN ('Eventos Culturales', 'Eventos Deportivos')
ORDER BY fecha_inicio_evento ASC;
```

### Ver Eventos Activos (En Curso Ahora)

```sql
SELECT 
    id,
    tipo_reporte,
    descripcion,
    fecha_inicio_evento,
    fecha_fin_evento
FROM reportes
WHERE tipo_reporte IN ('Eventos Culturales', 'Eventos Deportivos')
  AND NOW() BETWEEN fecha_inicio_evento AND fecha_fin_evento;
```

### Ver Próximos Eventos (Futuros)

```sql
SELECT 
    id,
    tipo_reporte,
    descripcion,
    fecha_inicio_evento,
    TIMESTAMPDIFF(DAY, NOW(), fecha_inicio_evento) as dias_faltantes
FROM reportes
WHERE tipo_reporte IN ('Eventos Culturales', 'Eventos Deportivos')
  AND fecha_inicio_evento > NOW()
ORDER BY fecha_inicio_evento ASC;
```

### Ver Eventos de Esta Semana

```sql
SELECT 
    id,
    tipo_reporte,
    descripcion,
    DATE_FORMAT(fecha_inicio_evento, '%W %d de %M') as fecha_formateada,
    DATE_FORMAT(fecha_inicio_evento, '%H:%i') as hora_inicio
FROM reportes
WHERE tipo_reporte IN ('Eventos Culturales', 'Eventos Deportivos')
  AND YEARWEEK(fecha_inicio_evento) = YEARWEEK(NOW())
ORDER BY fecha_inicio_evento ASC;
```

### Ver Reportes que NO son Eventos

```sql
SELECT 
    id,
    tipo_reporte,
    descripcion,
    timestamp,
    fecha_inicio_evento,  -- Debe ser NULL
    fecha_fin_evento      -- Debe ser NULL
FROM reportes
WHERE tipo_reporte NOT IN ('Eventos Culturales', 'Eventos Deportivos')
ORDER BY timestamp DESC
LIMIT 10;
```

### Contar Reportes por Tipo

```sql
SELECT 
    tipo_reporte,
    COUNT(*) as total,
    SUM(CASE WHEN fecha_inicio_evento IS NOT NULL THEN 1 ELSE 0 END) as con_fechas
FROM reportes
GROUP BY tipo_reporte
ORDER BY total DESC;
```

---

## 🎨 Actualizar Datos Existentes (Opcional)

Si ya tienes reportes de eventos y quieres agregarles fechas manualmente:

```sql
-- Actualizar un evento específico
UPDATE reportes
SET 
    fecha_inicio_evento = '2025-12-15 18:00:00',
    fecha_fin_evento = '2025-12-15 23:00:00'
WHERE id = 123  -- Reemplaza con el ID del reporte
  AND tipo_reporte IN ('Eventos Culturales', 'Eventos Deportivos');

-- Verificar el cambio
SELECT * FROM reportes WHERE id = 123;
```

---

## 🔒 Restaurar desde Backup

Si hiciste backup y quieres restaurar los datos:

```sql
-- Ver cuántos registros hay en el backup
SELECT COUNT(*) FROM reportes_backup;

-- Restaurar todos los datos
INSERT INTO reportes 
SELECT * FROM reportes_backup;

-- Verificar
SELECT COUNT(*) FROM reportes;

-- Borrar el backup (opcional)
DROP TABLE reportes_backup;
```

---

## 📊 Panel de Estado en Workbench

### Crear Vista para Monitoreo

```sql
CREATE OR REPLACE VIEW vista_eventos AS
SELECT 
    id,
    tipo_reporte,
    descripcion,
    fecha_inicio_evento,
    fecha_fin_evento,
    CASE
        WHEN NOW() < fecha_inicio_evento THEN '🔜 Próximo'
        WHEN NOW() BETWEEN fecha_inicio_evento AND fecha_fin_evento THEN '🔴 En Curso'
        WHEN NOW() > fecha_fin_evento THEN '✅ Finalizado'
        ELSE '❓ Sin Fecha'
    END as estado,
    TIMESTAMPDIFF(HOUR, fecha_inicio_evento, fecha_fin_evento) as duracion_horas
FROM reportes
WHERE tipo_reporte IN ('Eventos Culturales', 'Eventos Deportivos');

-- Usar la vista
SELECT * FROM vista_eventos ORDER BY fecha_inicio_evento;
```

---

## 🐛 Solución de Problemas

### Error: "Table 'reportes' doesn't exist"

```sql
-- Verificar que estás en la base de datos correcta
SELECT DATABASE();

-- Cambiar a la base de datos correcta
USE gps_reportes;
```

### Error: "Duplicate column name 'fecha_inicio_evento'"

Las columnas ya existen. Verifica con:

```sql
DESCRIBE reportes;
```

### Error: "Access denied"

Verifica que tu usuario tenga permisos:

```sql
-- Ver permisos actuales
SHOW GRANTS;

-- Si necesitas permisos de ALTER
-- (ejecutar como root o admin)
GRANT ALTER ON gps_reportes.* TO 'tu_usuario'@'%';
FLUSH PRIVILEGES;
```

---

## ✅ Checklist Final

Después de hacer las modificaciones:

- [ ] ✓ Columnas agregadas correctamente
- [ ] ✓ Estructura de tabla verificada con `DESCRIBE`
- [ ] ✓ Datos existentes preservados (si elegiste Opción 1)
- [ ] ✓ Consultas de prueba ejecutadas exitosamente
- [ ] ✓ Backend actualizado en el servidor
- [ ] ✓ App Flutter recompilada
- [ ] ✓ Prueba end-to-end realizada

---

## 📞 Comandos de Referencia Rápida

```sql
-- Conexión
USE gps_reportes;

-- Ver estructura
DESCRIBE reportes;

-- Agregar columnas
ALTER TABLE reportes 
ADD COLUMN fecha_inicio_evento DATETIME NULL,
ADD COLUMN fecha_fin_evento DATETIME NULL;

-- Ver datos
SELECT * FROM reportes ORDER BY id DESC LIMIT 10;

-- Estadísticas
SELECT COUNT(*) FROM reportes;
SELECT tipo_reporte, COUNT(*) FROM reportes GROUP BY tipo_reporte;

-- Limpiar (⚠️ PELIGROSO)
DELETE FROM reportes;
ALTER TABLE reportes AUTO_INCREMENT = 1;
```

---

## 🎓 Tips de MySQL Workbench

1. **Ejecutar solo una línea**: Selecciona la línea y presiona `Ctrl + Shift + Enter`
2. **Ejecutar todo**: Presiona el ícono del rayo ⚡ o `Ctrl + Enter`
3. **Comentar líneas**: Selecciona y presiona `Ctrl + /`
4. **Autocompletar**: Presiona `Ctrl + Space`
5. **Historial de consultas**: Ve a `Query` > `Query History`
6. **Exportar resultados**: Click derecho en resultados > `Export`

---

**✨ Todo listo para usar desde MySQL Workbench ✨**

**Última actualización**: 4 de diciembre de 2025
