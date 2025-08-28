from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Optional, List
import sqlite3
import json
from datetime import datetime
import os

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

# Base de datos: usar ruta absoluta relativa al archivo
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_PATH = os.path.join(BASE_DIR, "reportes.db")

def init_database():
    """Inicializa la base de datos SQLite"""
    # Asegurar que el directorio existe
    os.makedirs(BASE_DIR, exist_ok=True)
    conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
    cursor = conn.cursor()
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS reportes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        latitud REAL NOT NULL,
        longitud REAL NOT NULL,
        timestamp TEXT NOT NULL,
        foto_base64 TEXT NOT NULL,
        descripcion TEXT,
        tipo_reporte TEXT DEFAULT 'general',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    conn.commit()
    conn.close()

def get_db_connection():
    """Obtiene una conexión a la base de datos"""
    conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

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
        with open(os.path.join(BASE_DIR, "mapa.html"), "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "<h1>Error: archivo mapa.html no encontrado</h1>"

@app.post("/reportes/", response_model=ReporteResponse)
async def crear_reporte(reporte: ReporteCreate):
    """Crear un nuevo reporte"""
    try:
        # Si no hay timestamp, usar actual
        if not reporte.timestamp:
            reporte.timestamp = datetime.now().isoformat()
        
        # Insertar en BD
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
        INSERT INTO reportes (latitud, longitud, timestamp, foto_base64, descripcion, tipo_reporte)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            reporte.latitud,
            reporte.longitud,
            reporte.timestamp,
            reporte.foto_base64,
            reporte.descripcion,
            reporte.tipo_reporte
        ))
        
        reporte_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return ReporteResponse(
            id=reporte_id,
            latitud=reporte.latitud,
            longitud=reporte.longitud,
            timestamp=reporte.timestamp,
            foto_base64=reporte.foto_base64,
            descripcion=reporte.descripcion,
            tipo_reporte=reporte.tipo_reporte
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.get("/reportes/", response_model=List[ReporteResponse])
async def obtener_reportes():
    """Obtener todos los reportes"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT id, latitud, longitud, timestamp, foto_base64, descripcion, tipo_reporte
        FROM reportes
        ORDER BY created_at DESC
        ''')
        
        reportes = []
        for row in cursor.fetchall():
            # Usar acceso por nombre (row_factory) para mayor claridad
            reportes.append(ReporteResponse(
                id=row["id"],
                latitud=row["latitud"],
                longitud=row["longitud"],
                timestamp=row["timestamp"],
                foto_base64=row["foto_base64"],
                descripcion=row["descripcion"],
                tipo_reporte=row["tipo_reporte"]
            ))
        
        conn.close()
        return reportes
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.get("/stats")
async def estadisticas():
    """Estadísticas de reportes"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) as total FROM reportes")
        total = cursor.fetchone()["total"]
        
        cursor.execute("SELECT timestamp FROM reportes ORDER BY created_at DESC LIMIT 1")
        ultimo_row = cursor.fetchone()
        ultimo = ultimo_row["timestamp"] if ultimo_row else None
        
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
    print(f"📍 DB path: {DATABASE_PATH}")
    print("📍 API: http://localhost:5000")
    print("📚 Docs: http://localhost:5000/docs")
    print("🗺️ Mapa: http://localhost:5000/mapa")
    uvicorn.run(app, host="0.0.0.0", port=5000, reload=True)