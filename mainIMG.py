"""
mainIMG.py - Servidor de Procesamiento de Imágenes con Detección de Aforo
==========================================================================
Servidor FastAPI dedicado para:
1. Recibir imágenes base64 desde ESP32
2. Procesar con YOLOv8 para detectar personas
3. Calcular aforo (número de personas detectadas)
4. Enviar resultados (imagen + aforo) a la API principal (main.py)

Instancia: c7i-flex.large (2 vCPU, 4GB RAM)
IP Pública: 18.116.117.140
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Optional, List
import base64
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import cv2
import numpy as np
from datetime import datetime
import os
from dotenv import load_dotenv
import httpx
import asyncio
import torch
from ultralytics import YOLO
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Cargar variables de entorno
load_dotenv()

# Configuración
API_PRINCIPAL_URL = os.getenv('API_PRINCIPAL_URL', 'http://localhost:5000')
MODELO_YOLO = os.getenv('MODELO_YOLO', 'yolov8n.pt')  # yolov8n = nano (más rápido)
CONFIANZA_MIN = float(os.getenv('CONFIANZA_MIN', '0.45'))  # Umbral de confianza
PUERTO = int(os.getenv('PUERTO_IMG', '8000'))

# Directorio temporal para imágenes procesadas
TEMP_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "temp_procesadas")
os.makedirs(TEMP_FOLDER, exist_ok=True)

# Crear aplicación FastAPI
app = FastAPI(
    title="GPS Reporter - Servidor de Procesamiento de Imágenes",
    description="API para detección de aforo con YOLOv8",
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

# Variable global para el modelo YOLO (se carga al inicio)
modelo_yolo = None

# --- Modelos Pydantic ---
class ImagenESP32Request(BaseModel):
    """Modelo para recibir imagen desde ESP32"""
    foto_base64: str
    timestamp: Optional[str] = None
    latitud: Optional[float] = None
    longitud: Optional[float] = None
    descripcion: Optional[str] = None
    tipo_reporte: Optional[str] = "aforo"

class ImagenESP32Response(BaseModel):
    """Respuesta al ESP32"""
    success: bool
    message: str
    aforo: Optional[int] = None
    processing_time_ms: Optional[float] = None
    forwarded_to_api: Optional[bool] = None

class AforoDeteccionResponse(BaseModel):
    """Respuesta detallada de detección"""
    aforo: int
    confianza_promedio: float
    detecciones: List[dict]
    imagen_procesada_base64: Optional[str] = None

class StatsResponse(BaseModel):
    """Estadísticas del servidor"""
    imagenes_procesadas: int
    aforo_promedio: float
    modelo_cargado: bool
    modelo_nombre: str

# --- Estadísticas globales ---
stats = {
    "imagenes_procesadas": 0,
    "aforo_total": 0,
    "errores": 0
}

# --- Funciones de Procesamiento ---

def cargar_modelo_yolo():
    """Carga el modelo YOLO al iniciar el servidor"""
    global modelo_yolo
    try:
        logger.info(f"🔄 Cargando modelo YOLO: {MODELO_YOLO}")
        modelo_yolo = YOLO(MODELO_YOLO)
        logger.info(f"✅ Modelo YOLO {MODELO_YOLO} cargado exitosamente")
        
        # Warming up del modelo (primera inferencia es más lenta)
        logger.info("🔥 Calentando modelo...")
        dummy_img = np.zeros((640, 640, 3), dtype=np.uint8)
        modelo_yolo(dummy_img, verbose=False)
        logger.info("✅ Modelo listo para usar")
        
        return True
    except Exception as e:
        logger.error(f"❌ Error cargando modelo YOLO: {e}")
        logger.error("💡 Instala ultralytics: pip install ultralytics")
        return False

def base64_to_opencv(base64_str: str) -> np.ndarray:
    """Convierte imagen base64 a formato OpenCV (numpy array)"""
    try:
        # Decodificar base64
        image_data = base64.b64decode(base64_str)
        
        # Convertir a PIL Image
        pil_image = Image.open(BytesIO(image_data))
        
        # Convertir a RGB si es necesario
        if pil_image.mode != 'RGB':
            pil_image = pil_image.convert('RGB')
        
        # Convertir a numpy array (OpenCV format: BGR)
        opencv_image = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
        
        return opencv_image
    except Exception as e:
        logger.error(f"Error convirtiendo base64 a OpenCV: {e}")
        raise

def opencv_to_base64(opencv_image: np.ndarray) -> str:
    """Convierte imagen OpenCV a base64"""
    try:
        # Convertir BGR a RGB
        rgb_image = cv2.cvtColor(opencv_image, cv2.COLOR_BGR2RGB)
        
        # Convertir a PIL Image
        pil_image = Image.fromarray(rgb_image)
        
        # Guardar en buffer
        buffer = BytesIO()
        pil_image.save(buffer, format="JPEG", quality=85)
        
        # Codificar a base64
        base64_str = base64.b64encode(buffer.getvalue()).decode('utf-8')
        
        return base64_str
    except Exception as e:
        logger.error(f"Error convirtiendo OpenCV a base64: {e}")
        raise

def detectar_aforo_yolo(imagen_cv: np.ndarray, dibujar_boxes: bool = True) -> dict:
    """
    Detecta personas en la imagen usando YOLOv8
    
    Args:
        imagen_cv: Imagen en formato OpenCV (numpy array)
        dibujar_boxes: Si es True, dibuja cajas de detección en la imagen
    
    Returns:
        dict con: aforo, confianza_promedio, detecciones, imagen_procesada
    """
    if modelo_yolo is None:
        raise RuntimeError("Modelo YOLO no cargado")
    
    try:
        inicio = datetime.now()
        
        # Ejecutar detección
        resultados = modelo_yolo(imagen_cv, conf=CONFIANZA_MIN, verbose=False)
        
        # Extraer detecciones de personas (clase 0 en COCO dataset)
        detecciones = []
        imagen_procesada = imagen_cv.copy()
        
        for resultado in resultados:
            boxes = resultado.boxes
            
            for i, box in enumerate(boxes):
                # Obtener clase y confianza
                cls = int(box.cls[0])
                conf = float(box.conf[0])
                
                # Solo personas (clase 0)
                if cls == 0:
                    # Coordenadas del bounding box
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    
                    detecciones.append({
                        "id": len(detecciones) + 1,
                        "clase": "persona",
                        "confianza": round(conf, 2),
                        "bbox": [x1, y1, x2, y2]
                    })
                    
                    # Dibujar caja si es necesario
                    if dibujar_boxes:
                        # Color verde para alta confianza, amarillo para baja
                        color = (0, 255, 0) if conf > 0.6 else (0, 255, 255)
                        
                        # Dibujar rectángulo
                        cv2.rectangle(imagen_procesada, (x1, y1), (x2, y2), color, 2)
                        
                        # Texto con ID y confianza
                        texto = f"#{len(detecciones)} {conf:.2f}"
                        cv2.putText(imagen_procesada, texto, (x1, y1 - 10),
                                  cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        
        # Calcular estadísticas
        aforo = len(detecciones)
        confianza_promedio = sum(d["confianza"] for d in detecciones) / aforo if aforo > 0 else 0.0
        
        # Agregar texto de aforo en la imagen
        if dibujar_boxes:
            texto_aforo = f"AFORO: {aforo} persona{'s' if aforo != 1 else ''}"
            cv2.putText(imagen_procesada, texto_aforo, (20, 40),
                      cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 255), 3)
        
        tiempo_procesamiento = (datetime.now() - inicio).total_seconds() * 1000
        
        logger.info(f"✅ Detección completada: {aforo} personas en {tiempo_procesamiento:.1f}ms")
        
        return {
            "aforo": aforo,
            "confianza_promedio": round(confianza_promedio, 2),
            "detecciones": detecciones,
            "imagen_procesada": imagen_procesada,
            "tiempo_ms": round(tiempo_procesamiento, 1)
        }
        
    except Exception as e:
        logger.error(f"❌ Error en detección YOLO: {e}")
        raise

async def enviar_a_api_principal(
    foto_base64: str,
    timestamp: str,
    aforo: int,
    latitud: Optional[float] = None,
    longitud: Optional[float] = None,
    descripcion: Optional[str] = None,
    tipo_reporte: str = "aforo"
) -> bool:
    """
    Envía los datos procesados a la API principal (main.py)
    """
    try:
        payload = {
            "latitud": latitud or 0.0,
            "longitud": longitud or 0.0,
            "timestamp": timestamp,
            "foto_base64": foto_base64,
            "descripcion": descripcion or f"Aforo detectado: {aforo} personas",
            "tipo_reporte": tipo_reporte,
            "aforo": aforo  # Campo adicional
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{API_PRINCIPAL_URL}/reportes/",
                json=payload
            )
            
            if response.status_code == 200:
                logger.info(f"✅ Datos enviados a API principal: {API_PRINCIPAL_URL}")
                return True
            else:
                logger.error(f"❌ Error enviando a API principal: {response.status_code} - {response.text}")
                return False
                
    except Exception as e:
        logger.error(f"❌ Error conectando con API principal: {e}")
        return False

# --- Endpoints ---

@app.on_event("startup")
async def startup_event():
    """Inicialización al arrancar el servidor"""
    logger.info("🚀 Iniciando servidor de procesamiento de imágenes...")
    logger.info(f"📍 IP Pública: 18.116.117.140:{PUERTO}")
    logger.info(f"📡 API Principal: {API_PRINCIPAL_URL}")
    
    # Cargar modelo YOLO
    exito = cargar_modelo_yolo()
    if not exito:
        logger.warning("⚠️ Servidor iniciado sin modelo YOLO. No se podrá procesar imágenes.")
    
    logger.info("✅ Servidor listo para recibir imágenes")

@app.get("/", response_class=HTMLResponse)
async def root():
    """Página principal"""
    modelo_status = "✅ Cargado" if modelo_yolo else "❌ No cargado"
    
    return f"""
    <html>
        <head>
            <title>Servidor de Procesamiento - GPS Reporter</title>
            <meta http-equiv="refresh" content="30">
        </head>
        <body style="font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px;">
            <h1>🖼️ Servidor de Procesamiento de Imágenes</h1>
            <p>Sistema de detección de aforo con YOLOv8</p>
            
            <div style="background: #f0f9ff; padding: 20px; border-radius: 8px; margin: 20px 0;">
                <h3>📊 Estado del Sistema</h3>
                <p><strong>Modelo YOLO:</strong> {modelo_status} ({MODELO_YOLO})</p>
                <p><strong>Confianza mínima:</strong> {CONFIANZA_MIN}</p>
                <p><strong>API Principal:</strong> {API_PRINCIPAL_URL}</p>
                <p><strong>Imágenes procesadas:</strong> {stats['imagenes_procesadas']}</p>
                <p><strong>Aforo promedio:</strong> {stats['aforo_total'] / max(1, stats['imagenes_procesadas']):.1f}</p>
                <p><strong>Errores:</strong> {stats['errores']}</p>
            </div>
            
            <div style="background: #fff7ed; padding: 20px; border-radius: 8px;">
                <h3>📡 Endpoints Disponibles</h3>
                <ul>
                    <li><a href="/docs">📚 Documentación API (Swagger)</a></li>
                    <li><a href="/health">🏥 Estado de salud</a></li>
                    <li><a href="/stats">📊 Estadísticas</a></li>
                    <li><strong>POST /procesar-imagen</strong> - Endpoint principal para ESP32</li>
                </ul>
            </div>
            
            <div style="background: #f0fdf4; padding: 20px; border-radius: 8px; margin-top: 20px;">
                <h3>🔌 Uso desde ESP32</h3>
                <pre style="background: #1e293b; color: #10b981; padding: 15px; border-radius: 6px; overflow-x: auto;">
POST http://18.116.117.140:{PUERTO}/procesar-imagen
Content-Type: application/json

{{
  "foto_base64": "iVBORw0KGgoAAAANS...",
  "timestamp": "2025-12-02T10:30:00",
  "latitud": -12.0464,
  "longitud": -77.0428,
  "descripcion": "Captura desde ESP32"
}}
                </pre>
            </div>
        </body>
    </html>
    """

@app.get("/health")
async def health_check():
    """Endpoint de salud"""
    return {
        "status": "UP",
        "modelo_yolo": modelo_yolo is not None,
        "modelo_nombre": MODELO_YOLO,
        "api_principal": API_PRINCIPAL_URL,
        "imagenes_procesadas": stats["imagenes_procesadas"]
    }

@app.get("/stats", response_model=StatsResponse)
async def obtener_estadisticas():
    """Estadísticas del servidor"""
    return StatsResponse(
        imagenes_procesadas=stats["imagenes_procesadas"],
        aforo_promedio=stats["aforo_total"] / max(1, stats["imagenes_procesadas"]),
        modelo_cargado=modelo_yolo is not None,
        modelo_nombre=MODELO_YOLO
    )

@app.post("/procesar-imagen", response_model=ImagenESP32Response)
async def procesar_imagen_esp32(
    request: ImagenESP32Request,
    background_tasks: BackgroundTasks
):
    """
    Endpoint principal: Recibe imagen desde ESP32, procesa aforo y envía a API principal
    """
    inicio = datetime.now()
    
    try:
        # Validar que el modelo esté cargado
        if modelo_yolo is None:
            raise HTTPException(
                status_code=503,
                detail="Modelo YOLO no disponible. Servidor no listo para procesar."
            )
        
        # Validar imagen base64
        if not request.foto_base64:
            raise HTTPException(status_code=400, detail="foto_base64 es requerida")
        
        # Timestamp por defecto
        timestamp = request.timestamp or datetime.now().isoformat()
        
        logger.info(f"📥 Nueva imagen recibida. Timestamp: {timestamp}")
        
        # Convertir base64 a OpenCV
        imagen_cv = base64_to_opencv(request.foto_base64)
        logger.info(f"✅ Imagen decodificada: {imagen_cv.shape}")
        
        # Detectar aforo
        resultado = detectar_aforo_yolo(imagen_cv, dibujar_boxes=True)
        aforo = resultado["aforo"]
        
        # Convertir imagen procesada a base64
        imagen_procesada_b64 = opencv_to_base64(resultado["imagen_procesada"])
        
        # Actualizar estadísticas
        stats["imagenes_procesadas"] += 1
        stats["aforo_total"] += aforo
        
        # Enviar a API principal en background
        enviado = await enviar_a_api_principal(
            foto_base64=imagen_procesada_b64,
            timestamp=timestamp,
            aforo=aforo,
            latitud=request.latitud,
            longitud=request.longitud,
            descripcion=request.descripcion,
            tipo_reporte=request.tipo_reporte or "aforo"
        )
        
        tiempo_total = (datetime.now() - inicio).total_seconds() * 1000
        
        logger.info(f"✅ Procesamiento completo en {tiempo_total:.1f}ms - Aforo: {aforo}")
        
        return ImagenESP32Response(
            success=True,
            message=f"Imagen procesada exitosamente. Aforo detectado: {aforo} persona{'s' if aforo != 1 else ''}",
            aforo=aforo,
            processing_time_ms=round(tiempo_total, 1),
            forwarded_to_api=enviado
        )
        
    except HTTPException:
        raise
    except Exception as e:
        stats["errores"] += 1
        logger.error(f"❌ Error procesando imagen: {e}")
        raise HTTPException(status_code=500, detail=f"Error procesando imagen: {str(e)}")

@app.post("/test-deteccion", response_model=AforoDeteccionResponse)
async def test_deteccion(request: ImagenESP32Request):
    """
    Endpoint de prueba: Solo detecta aforo sin enviar a API principal
    Útil para debugging
    """
    try:
        if modelo_yolo is None:
            raise HTTPException(status_code=503, detail="Modelo YOLO no disponible")
        
        # Convertir y detectar
        imagen_cv = base64_to_opencv(request.foto_base64)
        resultado = detectar_aforo_yolo(imagen_cv, dibujar_boxes=True)
        
        # Convertir imagen procesada
        imagen_procesada_b64 = opencv_to_base64(resultado["imagen_procesada"])
        
        return AforoDeteccionResponse(
            aforo=resultado["aforo"],
            confianza_promedio=resultado["confianza_promedio"],
            detecciones=resultado["detecciones"],
            imagen_procesada_base64=imagen_procesada_b64
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en test de detección: {str(e)}")

@app.post("/reload-modelo")
async def recargar_modelo():
    """Recarga el modelo YOLO (útil si se actualiza)"""
    try:
        exito = cargar_modelo_yolo()
        if exito:
            return {"success": True, "message": "Modelo recargado exitosamente"}
        else:
            raise HTTPException(status_code=500, detail="Error recargando modelo")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

# --- Ejecución ---
if __name__ == "__main__":
    import uvicorn
    
    print("=" * 70)
    print("🖼️  SERVIDOR DE PROCESAMIENTO DE IMÁGENES - GPS REPORTER")
    print("=" * 70)
    print(f"📍 IP Pública: 18.116.117.140:{PUERTO}")
    print(f"🤖 Modelo: {MODELO_YOLO}")
    print(f"📡 API Principal: {API_PRINCIPAL_URL}")
    print(f"🌐 Docs: http://18.116.117.140:{PUERTO}/docs")
    print("=" * 70)
    
    uvicorn.run(
        app,
        host="0.0.0.0",  # Escuchar en todas las interfaces
        port=PUERTO,
        reload=False  # Desactivar reload en producción
    )
