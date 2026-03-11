#!/usr/bin/env python3
"""
Script para probar la conexión a RDS MySQL
"""
import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

DB_CONFIG = {
    'host': os.getenv('DB_HOST'),
    'port': int(os.getenv('DB_PORT', 3306)),
    'database': os.getenv('DB_NAME'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD')
}

def test_connection():
    """Prueba la conexión a la base de datos RDS"""
    print("🔧 Probando conexión a RDS MySQL...")
    print(f"Host: {DB_CONFIG['host']}")
    print(f"Database: {DB_CONFIG['database']}")
    print(f"User: {DB_CONFIG['user']}")
    print(f"Port: {DB_CONFIG['port']}")
    
    try:
        # Intentar conexión
        connection = mysql.connector.connect(**DB_CONFIG)
        
        if connection.is_connected():
            print("✅ ¡Conexión exitosa a RDS MySQL!")
            
            # Obtener información del servidor
            cursor = connection.cursor()
            cursor.execute("SELECT VERSION()")
            version = cursor.fetchone()
            print(f"📊 Versión MySQL: {version[0]}")
            
            # Verificar base de datos actual
            cursor.execute("SELECT DATABASE()")
            db = cursor.fetchone()
            print(f"📂 Base de datos actual: {db[0]}")
            
            # Listar tablas existentes
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            print(f"📋 Tablas existentes: {[table[0] for table in tables]}")
            
            cursor.close()
            connection.close()
            return True
            
    except Error as e:
        print(f"❌ Error de conexión: {e}")
        if "Access denied" in str(e):
            print("🔑 Problema de autenticación - verificar credenciales")
        elif "timeout" in str(e).lower():
            print("⏰ Timeout - verificar Security Groups")
        elif "Can't connect" in str(e):
            print("🌐 No se puede conectar - verificar Security Groups y IP")
        return False
    
    except Exception as e:
        print(f"💥 Error inesperado: {e}")
        return False

if __name__ == "__main__":
    success = test_connection()
    if success:
        print("\n🎉 La conexión está lista para usar!")
    else:
        print("\n❌ Necesitas configurar el acceso a RDS.")