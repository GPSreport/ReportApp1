#!/usr/bin/env python3
"""
Script mejorado para probar conexión RDS con diagnósticos
"""
import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv
import socket
import time

# Cargar variables de entorno
load_dotenv()

DB_CONFIG = {
    'host': os.getenv('DB_HOST'),
    'port': int(os.getenv('DB_PORT', 3306)),
    'database': os.getenv('DB_NAME'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'connection_timeout': 30,  # Timeout más largo
    'autocommit': True
}

def test_network_connectivity():
    """Prueba la conectividad de red básica"""
    host = DB_CONFIG['host']
    port = DB_CONFIG['port']
    
    print(f"🌐 Probando conectividad de red a {host}:{port}...")
    
    try:
        # Crear socket y probar conexión TCP
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        result = sock.connect_ex((host, port))
        sock.close()
        
        if result == 0:
            print("✅ Conectividad TCP exitosa - puerto abierto")
            return True
        else:
            print(f"❌ Puerto cerrado o bloqueado (código: {result})")
            return False
            
    except socket.gaierror as e:
        print(f"❌ Error de DNS: {e}")
        return False
    except Exception as e:
        print(f"❌ Error de red: {e}")
        return False

def test_mysql_connection():
    """Prueba la conexión MySQL completa"""
    print("🔧 Probando conexión MySQL...")
    print(f"Host: {DB_CONFIG['host']}")
    print(f"Database: {DB_CONFIG['database']}")
    print(f"User: {DB_CONFIG['user']}")
    print(f"Port: {DB_CONFIG['port']}")
    
    try:
        # Conexión con timeout extendido
        connection = mysql.connector.connect(**DB_CONFIG)
        
        if connection.is_connected():
            print("✅ ¡Conexión MySQL exitosa!")
            
            cursor = connection.cursor()
            
            # Información del servidor
            cursor.execute("SELECT VERSION()")
            version = cursor.fetchone()
            print(f"📊 Versión MySQL: {version[0]}")
            
            # Base de datos actual
            cursor.execute("SELECT DATABASE()")
            db = cursor.fetchone()
            print(f"📂 Base de datos: {db[0]}")
            
            # Listar tablas
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            table_list = [table[0] for table in tables]
            print(f"📋 Tablas existentes: {table_list}")
            
            # Verificar si tabla usuarios existe
            if 'usuarios' in table_list:
                print("✅ Tabla 'usuarios' ya existe")
                cursor.execute("SELECT COUNT(*) FROM usuarios")
                count = cursor.fetchone()
                print(f"👥 Usuarios registrados: {count[0]}")
            else:
                print("⚠️ Tabla 'usuarios' no existe - se creará automáticamente")
            
            cursor.close()
            connection.close()
            return True
            
    except mysql.connector.Error as e:
        print(f"❌ Error MySQL: {e}")
        
        # Análisis específico del error
        if e.errno == 2003:
            print("🔍 Diagnóstico: No se puede conectar al servidor")
            print("   - Verifica que el Security Group permita tu IP")
            print("   - Confirma que la instancia RDS esté en estado 'available'")
        elif e.errno == 1045:
            print("🔍 Diagnóstico: Error de autenticación")
            print("   - Verifica usuario y contraseña")
        elif e.errno == 1049:
            print("🔍 Diagnóstico: Base de datos no existe")
            print("   - Verifica el nombre de la base de datos")
        
        return False
    
    except Exception as e:
        print(f"💥 Error inesperado: {e}")
        return False

def main():
    print("=" * 60)
    print("🚀 DIAGNÓSTICO DE CONEXIÓN RDS")
    print("=" * 60)
    
    # Paso 1: Verificar conectividad de red
    network_ok = test_network_connectivity()
    print()
    
    # Paso 2: Si la red está OK, probar MySQL
    if network_ok:
        mysql_ok = test_mysql_connection()
        print()
        
        if mysql_ok:
            print("🎉 ¡TODO CONFIGURADO CORRECTAMENTE!")
            print("✅ Puedes ejecutar el servidor ahora")
        else:
            print("❌ Problema con la autenticación MySQL")
    else:
        print("❌ PROBLEMA DE CONECTIVIDAD")
        print("🔧 Configura el Security Group con tu IP: 186.168.214.122/32")
        print("📋 Pasos:")
        print("   1. Ve a AWS RDS Console")
        print("   2. Selecciona tu instancia 'reportdatabase'")
        print("   3. Ve a Security Groups")
        print("   4. Agrega regla: MySQL/Aurora, puerto 3306, IP 186.168.214.122/32")

if __name__ == "__main__":
    main()