"""
Script para actualizar la base de datos existente y agregar columna 'aforo'
Ejecutar en la instancia principal (donde está main.py y MySQL)
"""

import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuración de la base de datos MySQL
DB_CONFIG = {
    'host': os.getenv('DB_HOST'),
    'port': int(os.getenv('DB_PORT', 3306)),
    'database': os.getenv('DB_NAME'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD')
}

def actualizar_bd():
    """Actualiza la tabla reportes para agregar columna aforo"""
    try:
        print("🔄 Conectando a la base de datos MySQL...")
        connection = mysql.connector.connect(**DB_CONFIG)
        
        if connection.is_connected():
            cursor = connection.cursor()
            
            print("✅ Conexión establecida")
            
            # Verificar si la columna 'aforo' ya existe
            cursor.execute("""
                SELECT COUNT(*) 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_SCHEMA = %s 
                AND TABLE_NAME = 'reportes' 
                AND COLUMN_NAME = 'aforo'
            """, (DB_CONFIG['database'],))
            
            existe = cursor.fetchone()[0] > 0
            
            if existe:
                print("ℹ️  La columna 'aforo' ya existe en la tabla 'reportes'")
            else:
                print("🔧 Agregando columna 'aforo' a la tabla 'reportes'...")
                
                # Agregar columna aforo
                cursor.execute("""
                    ALTER TABLE reportes 
                    ADD COLUMN aforo INT DEFAULT NULL 
                    COMMENT 'Número de personas detectadas'
                """)
                
                connection.commit()
                print("✅ Columna 'aforo' agregada exitosamente")
            
            # Mostrar estructura actualizada de la tabla
            print("\n📋 Estructura actualizada de la tabla 'reportes':")
            cursor.execute("DESCRIBE reportes")
            
            for row in cursor:
                print(f"  - {row[0]}: {row[1]} {row[2]} {row[3]} {row[4]}")
            
            # Estadísticas
            cursor.execute("SELECT COUNT(*) FROM reportes")
            total = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM reportes WHERE aforo IS NOT NULL")
            con_aforo = cursor.fetchone()[0]
            
            print(f"\n📊 Estadísticas:")
            print(f"  - Total de reportes: {total}")
            print(f"  - Reportes con aforo: {con_aforo}")
            print(f"  - Reportes sin aforo: {total - con_aforo}")
            
            cursor.close()
            connection.close()
            
            print("\n✅ Base de datos actualizada correctamente")
            return True
            
    except Error as e:
        print(f"❌ Error actualizando la base de datos: {e}")
        return False
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("ACTUALIZACIÓN DE BASE DE DATOS - COLUMNA AFORO")
    print("=" * 60)
    print(f"Host: {DB_CONFIG['host']}")
    print(f"Base de datos: {DB_CONFIG['database']}")
    print("=" * 60)
    print()
    
    exito = actualizar_bd()
    
    if exito:
        print("\n✅ ¡Actualización completada!")
        print("📌 Ahora puedes reiniciar el servidor con: python main.py")
    else:
        print("\n❌ La actualización falló. Revisa los errores anteriores.")
