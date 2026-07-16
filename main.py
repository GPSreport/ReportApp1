from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, EmailStr
from typing import Optional, List
import mysql.connector
from mysql.connector import Error
import json
from datetime import datetime
from zoneinfo import ZoneInfo
import os
from dotenv import load_dotenv
import base64
from PIL import Image
from io import BytesIO
import hashlib
import re
import boto3
from botocore.exceptions import ClientError
import uuid
import random
import string
from urllib.parse import urlencode

# Cargar variables de entorno
load_dotenv()

# Configuración de la base de datos MySQL
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('DB_PORT', 3306)),
    'database': os.getenv('DB_NAME', 'gpsdb'),
    'user': os.getenv('DB_USER', 'dbuser'),
    'password': os.getenv('DB_PASSWORD', 'DB214user*')
}

# Configuración de AWS SES
AWS_CONFIG = {
    'region': os.getenv('AWS_REGION', 'us-east-1'),
    'access_key': os.getenv('AWS_ACCESS_KEY_ID'),
    'secret_key': os.getenv('AWS_SECRET_ACCESS_KEY'),
    'sender_email': os.getenv('AWS_SES_SENDER_EMAIL', 'noreply@tudominio.com')
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
    foto_base64: Optional[str] = None
    descripcion: Optional[str] = None
    tipo_reporte: Optional[str] = "general"
    fecha_inicio_evento: Optional[str] = None  # Para eventos culturales/deportivos
    fecha_fin_evento: Optional[str] = None     # Para eventos culturales/deportivos

class ReporteResponse(BaseModel):
    id: int
    latitud: float
    longitud: float
    timestamp: str
    foto_base64: str
    descripcion: Optional[str]
    tipo_reporte: str
    fecha_inicio_evento: Optional[str] = None
    fecha_fin_evento: Optional[str] = None

class LoginRequest(BaseModel):
    usuario: str
    clave: str

class LoginResponse(BaseModel):
    success: bool
    message: str
    usuario: Optional[str] = None
    numero_usuario: Optional[int] = None
    email: Optional[str] = None
    verificado: Optional[bool] = None

class UsuarioCreate(BaseModel):
    usuario: str
    clave: str
    nombres: str
    telefono: str
    correo: str

class UsuarioResponse(BaseModel):
    success: bool
    message: str
    usuario: Optional[str] = None
    numero_usuario: Optional[int] = None

class VerificationRequest(BaseModel):
    token: str

class VerificationResponse(BaseModel):
    success: bool
    message: str

class SendCodeRequest(BaseModel):
    email: EmailStr

class VerifyCodeRequest(BaseModel):
    codigo: str

class UserStatusResponse(BaseModel):
    nombre: str
    email: EmailStr
    verificado: bool
    estado_texto: str
    activo: Optional[int] = None
    success: bool = True

# --- Modelos para recuperación de usuario ---
class RecoverUserSendCodeRequest(BaseModel):
    email: EmailStr

class RecoverUserVerifyRequest(BaseModel):
    email: EmailStr
    codigo: str
    nueva_clave: str

class RecoverUserResponse(BaseModel):
    success: bool
    message: str
    usuario: Optional[str] = None
    email: Optional[EmailStr] = None

# --- Modelos para Aforo de Lugares de Interés ---
class AforoLugarCreate(BaseModel):
    """Modelo para recibir datos de aforo desde servidor de procesamiento de imágenes"""
    foto_base64: str
    timestamp: str
    aforo: int
    latitud: Optional[float] = None
    longitud: Optional[float] = None
    lugar_id: Optional[str] = None  # Identificador del lugar de interés

class AforoLugarResponse(BaseModel):
    success: bool
    message: str
    id: Optional[int] = None
    aforo: Optional[int] = None
    timestamp: Optional[str] = None

def get_db_connection():
    """Obtiene una conexión a la base de datos MySQL"""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

def hash_password(password: str) -> str:
    """Genera hash SHA-256 de la contraseña"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(plain: str, stored_hash: str) -> bool:
    """Verifica contraseña. Actualmente sólo SHA-256, deja hook para bcrypt futuro."""
    try:
        # Si longitud típica de sha256
        if len(stored_hash) == 64:
            return hash_password(plain) == stored_hash
        # Futuro: if stored_hash.startswith('$2b$'): usar bcrypt
        return False
    except Exception:
        return False

def is_valid_email(email: str) -> bool:
    """Valida el formato de un correo electrónico"""
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(email_pattern, email) is not None

# --- Variables globales de depuración ---
LAST_SENT_CODE: dict[str, dict] = {}

@app.get("/debug/ses")
async def debug_ses():
    """Verifica conectividad y límites de AWS SES."""
    try:
        if os.getenv('SKIP_EMAIL_VERIFICATION', '').lower() in ('1','true','yes'):
            return {"skip_mode": True, "message": "SKIP_EMAIL_VERIFICATION activo, no se prueba SES"}
        ses_client = boto3.client(
            'ses',
            region_name=AWS_CONFIG['region'],
            aws_access_key_id=AWS_CONFIG['access_key'],
            aws_secret_access_key=AWS_CONFIG['secret_key']
        )
        quota = ses_client.get_send_quota()
        idents = ses_client.list_identities(MaxItems=20)
        return {
            "skip_mode": False,
            "quota": quota,
            "identities_sample": idents.get('Identities', [])[:5],
            "region": AWS_CONFIG['region']
        }
    except ClientError as e:
        return {"error": e.response['Error'], "region": AWS_CONFIG['region']}
    except Exception as e:
        return {"error": str(e), "region": AWS_CONFIG['region']}

@app.get("/debug/ultimo-codigo/{email}")
async def debug_ultimo_codigo(email: str):
    data = LAST_SENT_CODE.get(email.lower())
    if not data:
        return {"found": False}
    return {"found": True, **data}

def generate_verification_token() -> str:
    """Genera un token único para verificación"""
    return str(uuid.uuid4())

def generate_verification_code() -> str:
    """Genera un código de verificación de 6 dígitos"""
    return ''.join(random.choices(string.digits, k=6))

def send_verification_email(email: str, token: str, base_url: str = "http://localhost:5000") -> bool:
    """Envía email de verificación usando AWS SES"""
    try:
        # Crear cliente de SES
        ses_client = boto3.client(
            'ses',
            region_name=AWS_CONFIG['region'],
            aws_access_key_id=AWS_CONFIG['access_key'],
            aws_secret_access_key=AWS_CONFIG['secret_key']
        )
        
        # URL de verificación
        verification_url = f"{base_url}/verificar-email?token={token}"
        
        # Contenido del email
        subject = "Verificación de Correo Electrónico - GPS Reporter"
        
        html_body = f"""
        <html>
        <head></head>
        <body>
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                <h2 style="color: #2563eb;">¡Bienvenido a GPS Reporter! 📍</h2>
                
                <p>Gracias por registrarte en nuestra aplicación de reportes GPS.</p>
                
                <p>Para completar tu registro y activar tu cuenta, por favor haz clic en el siguiente enlace:</p>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{verification_url}" 
                       style="background-color: #2563eb; color: white; padding: 12px 24px; 
                              text-decoration: none; border-radius: 6px; display: inline-block;">
                        ✅ Verificar mi correo electrónico
                    </a>
                </div>
                
                <p style="color: #666; font-size: 14px;">
                    Si no puedes hacer clic en el botón, copia y pega este enlace en tu navegador:
                    <br><a href="{verification_url}">{verification_url}</a>
                </p>
                
                <p style="color: #666; font-size: 12px; margin-top: 30px;">
                    Este enlace expira en 24 horas. Si no verificas tu cuenta en ese tiempo, 
                    deberás registrarte nuevamente.
                </p>
                
                <hr style="border: none; height: 1px; background-color: #eee; margin: 30px 0;">
                <p style="color: #999; font-size: 12px; text-align: center;">
                    GPS Reporter System - No responder a este correo
                </p>
            </div>
        </body>
        </html>
        """
        
        text_body = f"""
        ¡Bienvenido a GPS Reporter!
        
        Gracias por registrarte en nuestra aplicación de reportes GPS.
        
        Para completar tu registro y activar tu cuenta, visita el siguiente enlace:
        {verification_url}
        
        Este enlace expira en 24 horas.
        
        GPS Reporter System
        """
        
        # Enviar email
        response = ses_client.send_email(
            Source=AWS_CONFIG['sender_email'],
            Destination={'ToAddresses': [email]},
            Message={
                'Subject': {'Data': subject, 'Charset': 'UTF-8'},
                'Body': {
                    'Text': {'Data': text_body, 'Charset': 'UTF-8'},
                    'Html': {'Data': html_body, 'Charset': 'UTF-8'}
                }
            }
        )
        
        print(f"✅ Email de verificación enviado a {email}. Message ID: {response['MessageId']}")
        return True
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        error_message = e.response['Error']['Message']
        print(f"❌ Error enviando email: {error_code} - {error_message}")
        
        if error_code == 'MessageRejected':
            print("💡 Verifica que el email remitente esté verificado en AWS SES")
        elif error_code == 'InvalidParameterValue':
            print("💡 Verifica la configuración de AWS SES")
            
        return False
    except Exception as e:
        print(f"❌ Error inesperado enviando email: {e}")
        return False

def send_verification_code_email(email: str, codigo: str, usuario: str) -> bool:
    """Envía código de verificación de 6 dígitos por email"""
    try:
        # Permitir modo de desarrollo sin enviar correo real
        if os.getenv('SKIP_EMAIL_VERIFICATION', '').lower() in ('1', 'true', 'yes'):
            print(f"[DEV] SKIP_EMAIL_VERIFICATION activo. Se simula envío de código {codigo} a {email} (usuario={usuario}).")
            return True

        # Crear cliente de SES
        ses_client = boto3.client(
            'ses',
            region_name=AWS_CONFIG['region'],
            aws_access_key_id=AWS_CONFIG['access_key'],
            aws_secret_access_key=AWS_CONFIG['secret_key']
        )
        
        # Contenido del email
        subject = f"🔐 Código de Verificación - GPS Reporter: {codigo}"
        
        html_body = f"""
        <html>
        <head></head>
        <body>
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #2563eb; text-align: center;">🔐 Verificación de Cuenta</h2>
                
                <p>Hola <strong>{usuario}</strong>,</p>
                
                <p>Has solicitado verificar tu cuenta en GPS Reporter. Tu código de verificación es:</p>
                
                <div style="text-align: center; margin: 30px 0; padding: 20px; background: #f0f9ff; border-radius: 8px; border-left: 4px solid #2563eb;">
                    <h1 style="color: #2563eb; font-size: 36px; margin: 0; letter-spacing: 8px; font-family: 'Courier New', monospace;">
                        {codigo}
                    </h1>
                </div>
                
                <p style="color: #666; font-size: 14px;">
                    <strong>Instrucciones:</strong>
                    <br>1. Abre la aplicación GPS Reporter
                    <br>2. Ve a tu perfil
                    <br>3. Ingresa el código de 6 dígitos
                    <br>4. Tu cuenta será verificada automáticamente
                </p>
                
                <p style="color: #dc2626; font-size: 12px; margin-top: 30px;">
                    ⚠️ Este código expira en 15 minutos. No lo compartas con nadie.
                </p>
                
                <hr style="border: none; height: 1px; background-color: #eee; margin: 30px 0;">
                <p style="color: #999; font-size: 12px; text-align: center;">
                    GPS Reporter System - Código generado automáticamente
                </p>
            </div>
        </body>
        </html>
        """
        
        text_body = f"""
        🔐 Verificación de Cuenta - GPS Reporter
        
        Hola {usuario},
        
        Tu código de verificación es: {codigo}
        
        Instrucciones:
        1. Abre la aplicación GPS Reporter
        2. Ve a tu perfil  
        3. Ingresa el código de 6 dígitos
        4. Tu cuenta será verificada
        
        ⚠️ Este código expira en 15 minutos.
        
        GPS Reporter System
        """
        
        # Enviar email
        response = ses_client.send_email(
            Source=AWS_CONFIG['sender_email'],
            Destination={'ToAddresses': [email]},
            Message={
                'Subject': {'Data': subject, 'Charset': 'UTF-8'},
                'Body': {
                    'Text': {'Data': text_body, 'Charset': 'UTF-8'},
                    'Html': {'Data': html_body, 'Charset': 'UTF-8'}
                }
            }
        )
        
        print(f"✅ Código de verificación enviado a {email}. Message ID: {response['MessageId']}")
        return True
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        error_message = e.response['Error']['Message']
        print(f"❌ Error enviando código: {error_code} - {error_message}")
        return False
    except Exception as e:
        print(f"❌ Error inesperado enviando código: {e}")
        return False

def init_database():
    """Inicializa la base de datos MySQL creando las tablas si no existen"""
    conn = get_db_connection()
    if conn is None:
        print("Advertencia: No se pudo conectar a la base de datos en init_database(). La app arrancará sin acceso a DB.")
        return False
    cursor = None
    try:
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
            fecha_inicio_evento DATETIME NULL COMMENT 'Fecha y hora de inicio del evento',
            fecha_fin_evento DATETIME NULL COMMENT 'Fecha y hora de fin del evento',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INT AUTO_INCREMENT PRIMARY KEY,
            usuario VARCHAR(50) UNIQUE NOT NULL,
            clave_hash VARCHAR(64) NOT NULL,
            nombres VARCHAR(100) NULL,
            telefono VARCHAR(20) NULL,
            correo VARCHAR(255) NULL,
            activo TINYINT DEFAULT 1 COMMENT '1=registrado, 3=verificado',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP NULL,
            UNIQUE KEY idx_correo_unique (correo)
        )
        ''')

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS verification_tokens (
            id INT AUTO_INCREMENT PRIMARY KEY,
            usuario_id INT NOT NULL,
            token VARCHAR(255) UNIQUE NOT NULL,
            codigo VARCHAR(6) NULL COMMENT 'Código de 6 dígitos para verificación desde app',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP DEFAULT (CURRENT_TIMESTAMP + INTERVAL 24 HOUR),
            code_expires_at TIMESTAMP DEFAULT (CURRENT_TIMESTAMP + INTERVAL 15 MINUTE),
            used BOOLEAN DEFAULT FALSE,
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE,
            INDEX idx_token (token),
            INDEX idx_codigo (codigo),
            INDEX idx_expires (expires_at)
        )
        ''')

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS recovery_codes (
            id INT AUTO_INCREMENT PRIMARY KEY,
            usuario_id INT NOT NULL,
            codigo VARCHAR(6) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP DEFAULT (CURRENT_TIMESTAMP + INTERVAL 15 MINUTE),
            used BOOLEAN DEFAULT FALSE,
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE,
            INDEX idx_rec_codigo (codigo),
            INDEX idx_rec_expires (expires_at)
        )
        ''')

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS aforo_lugares (
            id INT AUTO_INCREMENT PRIMARY KEY,
            foto_ruta VARCHAR(500) NOT NULL COMMENT 'Ruta de la imagen procesada',
            timestamp_captura DATETIME NOT NULL COMMENT 'Timestamp de la captura original',
            aforo INT NOT NULL COMMENT 'Número de personas detectadas',
            latitud DECIMAL(10, 8) NULL,
            longitud DECIMAL(11, 8) NULL,
            lugar_id VARCHAR(100) NULL COMMENT 'Identificador del lugar de interés',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            INDEX idx_timestamp (timestamp_captura),
            INDEX idx_lugar (lugar_id),
            INDEX idx_aforo (aforo)
        )
        ''')

        cursor.execute("SELECT COUNT(*) as count FROM usuarios WHERE usuario = 'admin'")
        result = cursor.fetchone()
        if result and result[0] == 0:
            admin_password_hash = hash_password("admin123")
            cursor.execute('''
            INSERT INTO usuarios (usuario, clave_hash, nombres, telefono, correo, activo)
            VALUES (%s, %s, %s, %s, %s, %s)
            ''', ('admin', admin_password_hash, 'Administrador', '0000000000', 'admin@sistema.com', 3))
            print("✅ Usuario admin creado (usuario: admin, contraseña: admin123)")

        cursor.execute("SELECT COUNT(*) as count FROM usuarios WHERE usuario = 'usuario'")
        result = cursor.fetchone()
        if result and result[0] == 0:
            user_password_hash = hash_password("123456")
            cursor.execute('''
            INSERT INTO usuarios (usuario, clave_hash, nombres, telefono, correo, activo)
            VALUES (%s, %s, %s, %s, %s, %s)
            ''', ('usuario', user_password_hash, 'Usuario de prueba', '1111111111', 'usuario@test.com', 3))
            print("✅ Usuario 'usuario' creado (usuario: usuario, contraseña: 123456)")

        conn.commit()
        return True
    except Exception as e:
        print(f"Error inicializando la base de datos: {e}")
        return False
    finally:
        try:
            if cursor:
                cursor.close()
        except Exception:
            pass
        try:
            if conn:
                conn.close()
        except Exception:
            pass

def send_recovery_code_email(email: str, codigo: str) -> bool:
    """Envía email con código para recuperar nombre de usuario"""
    try:
        if os.getenv('SKIP_EMAIL_VERIFICATION', '').lower() in ('1','true','yes'):
            print(f"[DEV] SKIP_EMAIL_VERIFICATION activo. Simula envío código recuperación {codigo} -> {email}")
            return True
        ses_client = boto3.client(
            'ses',
            region_name=AWS_CONFIG['region'],
            aws_access_key_id=AWS_CONFIG['access_key'],
            aws_secret_access_key=AWS_CONFIG['secret_key']
        )
        subject = f"🔎 Recuperación de Usuario - Código: {codigo}"
        html_body = f"""
        <html><body style='font-family: Arial, sans-serif;'>
        <h2 style='color:#2563eb;'>Recuperación de Usuario</h2>
        <p>Has solicitado recuperar tu nombre de usuario en <strong>GPS Reporter</strong>.</p>
        <p>Tu código de recuperación es:</p>
        <div style='background:#f0f9ff;border-left:4px solid #2563eb;padding:16px;text-align:center;border-radius:6px;'>
            <span style='font-size:34px;letter-spacing:6px;font-family:Courier New,monospace;color:#2563eb;'>{codigo}</span>
        </div>
        <p style='font-size:13px;color:#555;'>Ingresa este código en la pantalla de recuperación para revelar tu usuario.</p>
        <p style='font-size:12px;color:#aa0000;'>El código expira en 15 minutos. Si no lo solicitaste, ignora este correo.</p>
        <hr><p style='font-size:11px;color:#999;'>GPS Reporter System</p>
        </body></html>
        """
        text_body = f"Recuperación de Usuario\n\nCódigo: {codigo}\nVálido 15 minutos."
        response = ses_client.send_email(
            Source=AWS_CONFIG['sender_email'],
            Destination={'ToAddresses':[email]},
            Message={
                'Subject': {'Data': subject,'Charset':'UTF-8'},
                'Body': {
                    'Text': {'Data': text_body,'Charset':'UTF-8'},
                    'Html': {'Data': html_body,'Charset':'UTF-8'}
                }
            }
        )
        print(f"✅ Código recuperación enviado a {email}. Message ID: {response['MessageId']}")
        return True
    except ClientError as e:
        print(f"❌ SES error recuperación: {e.response['Error']['Code']} - {e.response['Error']['Message']}")
        return False
    except Exception as e:
        print(f"❌ Error inesperado envío recuperación: {e}")
        return False
IMAGES_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "imagenes_reportes")
os.makedirs(IMAGES_FOLDER, exist_ok=True)

# Montar carpeta de imágenes como estáticos
app.mount("/imagenes_reportes", StaticFiles(directory=IMAGES_FOLDER), name="imagenes_reportes")

# Inicializar BD al iniciar
@app.on_event("startup")
async def startup_event():
    print("🚀 Servidor iniciado. Inicializando base de datos local MySQL...")

    if init_database():
        print("✅ Base de datos lista para usar")
    else:
        print("⚠️ No se pudo inicializar la base de datos. Revisa la configuración local de MySQL.")

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

@app.get("/debug/health")
async def debug_health():
    conn = get_db_connection()
    if conn is None:
        return {"database": False, "status": "DOWN"}
    try:
        cursor = conn.cursor(); cursor.execute("SELECT 1"); cursor.fetchone()
        cursor.close(); conn.close()
        return {"database": True, "status": "UP"}
    except Exception as e:
        return {"database": False, "error": str(e), "status": "DEGRADED"}

@app.get("/debug/user/{usuario}")
async def debug_user(usuario: str):
    conn = get_db_connection()
    if conn is None:
        raise HTTPException(status_code=500, detail="Sin conexión a BD")
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, usuario, correo, activo, created_at, last_login FROM usuarios WHERE usuario=%s", (usuario,))
        data = cursor.fetchone()
        cursor.close(); conn.close()
        if not data:
            raise HTTPException(status_code=404, detail="No encontrado")
        data['verificado'] = (data['activo'] == 3)
        return data
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """Endpoint de autenticación de usuarios"""
    try:
        # Validar que los campos no estén vacíos
        if not request.usuario or not request.clave:
            raise HTTPException(status_code=400, detail="Usuario y contraseña son requeridos")
        
        # Validar longitud mínima
        if len(request.usuario.strip()) < 2:
            raise HTTPException(status_code=400, detail="Usuario debe tener al menos 2 caracteres")
        
        if len(request.clave) < 3:
            raise HTTPException(status_code=400, detail="Contraseña debe tener al menos 3 caracteres")
        
        conn = get_db_connection()
        if conn is None:
            raise HTTPException(status_code=500, detail="Error de conexión a la base de datos")
        
        cursor = conn.cursor(dictionary=True)

        # Buscar usuario por nombre
        cursor.execute('''
        SELECT id, usuario, activo, correo, clave_hash
        FROM usuarios
        WHERE usuario = %s
        ''', (request.usuario.strip(),))
        usuario_db = cursor.fetchone()

        if not usuario_db:
            cursor.close(); conn.close()
            raise HTTPException(status_code=401, detail="Usuario no encontrado")

        # Verificar contraseña
        if not verify_password(request.clave, usuario_db['clave_hash']):
            cursor.close(); conn.close()
            raise HTTPException(status_code=401, detail="Contraseña incorrecta")

        # Determinar verificación
        verificado = (usuario_db['activo'] == 3)

        # Si verificado actualiza last_login
        if verificado:
            cursor.execute('''
            UPDATE usuarios SET last_login = CURRENT_TIMESTAMP WHERE id = %s
            ''', (usuario_db['id'],))
            conn.commit()

        numero_usuario = usuario_db['id']
        email_val = usuario_db['correo']

        cursor.close(); conn.close()

        return LoginResponse(
            success=True,
            message=(f"Bienvenido {usuario_db['usuario']}" if verificado else "Cuenta no verificada"),
            usuario=usuario_db['usuario'],
            numero_usuario=numero_usuario,
            email=email_val,
            verificado=verificado
        )
    
    except HTTPException:
        # Re-lanzar HTTPExceptions (errores de validación/autenticación)
        raise
    except Exception as e:
        # Error inesperado del servidor
        print(f"Error en login: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@app.post("/usuarios/crear", response_model=UsuarioResponse)
async def crear_usuario(request: UsuarioCreate):
    """Crear un nuevo usuario y devolver el identificador asignado automáticamente"""
    try:
        # Validaciones básicas
        if not request.usuario or not request.clave or not request.nombres or not request.telefono or not request.correo:
            raise HTTPException(status_code=400, detail="Todos los campos son requeridos")
        if len(request.usuario.strip()) < 3:
            raise HTTPException(status_code=400, detail="El usuario debe tener al menos 3 caracteres")
        if len(request.clave) < 3:
            raise HTTPException(status_code=400, detail="La contraseña debe tener al menos 3 caracteres")
        if len(request.telefono.strip()) < 6:
            raise HTTPException(status_code=400, detail="El teléfono no es válido")
        if not is_valid_email(request.correo.strip()):
            raise HTTPException(status_code=400, detail="El formato del correo electrónico no es válido")

        conn = get_db_connection()
        if conn is None:
            raise HTTPException(status_code=500, detail="Error de conexión a la base de datos")
        cursor = conn.cursor(dictionary=True)

        # Verificar que no exista el usuario
        cursor.execute('SELECT id FROM usuarios WHERE usuario = %s', (request.usuario.strip(),))
        if cursor.fetchone():
            cursor.close(); conn.close()
            raise HTTPException(status_code=409, detail="El usuario ya existe")
        
        # Verificar que no exista el correo electrónico
        cursor.execute('SELECT id FROM usuarios WHERE correo = %s', (request.correo.strip(),))
        if cursor.fetchone():
            cursor.close(); conn.close()
            raise HTTPException(status_code=409, detail="El correo electrónico ya está registrado")

        # Insertar usuario como no verificado (activo = 1)
        clave_hash = hash_password(request.clave)
        cursor.execute('''
        INSERT INTO usuarios (usuario, clave_hash, nombres, telefono, correo, activo)
        VALUES (%s, %s, %s, %s, %s, %s)
        ''', (request.usuario.strip(), clave_hash, request.nombres.strip(), request.telefono.strip(), request.correo.strip(), 1))

        conn.commit()
        nuevo_id = cursor.lastrowid
        
        # Generar token de verificación
        verification_token = generate_verification_token()
        cursor.execute('''
        INSERT INTO verification_tokens (usuario_id, token)
        VALUES (%s, %s)
        ''', (nuevo_id, verification_token))
        
        conn.commit()
        cursor.close(); conn.close()
        
        # Enviar email de verificación
        email_sent = send_verification_email(request.correo.strip(), verification_token)
        
        if email_sent:
            return UsuarioResponse(
                success=True, 
                message="Usuario creado. Revisa tu correo electrónico para verificar tu cuenta.", 
                usuario=request.usuario.strip(), 
                numero_usuario=nuevo_id
            )
        else:
            return UsuarioResponse(
                success=True, 
                message="Usuario creado, pero hubo un error enviando el email de verificación. Contacta al administrador.", 
                usuario=request.usuario.strip(), 
                numero_usuario=nuevo_id
            )
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error creando usuario: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@app.get("/verificar-email", response_class=HTMLResponse)
async def verificar_email_get(token: str):
    """Endpoint GET para verificar correo electrónico desde enlace"""
    try:
        conn = get_db_connection()
        if conn is None:
            return "<h1>Error: No se pudo conectar a la base de datos</h1>"
        
        cursor = conn.cursor(dictionary=True)
        
        # Buscar token válido
        cursor.execute('''
        SELECT vt.id, vt.usuario_id, vt.used, vt.expires_at, u.usuario, u.correo
        FROM verification_tokens vt
        JOIN usuarios u ON vt.usuario_id = u.id
        WHERE vt.token = %s AND vt.used = FALSE AND vt.expires_at > NOW()
        ''', (token,))
        
        token_data = cursor.fetchone()
        
        if not token_data:
            cursor.close(); conn.close()
            return """
            <html>
            <head><title>Verificación Fallida</title></head>
            <body style="font-family: Arial, sans-serif; text-align: center; padding: 50px;">
                <h1 style="color: #dc2626;">❌ Token de verificación inválido o expirado</h1>
                <p>El enlace de verificación no es válido o ha expirado.</p>
                <p>Por favor, regístrate nuevamente o contacta al administrador.</p>
            </body>
            </html>
            """
        
        # Marcar usuario como verificado
        cursor.execute('UPDATE usuarios SET activo = 3 WHERE id = %s', (token_data['usuario_id'],))
        
        # Marcar token como usado
        cursor.execute('UPDATE verification_tokens SET used = TRUE WHERE id = %s', (token_data['id'],))
        
        conn.commit()
        cursor.close(); conn.close()
        
        return f"""
        <html>
        <head><title>¡Verificación Exitosa!</title></head>
        <body style="font-family: Arial, sans-serif; text-align: center; padding: 50px;">
            <h1 style="color: #16a34a;">✅ ¡Cuenta verificada exitosamente!</h1>
            <p>Hola <strong>{token_data['usuario']}</strong>,</p>
            <p>Tu correo <strong>{token_data['correo']}</strong> ha sido verificado correctamente.</p>
            <p>Ya puedes iniciar sesión en la aplicación GPS Reporter.</p>
            
            <div style="margin-top: 30px; padding: 20px; background: #f0f9ff; border-radius: 8px;">
                <h3>🔐 Próximos pasos:</h3>
                <p>1. Abre la aplicación GPS Reporter</p>
                <p>2. Inicia sesión con tu usuario y contraseña</p>
                <p>3. ¡Comienza a crear reportes!</p>
            </div>
        </body>
        </html>
        """
        
    except Exception as e:
        return f"<h1>Error: {str(e)}</h1>"

@app.post("/verificar-email", response_model=VerificationResponse)
async def verificar_email_post(request: VerificationRequest):
    """Endpoint POST para verificar correo electrónico"""
    try:
        conn = get_db_connection()
        if conn is None:
            raise HTTPException(status_code=500, detail="Error de conexión a la base de datos")
        
        cursor = conn.cursor(dictionary=True)
        
        # Buscar token válido
        cursor.execute('''
        SELECT vt.id, vt.usuario_id, vt.used, vt.expires_at, u.usuario
        FROM verification_tokens vt
        JOIN usuarios u ON vt.usuario_id = u.id
        WHERE vt.token = %s AND vt.used = FALSE AND vt.expires_at > NOW()
        ''', (request.token,))
        
        token_data = cursor.fetchone()
        
        if not token_data:
            cursor.close(); conn.close()
            raise HTTPException(status_code=400, detail="Token de verificación inválido o expirado")
        
        # Marcar usuario como verificado
        cursor.execute('UPDATE usuarios SET activo = 3 WHERE id = %s', (token_data['usuario_id'],))
        
        # Marcar token como usado
        cursor.execute('UPDATE verification_tokens SET used = TRUE WHERE id = %s', (token_data['id'],))
        
        conn.commit()
        cursor.close(); conn.close()
        
        return VerificationResponse(
            success=True, 
            message=f"Cuenta verificada exitosamente. ¡Bienvenido {token_data['usuario']}!"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")

@app.post("/reenviar-verificacion")
async def reenviar_verificacion(request: LoginRequest):
    """Reenviar correo de verificación para usuarios no verificados"""
    try:
        conn = get_db_connection()
        if conn is None:
            raise HTTPException(status_code=500, detail="Error de conexión a la base de datos")
        
        cursor = conn.cursor(dictionary=True)
        
        # Buscar usuario no verificado
        cursor.execute('''
        SELECT id, usuario, correo, activo
        FROM usuarios
        WHERE usuario = %s AND activo = 1
        ''', (request.usuario.strip(),))
        
        usuario_db = cursor.fetchone()
        
        if not usuario_db:
            cursor.close(); conn.close()
            raise HTTPException(status_code=404, detail="Usuario no encontrado o ya verificado")
        
        # Verificar contraseña
        clave_hash = hash_password(request.clave)
        cursor.execute('''
        SELECT id FROM usuarios
        WHERE id = %s AND clave_hash = %s
        ''', (usuario_db['id'], clave_hash))
        
        if not cursor.fetchone():
            cursor.close(); conn.close()
            raise HTTPException(status_code=401, detail="Contraseña incorrecta")
        
        # Invalidar tokens anteriores
        cursor.execute('''
        UPDATE verification_tokens 
        SET used = TRUE 
        WHERE usuario_id = %s AND used = FALSE
        ''', (usuario_db['id'],))
        
        # Generar nuevo token
        verification_token = generate_verification_token()
        cursor.execute('''
        INSERT INTO verification_tokens (usuario_id, token)
        VALUES (%s, %s)
        ''', (usuario_db['id'], verification_token))
        
        conn.commit()
        cursor.close(); conn.close()
        
        # Enviar email
        email_sent = send_verification_email(usuario_db['correo'], verification_token)
        
        if email_sent:
            return {"success": True, "message": "Correo de verificación reenviado. Revisa tu bandeja de entrada."}
        else:
            return {"success": False, "message": "Error enviando el correo. Intenta más tarde."}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")

# Endpoint para enviar código de verificación de 6 dígitos
@app.post("/enviar-codigo")
async def enviar_codigo_verificacion(request: SendCodeRequest):
    connection = None
    cursor = None
    
    try:
        # Conectar a la base de datos
        connection = get_db_connection()
        if connection is None:
            raise HTTPException(status_code=500, detail="Error de conexión a la base de datos")
        
        if not is_valid_email(request.email):
            raise HTTPException(status_code=400, detail="Formato de email inválido")

        cursor = connection.cursor()
        
        # Verificar que el usuario existe y no está verificado (obtenemos también el nombre de usuario para personalizar el correo)
        cursor.execute("SELECT id, activo, usuario FROM usuarios WHERE correo = %s", (request.email,))
        user = cursor.fetchone()
        
        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
        user_id, activo, usuario_nombre = user
        
        if activo == 3:
            raise HTTPException(status_code=400, detail="El usuario ya está verificado")
        
        # Generar código de 6 dígitos
        codigo = generate_verification_code()
        
        # Limpiar códigos anteriores no usados para este usuario
        cursor.execute("DELETE FROM verification_tokens WHERE usuario_id = %s AND codigo IS NOT NULL", (user_id,))
        
        # Crear nuevo token con código
        token = str(uuid.uuid4())
        cursor.execute("""
            INSERT INTO verification_tokens (usuario_id, token, codigo, expires_at, code_expires_at)
            VALUES (%s, %s, %s, DATE_ADD(NOW(), INTERVAL 24 HOUR), DATE_ADD(NOW(), INTERVAL 15 MINUTE))
        """, (user_id, token, codigo))
        
        connection.commit()

        # Guardar en memoria para depuración
        LAST_SENT_CODE[request.email.lower()] = {
            "codigo": codigo,
            "generado_at": datetime.utcnow().isoformat() + 'Z',
            "usuario_id": user_id,
            "usuario": usuario_nombre
        }
        
        # Enviar email con código (incluyendo el nombre de usuario para el saludo)
        email_ok = send_verification_code_email(request.email, codigo, usuario_nombre)
        if not email_ok:
            # Si falla el envío devolvemos 500 para que el cliente no muestre falso positivo
            raise HTTPException(status_code=500, detail="Fallo al enviar correo (ver logs SES / configura SKIP_EMAIL_VERIFICATION=1 para pruebas)")
        
        return {
            "success": True,
            "message": "Código de verificación enviado correctamente",
            "expires_in_minutes": 15,
            "email": request.email,
            "usuario": usuario_nombre
        }
        
    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=f"Error de base de datos: {err}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

# ------------------ Recuperación de Usuario ------------------
@app.post("/recuperar-usuario/enviar-codigo", response_model=RecoverUserResponse)
async def recuperar_usuario_enviar_codigo(request: RecoverUserSendCodeRequest):
    if not is_valid_email(request.email):
        raise HTTPException(status_code=400, detail="Formato de email inválido")
    conn = get_db_connection()
    if conn is None:
        raise HTTPException(status_code=500, detail="Error de conexión a la base de datos")
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id FROM usuarios WHERE correo=%s", (request.email,))
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Email no registrado")
        usuario_id = row[0]
        # Limpiar códigos anteriores no usados
        cursor.execute("DELETE FROM recovery_codes WHERE usuario_id=%s AND used=FALSE", (usuario_id,))
        codigo = generate_verification_code()
        cursor.execute("""
            INSERT INTO recovery_codes (usuario_id, codigo, expires_at)
            VALUES (%s, %s, DATE_ADD(NOW(), INTERVAL 15 MINUTE))
        """, (usuario_id, codigo))
        conn.commit()
        ok = send_recovery_code_email(request.email, codigo)
        if not ok:
            raise HTTPException(status_code=500, detail="No se pudo enviar el correo (SES)")
        return RecoverUserResponse(success=True, message="Código enviado a tu correo", email=request.email)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {e}")
    finally:
        cursor.close(); conn.close()

@app.post("/recuperar-usuario/verificar", response_model=RecoverUserResponse)
async def recuperar_usuario_verificar(request: RecoverUserVerifyRequest):
    if not is_valid_email(request.email):
        raise HTTPException(status_code=400, detail="Formato de email inválido")
    if not (len(request.codigo) == 6 and request.codigo.isdigit()):
        raise HTTPException(status_code=400, detail="Código inválido")
    if not request.nueva_clave or len(request.nueva_clave) < 6:
        raise HTTPException(status_code=400, detail="La nueva contraseña debe tener al menos 6 caracteres")
    conn = get_db_connection()
    if conn is None:
        raise HTTPException(status_code=500, detail="Error de conexión a la base de datos")
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT rc.id, u.usuario, rc.used, u.id
            FROM recovery_codes rc
            JOIN usuarios u ON rc.usuario_id = u.id
            WHERE u.correo=%s AND rc.codigo=%s AND rc.expires_at > NOW() AND rc.used = FALSE
        """, (request.email, request.codigo))
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=400, detail="Código inválido o expirado")
        rec_id, usuario, used, usuario_id = row
        # Marcar código como usado
        cursor.execute("UPDATE recovery_codes SET used=TRUE WHERE id=%s", (rec_id,))
        # Actualizar contraseña del usuario usando la columna correcta clave_hash
        hashed = hash_password(request.nueva_clave)
        cursor.execute("UPDATE usuarios SET clave_hash=%s WHERE id=%s", (hashed, usuario_id))
        conn.commit()
        return RecoverUserResponse(success=True, message="Contraseña actualizada y usuario recuperado", usuario=usuario, email=request.email)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {e}")
    finally:
        cursor.close(); conn.close()

# Endpoint para verificar código de 6 dígitos
@app.post("/verificar-codigo")
async def verificar_codigo(request: VerifyCodeRequest):
    connection = None
    cursor = None
    
    try:
        # Conectar a la base de datos
        connection = get_db_connection()
        if connection is None:
            raise HTTPException(status_code=500, detail="Error de conexión a la base de datos")
        
        cursor = connection.cursor()
        
        # Buscar el código
        cursor.execute("""
            SELECT vt.id, vt.usuario_id, vt.used, u.correo
            FROM verification_tokens vt
            JOIN usuarios u ON vt.usuario_id = u.id
            WHERE vt.codigo = %s AND vt.code_expires_at > NOW() AND vt.used = FALSE
        """, (request.codigo,))
        
        token_data = cursor.fetchone()
        
        if not token_data:
            raise HTTPException(status_code=400, detail="Código inválido o expirado")
        
        token_id, user_id, used, email = token_data
        
        # Marcar el token como usado
        cursor.execute("UPDATE verification_tokens SET used = TRUE WHERE id = %s", (token_id,))
        
        # Activar el usuario
        cursor.execute("UPDATE usuarios SET activo = 3 WHERE id = %s", (user_id,))
        
        connection.commit()
        
        return {
            "success": True,
            "message": "Usuario verificado correctamente",
            "email": email,
            "activo": 3,
            "verificado": True
        }
        
    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=f"Error de base de datos: {err}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

# Endpoint para obtener estado del usuario
@app.get("/usuario-estado/{email}")
async def obtener_estado_usuario(email: str):
    connection = None
    cursor = None
    
    try:
        # Conectar a la base de datos
        connection = get_db_connection()
        if connection is None:
            raise HTTPException(status_code=500, detail="Error de conexión a la base de datos")
        
        cursor = connection.cursor()
        
        # Obtener información del usuario
        cursor.execute("SELECT nombres, activo FROM usuarios WHERE correo = %s", (email,))
        user = cursor.fetchone()
        
        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
        nombre, activo = user
        
        return UserStatusResponse(
            nombre=nombre,
            email=email,
            verificado=(activo == 3),
            estado_texto="Usuario Verificado" if activo == 3 else "Usuario No Verificado",
            activo=activo,
            success=True
        )
        
    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=f"Error de base de datos: {err}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

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
    """Crear un nuevo reporte, guardar imagen en disco y ruta en la base de datos"""
    try:
        print(f"\n🔵 Recibiendo nuevo reporte...")
        print(f"   timestamp recibido: {reporte.timestamp}")
        
        # Si no hay timestamp, usar actual en zona horaria de Bogotá
        if not reporte.timestamp:
            current_time = datetime.now(ZoneInfo("America/Bogota")).replace(tzinfo=None)
            print(f"   ✅ timestamp generado (hora actual Bogotá): {current_time}")
        else:
            try:
                # La app envía timestamp en hora local (Bogotá) sin timezone
                # Formato: YYYY-MM-DDTHH:mm:ss
                timestamp_str = reporte.timestamp.replace('Z', '').strip()
                current_time = datetime.fromisoformat(timestamp_str)
                print(f"   ✅ timestamp parseado (hora Bogotá): {current_time}")
            except (ValueError, AttributeError) as e:
                # Si falla el parseo, usar hora actual de Bogotá
                print(f"   ⚠️ Error parseando timestamp '{reporte.timestamp}': {e}")
                current_time = datetime.now(ZoneInfo("America/Bogota")).replace(tzinfo=None)
                print(f"   ✅ usando hora actual Bogotá: {current_time}")

        conn = get_db_connection()
        if conn is None:
            raise HTTPException(status_code=500, detail="Error de conexión a la base de datos")
        cursor = conn.cursor(dictionary=True)

        # Obtener el próximo ID
        cursor.execute("SELECT MAX(id) as max_id FROM reportes")
        row = cursor.fetchone()
        next_id = (row["max_id"] or 0) + 1

        # Guardar imagen en disco y obtener ruta
        ruta_imagen = ""
        if reporte.foto_base64:
            try:
                image_data = base64.b64decode(reporte.foto_base64)
                image = Image.open(BytesIO(image_data))
                
                # Convertir a RGB si tiene transparencia (RGBA, LA, P con transparencia)
                if image.mode in ('RGBA', 'LA', 'P'):
                    print(f"  🎨 Imagen con transparencia detectada (modo {image.mode}), convirtiendo a RGB...")
                    # Crear fondo blanco
                    rgb_image = Image.new('RGB', image.size, (255, 255, 255))
                    # Si tiene canal alfa, hacer composición
                    if image.mode == 'RGBA':
                        rgb_image.paste(image, mask=image.split()[3])  # Usar canal alfa como máscara
                    elif image.mode == 'LA':
                        rgb_image.paste(image, mask=image.split()[1])  # Usar canal alfa como máscara
                    else:  # Modo P (palette)
                        rgb_image.paste(image.convert('RGBA'))
                    image = rgb_image
                    print(f"  ✅ Imagen convertida a RGB")
                
                image_filename = f"{next_id}.jpg"
                image_path = os.path.join(IMAGES_FOLDER, image_filename)
                image.save(image_path, format="JPEG", quality=85)
                ruta_imagen = f"imagenes_reportes/{image_filename}"
                print(f"  💾 Imagen guardada: {image_filename}")
            except Exception as img_err:
                print(f"  ❌ Error procesando imagen: {img_err}")
                raise HTTPException(status_code=400, detail=f"Error al procesar la imagen: {img_err}")

        # Asegurar que latitud y longitud sean float con precisión correcta
        lat = round(float(reporte.latitud), 8)
        lng = round(float(reporte.longitud), 8)

        # Procesar fechas de evento si es un evento cultural o deportivo
        fecha_inicio = None
        fecha_fin = None
        
        # Debug: Imprimir tipo de reporte recibido
        print(f"📋 Tipo de reporte recibido: '{reporte.tipo_reporte}'")
        print(f"   fecha_inicio_evento: {reporte.fecha_inicio_evento}")
        print(f"   fecha_fin_evento: {reporte.fecha_fin_evento}")
        
        if reporte.tipo_reporte in ['Eventos Culturales', 'Eventos Deportivos']:
            print(f"✓ Es un evento cultural/deportivo, procesando fechas...")
            
            if reporte.fecha_inicio_evento:
                try:
                    # La app envía fechas en hora local (Bogotá) sin timezone
                    # Formato: YYYY-MM-DDTHH:mm:ss
                    fecha_inicio_str = reporte.fecha_inicio_evento.replace('Z', '').strip()
                    fecha_inicio = datetime.fromisoformat(fecha_inicio_str)
                    print(f"  ✅ fecha_inicio procesada (hora Bogotá): {fecha_inicio}")
                except Exception as e:
                    print(f"  ❌ Error procesando fecha_inicio_evento '{reporte.fecha_inicio_evento}': {e}")
                    fecha_inicio = None
            else:
                print(f"  ⚠️  fecha_inicio_evento es None/vacía")
            
            if reporte.fecha_fin_evento:
                try:
                    # La app envía fechas en hora local (Bogotá) sin timezone
                    # Formato: YYYY-MM-DDTHH:mm:ss
                    fecha_fin_str = reporte.fecha_fin_evento.replace('Z', '').strip()
                    fecha_fin = datetime.fromisoformat(fecha_fin_str)
                    print(f"  ✅ fecha_fin procesada (hora Bogotá): {fecha_fin}")
                except Exception as e:
                    print(f"  ❌ Error procesando fecha_fin_evento '{reporte.fecha_fin_evento}': {e}")
                    fecha_fin = None
            else:
                print(f"  ⚠️  fecha_fin_evento es None/vacía")
        else:
            print(f"✗ No es un evento, tipo_reporte no coincide con 'Eventos Culturales' o 'Eventos Deportivos'")

        # Guardar en la base de datos (la ruta en la columna foto_base64)
        cursor.execute('''
        INSERT INTO reportes (latitud, longitud, timestamp, foto_base64, descripcion, tipo_reporte, fecha_inicio_evento, fecha_fin_evento)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        ''', (
            lat,
            lng,
            current_time,
            ruta_imagen,
            reporte.descripcion or None,
            reporte.tipo_reporte or 'general',
            fecha_inicio,
            fecha_fin
        ))
        reporte_id = cursor.lastrowid
        conn.commit()
        cursor.close()
        conn.close()

        print(f"✅ Reporte {reporte_id} guardado exitosamente")
        print(f"   Timestamp en BD: {current_time}")
        print(f"   Fecha inicio: {fecha_inicio}")
        print(f"   Fecha fin: {fecha_fin}\n")

        return ReporteResponse(
            id=reporte_id,
            latitud=lat,
            longitud=lng,
            timestamp=current_time.isoformat(),
            foto_base64=ruta_imagen,
            descripcion=reporte.descripcion,
            tipo_reporte=reporte.tipo_reporte or 'general',
            fecha_inicio_evento=fecha_inicio.isoformat() if fecha_inicio else None,
            fecha_fin_evento=fecha_fin.isoformat() if fecha_fin else None
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f"\n❌ ERROR CRÍTICO en crear_reporte:")
        print(f"   Tipo de error: {type(e).__name__}")
        print(f"   Mensaje: {str(e)}")
        import traceback
        print(f"   Traceback:\n{traceback.format_exc()}")
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
        SELECT id, latitud, longitud, timestamp, foto_base64, descripcion, tipo_reporte, 
               fecha_inicio_evento, fecha_fin_evento
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
            
            # Manejar fechas de eventos
            fecha_inicio = None
            fecha_fin = None
            
            if row["fecha_inicio_evento"]:
                if isinstance(row["fecha_inicio_evento"], datetime):
                    fecha_inicio = row["fecha_inicio_evento"].isoformat()
                else:
                    try:
                        fecha_inicio = datetime.fromisoformat(str(row["fecha_inicio_evento"])).isoformat()
                    except (ValueError, AttributeError):
                        fecha_inicio = None
            
            if row["fecha_fin_evento"]:
                if isinstance(row["fecha_fin_evento"], datetime):
                    fecha_fin = row["fecha_fin_evento"].isoformat()
                else:
                    try:
                        fecha_fin = datetime.fromisoformat(str(row["fecha_fin_evento"])).isoformat()
                    except (ValueError, AttributeError):
                        fecha_fin = None
            
            reportes.append(ReporteResponse(
                id=int(row["id"]),
                latitud=lat,
                longitud=lng,
                timestamp=timestamp,
                foto_base64=row["foto_base64"] or "",  # Evitar None en foto_base64
                descripcion=row["descripcion"] or "",  # Convertir None a string vacío
                tipo_reporte=row["tipo_reporte"] or "general",  # Usar valor por defecto si es None
                fecha_inicio_evento=fecha_inicio,
                fecha_fin_evento=fecha_fin
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

# Endpoint adicional para gestión de usuarios (opcional)
@app.get("/usuarios/info")
async def info_usuarios():
    """Información sobre usuarios registrados (solo para debugging)"""
    try:
        conn = get_db_connection()
        if conn is None:
            raise HTTPException(status_code=500, detail="Error de conexión a la base de datos")
            
        cursor = conn.cursor(dictionary=True)
        cursor.execute('''
        SELECT usuario, correo, activo, created_at, last_login 
        FROM usuarios 
        WHERE activo = TRUE
        ORDER BY created_at DESC
        ''')
        
        usuarios = []
        for row in cursor:
            usuarios.append({
                "usuario": row["usuario"],
                "correo": row["correo"],
                "activo": row["activo"],
                "created_at": row["created_at"].isoformat() if row["created_at"] else None,
                "last_login": row["last_login"].isoformat() if row["last_login"] else None
            })
        
        cursor.close()
        conn.close()
        
        return {"usuarios": usuarios}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

# --- Endpoints para Aforo de Lugares de Interés ---

@app.post("/aforo/registrar", response_model=AforoLugarResponse)
async def registrar_aforo(data: AforoLugarCreate):
    """
    Endpoint para recibir datos de aforo desde el servidor de procesamiento de imágenes
    URL: http://TU-SERVIDOR-PRINCIPAL:5000/aforo/registrar
    """
    try:
        # Validaciones
        if not data.foto_base64:
            raise HTTPException(status_code=400, detail="foto_base64 es requerida")
        
        if not data.timestamp:
            raise HTTPException(status_code=400, detail="timestamp es requerido")
        
        if data.aforo < 0:
            raise HTTPException(status_code=400, detail="aforo debe ser mayor o igual a 0")
        
        # Parsear timestamp y convertir a zona horaria de Bogotá
        try:
            timestamp_dt = datetime.fromisoformat(data.timestamp.replace('Z', '+00:00'))
            # Si el timestamp no tiene zona horaria, asumimos UTC y convertimos a Bogotá
            if timestamp_dt.tzinfo is None:
                timestamp_dt = timestamp_dt.replace(tzinfo=ZoneInfo("UTC")).astimezone(ZoneInfo("America/Bogota"))
            else:
                # Si ya tiene zona horaria, convertir a Bogotá
                timestamp_dt = timestamp_dt.astimezone(ZoneInfo("America/Bogota"))
            # Remover info de zona horaria para almacenar en MySQL (guardar como hora local de Bogotá)
            timestamp_dt = timestamp_dt.replace(tzinfo=None)
        except ValueError:
            raise HTTPException(status_code=400, detail="Formato de timestamp inválido. Use ISO 8601")
        
        conn = get_db_connection()
        if conn is None:
            raise HTTPException(status_code=500, detail="Error de conexión a la base de datos")
        
        cursor = conn.cursor(dictionary=True)
        
        # Obtener próximo ID para nombre de archivo
        cursor.execute("SELECT MAX(id) as max_id FROM aforo_lugares")
        row = cursor.fetchone()
        next_id = (row["max_id"] or 0) + 1
        
        # Guardar imagen en carpeta específica
        aforo_folder = os.path.join(IMAGES_FOLDER, "aforo")
        os.makedirs(aforo_folder, exist_ok=True)
        
        try:
            # Decodificar y guardar imagen
            image_data = base64.b64decode(data.foto_base64)
            image = Image.open(BytesIO(image_data))
            image_filename = f"aforo_{next_id}_{data.lugar_id or 'general'}.jpg"
            image_path = os.path.join(aforo_folder, image_filename)
            image.save(image_path, format="JPEG", quality=85)
            
            # Ruta relativa para almacenar en BD
            foto_ruta = f"imagenes_reportes/aforo/{image_filename}"
            
        except Exception as img_err:
            raise HTTPException(status_code=400, detail=f"Error procesando imagen: {str(img_err)}")
        
        # Insertar en base de datos
        cursor.execute('''
        INSERT INTO aforo_lugares 
        (foto_ruta, timestamp_captura, aforo, latitud, longitud, lugar_id)
        VALUES (%s, %s, %s, %s, %s, %s)
        ''', (
            foto_ruta,
            timestamp_dt,
            data.aforo,
            data.latitud,
            data.longitud,
            data.lugar_id
        ))
        
        aforo_id = cursor.lastrowid
        conn.commit()
        cursor.close()
        conn.close()
        
        print(f"✅ Aforo registrado: ID={aforo_id}, Aforo={data.aforo}, Lugar={data.lugar_id or 'N/A'}")
        
        return AforoLugarResponse(
            success=True,
            message=f"Aforo registrado exitosamente. {data.aforo} persona(s) detectada(s)",
            id=aforo_id,
            aforo=data.aforo,
            timestamp=timestamp_dt.isoformat()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error registrando aforo: {e}")
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

@app.get("/aforo/historial")
async def obtener_historial_aforo(
    lugar_id: Optional[str] = None,
    limite: int = 50,
    orden: str = "desc"
):
    """
    Obtener historial de aforo
    Parámetros:
    - lugar_id: Filtrar por lugar específico (opcional)
    - limite: Número máximo de registros (default: 50)
    - orden: 'asc' o 'desc' (default: 'desc')
    """
    try:
        if limite > 500:
            limite = 500  # Límite máximo de seguridad
        
        orden_sql = "DESC" if orden.lower() == "desc" else "ASC"
        
        conn = get_db_connection()
        if conn is None:
            raise HTTPException(status_code=500, detail="Error de conexión a la base de datos")
        
        cursor = conn.cursor(dictionary=True)
        
        # Construir query
        if lugar_id:
            cursor.execute(f'''
            SELECT id, foto_ruta, timestamp_captura, aforo, latitud, longitud, lugar_id, created_at
            FROM aforo_lugares
            WHERE lugar_id = %s
            ORDER BY timestamp_captura {orden_sql}
            LIMIT %s
            ''', (lugar_id, limite))
        else:
            cursor.execute(f'''
            SELECT id, foto_ruta, timestamp_captura, aforo, latitud, longitud, lugar_id, created_at
            FROM aforo_lugares
            ORDER BY timestamp_captura {orden_sql}
            LIMIT %s
            ''', (limite,))
        
        registros = []
        for row in cursor:
            registros.append({
                "id": row["id"],
                "foto_ruta": row["foto_ruta"],
                "timestamp_captura": row["timestamp_captura"].isoformat() if row["timestamp_captura"] else None,
                "aforo": row["aforo"],
                "latitud": float(row["latitud"]) if row["latitud"] else None,
                "longitud": float(row["longitud"]) if row["longitud"] else None,
                "lugar_id": row["lugar_id"],
                "created_at": row["created_at"].isoformat() if row["created_at"] else None
            })
        
        cursor.close()
        conn.close()
        
        return {
            "success": True,
            "total": len(registros),
            "registros": registros
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.get("/aforo/estadisticas")
async def obtener_estadisticas_aforo(lugar_id: Optional[str] = None):
    """
    Obtener estadísticas de aforo
    Parámetros:
    - lugar_id: Estadísticas de un lugar específico (opcional)
    """
    try:
        conn = get_db_connection()
        if conn is None:
            raise HTTPException(status_code=500, detail="Error de conexión a la base de datos")
        
        cursor = conn.cursor(dictionary=True)
        
        # Estadísticas globales o por lugar
        if lugar_id:
            cursor.execute('''
            SELECT 
                COUNT(*) as total_registros,
                AVG(aforo) as aforo_promedio,
                MAX(aforo) as aforo_maximo,
                MIN(aforo) as aforo_minimo,
                MAX(timestamp_captura) as ultimo_registro
            FROM aforo_lugares
            WHERE lugar_id = %s
            ''', (lugar_id,))
        else:
            cursor.execute('''
            SELECT 
                COUNT(*) as total_registros,
                AVG(aforo) as aforo_promedio,
                MAX(aforo) as aforo_maximo,
                MIN(aforo) as aforo_minimo,
                MAX(timestamp_captura) as ultimo_registro,
                COUNT(DISTINCT lugar_id) as total_lugares
            FROM aforo_lugares
            ''')
        
        stats = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        return {
            "success": True,
            "lugar_id": lugar_id,
            "estadisticas": {
                "total_registros": stats["total_registros"] or 0,
                "aforo_promedio": round(float(stats["aforo_promedio"] or 0), 2),
                "aforo_maximo": stats["aforo_maximo"] or 0,
                "aforo_minimo": stats["aforo_minimo"] or 0,
                "ultimo_registro": stats["ultimo_registro"].isoformat() if stats.get("ultimo_registro") else None,
                "total_lugares": stats.get("total_lugares", 1 if lugar_id else 0)
            }
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
    print("🔐 Login endpoint: POST /login")
    uvicorn.run(app, host="0.0.0.0", port=5000, reload=True)