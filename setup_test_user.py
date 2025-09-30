#!/usr/bin/env python3
"""
Script para crear un usuario de prueba no verificado
"""

import mysql.connector
from passlib.context import CryptContext

# Configuración de la base de datos
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'reportes_gps'
}

# Configuración de hash de contraseñas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """Hashear contraseña usando bcrypt"""
    return pwd_context.hash(password)

def crear_usuario_prueba():
    """Crear usuario de prueba no verificado"""
    try:
        # Conectar a la base de datos
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()
        
        # Datos del usuario de prueba
        email_prueba = "gpsreportbaq@gmail.com"
        usuario = "testverify"
        nombres = "Usuario de Prueba Verificación"
        telefono = "3001234567"
        clave = "123456"
        
        # Verificar si el usuario ya existe
        cursor.execute("SELECT id, activo FROM usuarios WHERE correo = %s", (email_prueba,))
        user_exists = cursor.fetchone()
        
        if user_exists:
            user_id, activo = user_exists
            print(f"Usuario existente encontrado - ID: {user_id}, Estado: {activo}")
            
            # Si está verificado (activo=3), cambiar a no verificado (activo=1)
            if activo == 3:
                cursor.execute("UPDATE usuarios SET activo = 1 WHERE id = %s", (user_id,))
                connection.commit()
                print("✅ Usuario cambiado a estado no verificado (activo=1)")
            else:
                print("✅ Usuario ya está en estado no verificado")
        else:
            # Crear nuevo usuario no verificado
            clave_hash = hash_password(clave)
            cursor.execute("""
                INSERT INTO usuarios (usuario, clave_hash, nombres, telefono, correo, activo)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (usuario, clave_hash, nombres, telefono, email_prueba, 1))
            
            connection.commit()
            user_id = cursor.lastrowid
            print(f"✅ Usuario de prueba creado - ID: {user_id}")
        
        # Mostrar información del usuario
        cursor.execute("SELECT * FROM usuarios WHERE correo = %s", (email_prueba,))
        user_data = cursor.fetchone()
        
        if user_data:
            print("\n📋 Información del usuario de prueba:")
            print(f"   ID: {user_data[0]}")
            print(f"   Usuario: {user_data[1]}")
            print(f"   Nombres: {user_data[3]}")
            print(f"   Teléfono: {user_data[4]}")
            print(f"   Email: {user_data[5]}")
            print(f"   Estado: {user_data[6]} ({'Verificado' if user_data[6] == 3 else 'No Verificado'})")
        
        cursor.close()
        connection.close()
        
        print(f"\n🎯 Usuario listo para pruebas de verificación por código")
        print(f"   Email: {email_prueba}")
        print(f"   Usuario: {usuario}")
        print(f"   Contraseña: {clave}")
        
        return True
        
    except mysql.connector.Error as err:
        print(f"❌ Error de base de datos: {err}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🔧 Configurando usuario de prueba para verificación...")
    crear_usuario_prueba()