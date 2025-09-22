from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Optional
import json
from datetime import datetime
import hashlib

# Crear la aplicación FastAPI
app = FastAPI(
    title="Reportes GPS API - Test Login",
    description="API de prueba para testing del login",
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

# Modelos de login
class LoginRequest(BaseModel):
    usuario: str
    clave: str

class LoginResponse(BaseModel):
    success: bool
    message: str
    usuario: Optional[str] = None

def hash_password(password: str) -> str:
    """Genera hash SHA-256 de la contraseña"""
    return hashlib.sha256(password.encode()).hexdigest()

# Usuarios en memoria para prueba
USUARIOS_PRUEBA = {
    "admin": {
        "clave_hash": hash_password("admin123"),
        "activo": True
    },
    "usuario": {
        "clave_hash": hash_password("123456"),
        "activo": True
    }
}

@app.get("/", response_class=HTMLResponse)
async def root():
    return """
    <html>
        <head><title>API Test Login</title></head>
        <body>
            <h1>🔐 API Test Login</h1>
            <p>Servidor de prueba para verificar funcionalidad de login</p>
            <ul>
                <li><a href="/docs">📚 Documentación Swagger</a></li>
            </ul>
            <div style="margin-top: 30px; padding: 20px; background: #f0f8ff; border-radius: 8px;">
                <h3>🔐 Credenciales de prueba:</h3>
                <p><strong>Usuario:</strong> admin | <strong>Contraseña:</strong> admin123</p>
                <p><strong>Usuario:</strong> usuario | <strong>Contraseña:</strong> 123456</p>
            </div>
            <div style="margin-top: 20px; padding: 15px; background: #e8f5e8; border-radius: 8px;">
                <h4>🧪 Prueba del endpoint:</h4>
                <code>curl -X POST "http://localhost:5001/login" -H "Content-Type: application/json" -d '{"usuario":"admin","clave":"admin123"}'</code>
            </div>
        </body>
    </html>
    """

@app.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """Endpoint de autenticación de usuarios - VERSION DE PRUEBA"""
    try:
        # Validar que los campos no estén vacíos
        if not request.usuario or not request.clave:
            raise HTTPException(status_code=400, detail="Usuario y contraseña son requeridos")
        
        # Validar longitud mínima
        if len(request.usuario.strip()) < 2:
            raise HTTPException(status_code=400, detail="Usuario debe tener al menos 2 caracteres")
        
        if len(request.clave) < 3:
            raise HTTPException(status_code=400, detail="Contraseña debe tener al menos 3 caracteres")
        
        usuario_limpio = request.usuario.strip()
        
        # Verificar si el usuario existe en nuestra base de datos en memoria
        if usuario_limpio in USUARIOS_PRUEBA:
            usuario_data = USUARIOS_PRUEBA[usuario_limpio]
            
            # Verificar si está activo
            if not usuario_data["activo"]:
                raise HTTPException(status_code=401, detail="Usuario desactivado")
            
            # Generar hash de la contraseña proporcionada
            clave_hash = hash_password(request.clave)
            
            # Verificar contraseña
            if clave_hash == usuario_data["clave_hash"]:
                return LoginResponse(
                    success=True,
                    message=f"Bienvenido {usuario_limpio}",
                    usuario=usuario_limpio
                )
            else:
                # Contraseña incorrecta
                raise HTTPException(status_code=401, detail="Contraseña incorrecta")
        else:
            # Usuario no existe
            raise HTTPException(status_code=401, detail="Usuario no encontrado")
    
    except HTTPException:
        # Re-lanzar HTTPExceptions (errores de validación/autenticación)
        raise
    except Exception as e:
        # Error inesperado del servidor
        print(f"Error en login: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

if __name__ == "__main__":
    import uvicorn
    print("🚀 Iniciando servidor de prueba...")
    print("📍 API: http://localhost:5001")
    print("📚 Docs: http://localhost:5001/docs")
    print("🔐 Login endpoint: POST /login")
    print("\n🧪 Prueba con:")
    print('curl -X POST "http://localhost:5001/login" -H "Content-Type: application/json" -d \'{"usuario":"admin","clave":"admin123"}\'')
    uvicorn.run(app, host="0.0.0.0", port=5001, reload=False)