import os
from dotenv import load_dotenv
import mysql.connector
from mysql.connector import Error
import hashlib
from typing import Optional

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

def hash_password(password: str) -> str:
    """Genera hash SHA-256 de la contraseña"""
    return hashlib.sha256(password.encode()).hexdigest()

def create_database():
    try:
        print("🚀 Inicializando base de datos MySQL...")
        print(f"📍 Host: {DB_CONFIG['host']}")
        print(f"📂 Database: {DB_CONFIG['database']}")
        
        # Conectar a MySQL sin seleccionar una base de datos
        conn = mysql.connector.connect(
            host=DB_CONFIG['host'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            port=DB_CONFIG['port']
        )
        
        cursor = conn.cursor()
        
        # Crear la base de datos si no existe
        print(f"📦 Creando base de datos '{DB_CONFIG['database']}'...")
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_CONFIG['database']}")
        
        # Seleccionar la base de datos
        cursor.execute(f"USE {DB_CONFIG['database']}")
        
        # Crear la tabla reportes
        print("📊 Creando tabla 'reportes'...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS reportes (
                id INT AUTO_INCREMENT PRIMARY KEY,
                latitud DECIMAL(10, 8) NOT NULL,
                longitud DECIMAL(11, 8) NOT NULL,
                timestamp DATETIME NOT NULL,
                foto_base64 LONGTEXT NOT NULL,
                descripcion TEXT,
                tipo_reporte VARCHAR(50) DEFAULT 'general',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Crear la tabla usuarios para login (con nuevos campos)
        print("👥 Creando/actualizando tabla 'usuarios'...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id INT AUTO_INCREMENT PRIMARY KEY,
                usuario VARCHAR(50) UNIQUE NOT NULL,
                clave_hash VARCHAR(64) NOT NULL,
                nombres VARCHAR(100) NULL,
                telefono VARCHAR(20) NULL,
                numero_usuario INT UNIQUE,
                activo BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP NULL
            )
        """)

        # Migración segura: asegurar columnas si faltan (para instalaciones existentes)
        def ensure_column(name: str, definition: str):
            cursor.execute(
                """
                SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_SCHEMA = %s AND TABLE_NAME = 'usuarios' AND COLUMN_NAME = %s
                """,
                (DB_CONFIG['database'], name)
            )
            exists = cursor.fetchone()[0] > 0
            if not exists:
                print(f"🔧 Agregando columna faltante '{name}' a usuarios...")
                cursor.execute(f"ALTER TABLE usuarios ADD COLUMN {definition}")

        ensure_column('nombres', 'nombres VARCHAR(100) NULL')
        ensure_column('telefono', 'telefono VARCHAR(20) NULL')
        ensure_column('numero_usuario', 'numero_usuario INT UNIQUE')

        # Asignar numero_usuario a registros existentes si está NULL
        cursor.execute("SELECT id FROM usuarios WHERE numero_usuario IS NULL ORDER BY id")
        rows_missing = cursor.fetchall()
        if rows_missing:
            print("🔢 Asignando numero_usuario a usuarios existentes...")
            # Obtener máximo actual
            cursor.execute("SELECT COALESCE(MAX(numero_usuario), 0) FROM usuarios")
            max_num = cursor.fetchone()[0] or 0
            next_num = max_num + 1
            for (uid,) in rows_missing:
                cursor.execute("UPDATE usuarios SET numero_usuario = %s WHERE id = %s", (next_num, uid))
                next_num += 1
        
        # Helper para obtener siguiente numero_usuario
        def get_next_user_number(cur) -> int:
            cur.execute("SELECT COALESCE(MAX(numero_usuario), 0) + 1 FROM usuarios")
            return int(cur.fetchone()[0])

        # Verificar si ya existe un usuario admin por defecto
        cursor.execute("SELECT COUNT(*) as count FROM usuarios WHERE usuario = 'admin'")
        result = cursor.fetchone()
        
        if result[0] == 0:
            # Crear usuario admin por defecto con contraseña "admin123"
            admin_password_hash = hash_password("admin123")
            admin_num = get_next_user_number(cursor)
            cursor.execute('''
            INSERT INTO usuarios (usuario, clave_hash, activo, nombres, telefono, numero_usuario)
            VALUES (%s, %s, %s, %s, %s, %s)
            ''', ('admin', admin_password_hash, True, 'Administrador', '0000000000', admin_num))
            print(f"✅ Usuario 'admin' creado (contraseña: admin123, numero_usuario: {admin_num})")
        else:
            print("ℹ️ Usuario 'admin' ya existe")
        
        # Verificar si existe usuario "usuario" por defecto
        cursor.execute("SELECT COUNT(*) as count FROM usuarios WHERE usuario = 'usuario'")
        result = cursor.fetchone()
        
        if result[0] == 0:
            # Crear usuario "usuario" por defecto con contraseña "123456"
            user_password_hash = hash_password("123456")
            usr_num = get_next_user_number(cursor)
            cursor.execute('''
            INSERT INTO usuarios (usuario, clave_hash, activo, nombres, telefono, numero_usuario)
            VALUES (%s, %s, %s, %s, %s, %s)
            ''', ('usuario', user_password_hash, True, 'Usuario de prueba', '1111111111', usr_num))
            print(f"✅ Usuario 'usuario' creado (contraseña: 123456, numero_usuario: {usr_num})")
        else:
            print("ℹ️ Usuario 'usuario' ya existe")
        
        # Mostrar estadísticas
        cursor.execute("SELECT COUNT(*) FROM reportes")
        reportes_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM usuarios WHERE activo = TRUE")
        usuarios_count = cursor.fetchone()[0]
        
        print("\n📈 RESUMEN:")
        print(f"📊 Reportes en base de datos: {reportes_count}")
        print(f"👥 Usuarios activos: {usuarios_count}")
        print("✅ Base de datos inicializada correctamente")
        
        conn.commit()
        
    except Error as e:
        print(f"❌ Error de MySQL: {e}")
        return False
    
    except Exception as e:
        print(f"💥 Error inesperado: {e}")
        return False
    
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()
            print("🔌 Conexión cerrada")
    
    return True

if __name__ == "__main__":
    print("=" * 60)
    print("🔧 CONFIGURACIÓN DE BASE DE DATOS REPORTES GPS")
    print("=" * 60)
    
    success = create_database()
    
    if success:
        print("\n🎉 ¡CONFIGURACIÓN COMPLETADA!")
        print("\n🔐 Credenciales de login disponibles:")
        print("   👤 Usuario: admin    | 🔑 Contraseña: admin123")
        print("   👤 Usuario: usuario  | 🔑 Contraseña: 123456")
        print("\n🚀 Puedes ejecutar el servidor ahora:")
        print("   python main.py")
    else:
        print("\n❌ Error en la configuración. Revisa los logs arriba.")
