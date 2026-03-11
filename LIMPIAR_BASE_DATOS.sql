-- ⚠️⚠️⚠️ SCRIPT DESTRUCTIVO - USAR CON PRECAUCIÓN ⚠️⚠️⚠️
-- Este script ELIMINARÁ todos los registros de la tabla reportes
-- y reiniciará el contador AUTO_INCREMENT a 1

-- Ejecuta este script SOLO si estás completamente seguro

-- 1. Borrar todos los reportes
DELETE FROM reportes;

-- 2. Reiniciar contador AUTO_INCREMENT
ALTER TABLE reportes AUTO_INCREMENT = 1;

-- 3. Verificar que la tabla está vacía
SELECT COUNT(*) as total_registros FROM reportes;

-- 4. Mostrar estructura actualizada
DESCRIBE reportes;

-- Resultado esperado: 
-- total_registros = 0
-- El próximo registro insertado tendrá id = 1
