from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Optional, List
import mysql.connector
from mysql.connector import Error
import json
from datetime import datetime
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

# Crear la aplicación FastAPI
app = FastAPI(
    title="Reportes GPS API",
    description="API para recibir y servir reportes con coordenadas GPS y fotos",
    version="1.0.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modelos
class ReporteCreate(BaseModel):
    latitud: float
    longitud: float
    timestamp: Optional[str] = None
    foto_base64: str
    descripcion: Optional[str] = None
    tipo_reporte: Optional[str] = "general"

class ReporteResponse(BaseModel):
    id: int
    latitud: float
    longitud: float
    timestamp: str
    foto_base64: str
    descripcion: Optional[str]
    tipo_reporte: str

def get_db_connection():
    """Obtiene una conexión a la base de datos MySQL"""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

def init_database():
    """Inicializa la base de datos MySQL"""
    conn = get_db_connection()
    if conn is None:
        raise Exception("No se pudo conectar a la base de datos")
        
    cursor = conn.cursor()
    
    cursor.execute('''
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
    ''')
    
    conn.commit()
    cursor.close()
    conn.close()

# Inicializar BD al iniciar
@app.on_event("startup")
async def startup_event():
    init_database()

# Endpoints
@app.get("/", response_class=HTMLResponse)
async def root():
    return """
    <html>
        <head><title>Reportes GPS API</title></head>
        <body>
            <h1>🗺️ API de Reportes GPS</h1>
            <p>Bienvenido a la API de reportes con coordenadas GPS</p>
            <ul>
                <li><a href="/docs">📚 Documentación Swagger</a></li>
                <li><a href="/mapa">🗺️ Ver Mapa de Reportes</a></li>
                <li><a href="/reportes">📊 Ver Reportes (JSON)</a></li>
            </ul>
        </body>
    </html>
    """

@app.get("/mapa", response_class=HTMLResponse)
async def mapa():
    """Página web con mapa interactivo"""
    try:
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "mapa.html"), "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "<h1>Error: archivo mapa.html no encontrado</h1>"

@app.post("/reportes/", response_model=ReporteResponse)
async def crear_reporte(reporte: ReporteCreate):
    """Crear un nuevo reporte"""
    try:
        # Si no hay timestamp, usar actual
        current_time = datetime.now()
        if not reporte.timestamp:
            reporte.timestamp = current_time.isoformat()
        else:
            # Convertir el timestamp de string a datetime si es necesario
            try:
                current_time = datetime.fromisoformat(reporte.timestamp)
            except ValueError:
                current_time = datetime.now()
        
        conn = get_db_connection()
        if conn is None:
            raise HTTPException(status_code=500, detail="Error de conexión a la base de datos")
            
        cursor = conn.cursor(dictionary=True)
        
        # Asegurar que latitud y longitud sean float con precisión correcta
        lat = round(float(reporte.latitud), 8)
        lng = round(float(reporte.longitud), 8)
        
        cursor.execute('''
        INSERT INTO reportes (latitud, longitud, timestamp, foto_base64, descripcion, tipo_reporte)
        VALUES (%s, %s, %s, %s, %s, %s)
        ''', (
            lat,
            lng,
            current_time,  # Usar el objeto datetime directamente
            reporte.foto_base64,
            reporte.descripcion or None,  # Convertir string vacío a None
            reporte.tipo_reporte or 'general'  # Valor por defecto si es None
        ))
        
        reporte_id = cursor.lastrowid
        conn.commit()
        cursor.close()
        conn.close()
        
        return ReporteResponse(
            id=reporte_id,
            latitud=lat,
            longitud=lng,
            timestamp=current_time.isoformat(),  # Convertir de nuevo a ISO format para la respuesta
            foto_base64=reporte.foto_base64,
            descripcion=reporte.descripcion,
            tipo_reporte=reporte.tipo_reporte or 'general'
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.get("/reportes/", response_model=List[ReporteResponse])
async def obtener_reportes():
    """Obtener todos los reportes"""
    try:
        conn = get_db_connection()
        if conn is None:
            raise HTTPException(status_code=500, detail="Error de conexión a la base de datos")
            
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute('''
        SELECT id, latitud, longitud, timestamp, foto_base64, descripcion, tipo_reporte
        FROM reportes
        ORDER BY created_at DESC
        ''')
        
        reportes = []
        for row in cursor:
            # Asegurar que los tipos de datos sean correctos
            lat = round(float(row["latitud"]), 8)
            lng = round(float(row["longitud"]), 8)
            
            # Manejar el timestamp
            if isinstance(row["timestamp"], datetime):
                timestamp = row["timestamp"].isoformat()
            else:
                try:
                    timestamp = datetime.fromisoformat(str(row["timestamp"])).isoformat()
                except ValueError:
                    timestamp = datetime.now().isoformat()
            
            reportes.append(ReporteResponse(
                id=int(row["id"]),
                latitud=lat,
                longitud=lng,
                timestamp=timestamp,
                foto_base64=row["foto_base64"] or "",  # Evitar None en foto_base64
                descripcion=row["descripcion"] or "",  # Convertir None a string vacío
                tipo_reporte=row["tipo_reporte"] or "general"  # Usar valor por defecto si es None
            ))
        
        cursor.close()
        conn.close()
        return reportes
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.get("/stats")
async def estadisticas():
    """Estadísticas de reportes"""
    try:
        conn = get_db_connection()
        if conn is None:
            raise HTTPException(status_code=500, detail="Error de conexión a la base de datos")
            
        cursor = conn.cursor(dictionary=True)
        
        # Obtener total de reportes
        cursor.execute("SELECT COUNT(*) as total FROM reportes")
        result = cursor.fetchone()
        total = int(result["total"]) if result else 0
        
        # Obtener último reporte con manejo seguro de fecha
        cursor.execute("SELECT timestamp FROM reportes ORDER BY created_at DESC LIMIT 1")
        ultimo_row = cursor.fetchone()
        
        if ultimo_row and ultimo_row["timestamp"]:
            if isinstance(ultimo_row["timestamp"], datetime):
                ultimo = ultimo_row["timestamp"].isoformat()
            else:
                try:
                    ultimo = datetime.fromisoformat(str(ultimo_row["timestamp"])).isoformat()
                except ValueError:
                    ultimo = None
        else:
            ultimo = None
        
        cursor.close()
        conn.close()
        
        return {
            "total_reportes": total,
            "ultimo_reporte": ultimo
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    print("🚀 Iniciando servidor...")
    #print(f"📍 DB path: {DATABASE_PATH}")
    print("📍 API: http://localhost:5000")
    print("📚 Docs: http://localhost:5000/docs")
    print("🗺️ Mapa: http://localhost:5000/mapa")
    uvicorn.run(app, host="0.0.0.0", port=5000, reload=True)