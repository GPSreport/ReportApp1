import os
from dotenv import load_dotenv
import mysql.connector
from mysql.connector import Error

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

def create_database():
    try:
        # Conectar a MySQL sin seleccionar una base de datos
        conn = mysql.connector.connect(
            host=DB_CONFIG['host'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password']
        )
        
        cursor = conn.cursor()
        
        # Crear la base de datos si no existe
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_CONFIG['database']}")
        
        # Seleccionar la base de datos
        cursor.execute(f"USE {DB_CONFIG['database']}")
        
        # Crear la tabla reportes
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS reportes (
                id INT AUTO_INCREMENT PRIMARY KEY,
                latitud DECIMAL(10, 8) NOT NULL,
                longitud DECIMAL(11, 8) NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                descripcion TEXT,
                tipo_reporte VARCHAR(50) DEFAULT 'otro',
                foto_base64 LONGTEXT
            )
        """)
        
        print("Base de datos y tabla creadas correctamente")
        conn.commit()
        
    except Error as e:
        print(f"Error: {e}")
    
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

if __name__ == "__main__":
    create_database()
