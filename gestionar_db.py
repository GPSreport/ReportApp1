#!/usr/bin/env python3
"""
Script para gestionar la base de datos de reportes
Permite limpiar registros y reiniciar contadores de forma segura
"""

import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv
import sys

# Cargar variables de entorno
load_dotenv()

# Configuración de la base de datos
DB_CONFIG = {
    'host': os.getenv('DB_HOST'),
    'port': int(os.getenv('DB_PORT', 3306)),
    'database': os.getenv('DB_NAME'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD')
}

def conectar_db():
    """Conectar a la base de datos"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        print(f"✅ Conectado a la base de datos: {DB_CONFIG['database']}")
        return conn
    except Error as e:
        print(f"❌ Error de conexión: {e}")
        return None

def mostrar_estadisticas(cursor):
    """Mostrar estadísticas de la base de datos"""
    print("\n📊 ESTADÍSTICAS ACTUALES:")
    print("-" * 50)
    
    # Total de reportes
    cursor.execute("SELECT COUNT(*) as total FROM reportes")
    total = cursor.fetchone()[0]
    print(f"Total de reportes: {total}")
    
    # Reportes por tipo
    cursor.execute("""
        SELECT tipo_reporte, COUNT(*) as cantidad 
        FROM reportes 
        GROUP BY tipo_reporte
        ORDER BY cantidad DESC
    """)
    print("\nReportes por tipo:")
    for row in cursor.fetchall():
        print(f"  - {row[0]}: {row[1]}")
    
    # Último ID
    cursor.execute("SELECT MAX(id) as ultimo_id FROM reportes")
    ultimo_id = cursor.fetchone()[0]
    print(f"\nÚltimo ID: {ultimo_id if ultimo_id else 'N/A'}")
    
    # Auto increment actual
    cursor.execute(f"SHOW TABLE STATUS LIKE 'reportes'")
    status = cursor.fetchone()
    if status:
        print(f"Próximo AUTO_INCREMENT: {status[10]}")
    
    print("-" * 50)

def agregar_columnas_eventos(conn):
    """Agregar columnas para fechas de eventos si no existen"""
    cursor = conn.cursor()
    
    try:
        print("\n🔧 Verificando columnas de eventos...")
        
        # Verificar si las columnas ya existen
        cursor.execute("""
            SELECT COLUMN_NAME 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = %s 
            AND TABLE_NAME = 'reportes' 
            AND COLUMN_NAME IN ('fecha_inicio_evento', 'fecha_fin_evento')
        """, (DB_CONFIG['database'],))
        
        columnas_existentes = [row[0] for row in cursor.fetchall()]
        
        if 'fecha_inicio_evento' in columnas_existentes and 'fecha_fin_evento' in columnas_existentes:
            print("✅ Las columnas de eventos ya existen")
            return True
        
        print("➕ Agregando columnas de eventos...")
        
        if 'fecha_inicio_evento' not in columnas_existentes:
            cursor.execute("""
                ALTER TABLE reportes 
                ADD COLUMN fecha_inicio_evento DATETIME NULL 
                COMMENT 'Fecha y hora de inicio del evento'
            """)
            print("   ✓ Columna 'fecha_inicio_evento' agregada")
        
        if 'fecha_fin_evento' not in columnas_existentes:
            cursor.execute("""
                ALTER TABLE reportes 
                ADD COLUMN fecha_fin_evento DATETIME NULL 
                COMMENT 'Fecha y hora de fin del evento'
            """)
            print("   ✓ Columna 'fecha_fin_evento' agregada")
        
        conn.commit()
        print("✅ Columnas de eventos agregadas correctamente")
        return True
        
    except Error as e:
        print(f"❌ Error al agregar columnas: {e}")
        conn.rollback()
        return False
    finally:
        cursor.close()

def limpiar_base_datos(conn, confirmar=True):
    """Limpiar todos los reportes y reiniciar contador"""
    cursor = conn.cursor()
    
    try:
        # Mostrar estadísticas antes de borrar
        mostrar_estadisticas(cursor)
        
        if confirmar:
            print("\n⚠️  ¡ADVERTENCIA! ⚠️")
            print("Esta operación eliminará TODOS los reportes de la base de datos.")
            print("Esta acción NO se puede deshacer.")
            respuesta = input("\n¿Estás seguro? Escribe 'SI BORRAR TODO' para confirmar: ")
            
            if respuesta != "SI BORRAR TODO":
                print("❌ Operación cancelada")
                return False
        
        print("\n🗑️  Eliminando todos los reportes...")
        cursor.execute("DELETE FROM reportes")
        registros_borrados = cursor.rowcount
        
        print(f"   ✓ {registros_borrados} registros eliminados")
        
        print("🔄 Reiniciando contador AUTO_INCREMENT...")
        cursor.execute("ALTER TABLE reportes AUTO_INCREMENT = 1")
        print("   ✓ Contador reiniciado a 1")
        
        conn.commit()
        
        # Mostrar estadísticas después de limpiar
        print("\n📊 ESTADÍSTICAS DESPUÉS DE LIMPIAR:")
        mostrar_estadisticas(cursor)
        
        print("\n✅ Base de datos limpiada exitosamente")
        print("   El próximo reporte tendrá ID = 1")
        return True
        
    except Error as e:
        print(f"❌ Error al limpiar base de datos: {e}")
        conn.rollback()
        return False
    finally:
        cursor.close()

def menu_principal():
    """Menú principal del script"""
    print("\n" + "=" * 60)
    print("   🛠️  GESTOR DE BASE DE DATOS - REPORTES GPS")
    print("=" * 60)
    print("\nOpciones:")
    print("  1. Ver estadísticas")
    print("  2. Agregar columnas de eventos (si no existen)")
    print("  3. Limpiar base de datos (BORRAR TODO)")
    print("  4. Salir")
    print("-" * 60)
    
    opcion = input("\nSelecciona una opción (1-4): ").strip()
    return opcion

def main():
    """Función principal"""
    conn = conectar_db()
    
    if not conn:
        print("❌ No se pudo conectar a la base de datos")
        sys.exit(1)
    
    try:
        while True:
            opcion = menu_principal()
            
            if opcion == "1":
                cursor = conn.cursor()
                mostrar_estadisticas(cursor)
                cursor.close()
                input("\nPresiona Enter para continuar...")
                
            elif opcion == "2":
                agregar_columnas_eventos(conn)
                input("\nPresiona Enter para continuar...")
                
            elif opcion == "3":
                limpiar_base_datos(conn, confirmar=True)
                input("\nPresiona Enter para continuar...")
                
            elif opcion == "4":
                print("\n👋 ¡Hasta luego!")
                break
                
            else:
                print("\n❌ Opción inválida. Intenta de nuevo.")
                input("\nPresiona Enter para continuar...")
    
    finally:
        if conn.is_connected():
            conn.close()
            print("\n🔌 Conexión cerrada")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Operación cancelada por el usuario")
        sys.exit(0)
