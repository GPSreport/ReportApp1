-- Script SQL para agregar columnas de fecha inicio/fin a eventos
-- y limpiar registros antiguos

-- 1. Agregar columnas para eventos (inicio y fin)
ALTER TABLE reportes 
ADD COLUMN fecha_inicio_evento DATETIME NULL COMMENT 'Fecha y hora de inicio del evento',
ADD COLUMN fecha_fin_evento DATETIME NULL COMMENT 'Fecha y hora de fin del evento';

-- 2. (OPCIONAL) Borrar todos los registros antiguos
-- ⚠️ ADVERTENCIA: Esto eliminará TODOS los reportes existentes
-- Descomenta las siguientes líneas solo si estás seguro
-- DELETE FROM reportes;

-- 3. (OPCIONAL) Reiniciar el contador AUTO_INCREMENT
-- Esto hará que el próximo ID sea 1
-- Descomenta la siguiente línea solo si borraste todos los registros
-- ALTER TABLE reportes AUTO_INCREMENT = 1;

-- 4. Verificar los cambios
DESCRIBE reportes;

-- 5. Ver conteo actual de registros
SELECT COUNT(*) as total_registros FROM reportes;
