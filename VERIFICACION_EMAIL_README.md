# Sistema de Verificación por Email - GPS Reporter

## 🎯 ¿Qué se implementó?

Un sistema completo de verificación de usuarios por correo electrónico usando AWS SES (Simple Email Service) con las siguientes características:

### ✅ Funcionalidades Implementadas

1. **Registro con verificación obligatoria**
   - Usuario se registra con correo electrónico
   - Estado inicial: `activo = 1` (no verificado)
   - Se envía email automático de verificación

2. **Verificación por email**
   - Link único en el correo con token de 24 horas
   - Al verificar: `activo = 3` (verificado)
   - Solo usuarios verificados pueden hacer login

3. **Reenvío de verificación**
   - Opción para reenviar correo si no llegó
   - Invalidación de tokens anteriores

4. **Validaciones robustas**
   - Formato de email correcto
   - Emails únicos en la base de datos
   - Tokens únicos con expiración

## 📁 Archivos Modificados/Creados

### Backend (FastAPI)
- ✅ `main.py` - Lógica principal con endpoints de verificación
- ✅ `init_db.py` - Tablas actualizadas
- ✅ `requirements.txt` - Dependencias AWS
- ✅ `.env.example` - Variables de configuración
- ✅ `test_email.py` - Script de prueba
- ✅ `AWS_SES_SETUP.md` - Guía de configuración

### Frontend (Flutter)
- ✅ `main.dart` - Manejo de cuentas no verificadas
- ✅ Diálogo de reenvío de verificación
- ✅ Validación de formato de email

### Base de Datos
- ✅ Tabla `usuarios` - Campo `activo` cambiado a TINYINT
- ✅ Tabla `verification_tokens` - Tokens de verificación

## 🚀 Pasos de Implementación

### 1. Configurar AWS SES
```bash
# Sigue la guía detallada
cat AWS_SES_SETUP.md
```

### 2. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 3. Configurar variables de entorno
```bash
# Copia y edita el archivo de configuración
cp .env.example .env
# Edita .env con tus credenciales AWS
```

### 4. Probar configuración de email
```bash
python test_email.py
```

### 5. Actualizar base de datos
```bash
# Opción A: Base de datos nueva
python init_db.py

# Opción B: Base de datos existente - ejecutar en MySQL:
ALTER TABLE usuarios MODIFY COLUMN activo TINYINT DEFAULT 1 COMMENT '1=registrado, 3=verificado';

CREATE TABLE verification_tokens (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario_id INT NOT NULL,
    token VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP DEFAULT (CURRENT_TIMESTAMP + INTERVAL 24 HOUR),
    used BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE,
    INDEX idx_token (token),
    INDEX idx_expires (expires_at)
);
```

### 6. Actualizar app Flutter
```bash
# Compilar la nueva versión de la app
flutter build apk
# Instalar en dispositivo
flutter install
```

### 7. Ejecutar servidor
```bash
python main.py
```

## 🔄 Flujo de Usuario

1. **Registro**:
   - Usuario completa formulario (incluye email)
   - Servidor crea usuario con `activo = 1`
   - Se envía email de verificación automáticamente
   - Mensaje: "Usuario creado. Revisa tu correo electrónico"

2. **Verificación**:
   - Usuario recibe email con link único
   - Al hacer click, se abre página web de confirmación
   - Servidor cambia `activo = 3`
   - Usuario puede iniciar sesión

3. **Login**:
   - Si `activo = 1`: Error "Cuenta no verificada" + opción de reenvío
   - Si `activo = 3`: Login exitoso
   - Otros valores: Cuenta inactiva

## 🎛️ Nuevos Endpoints

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | `/usuarios/crear` | Registro + envío de email |
| GET | `/verificar-email?token=xxx` | Verificar desde email |
| POST | `/verificar-email` | API de verificación |
| POST | `/reenviar-verificacion` | Reenviar email |

## 🔧 Estados de Usuario

| Valor | Estado | Descripción |
|-------|--------|-------------|
| 1 | No verificado | Registrado, esperando verificación |
| 3 | Verificado | Puede usar la aplicación |
| 0 | Inactivo | Bloqueado por admin |

## 💰 Costos AWS (Free Tier)

- **200 emails gratuitos por día**
- **50,000 emails gratis por mes** (desde EC2)
- Después: $0.10 por cada 1,000 emails
- **Muy económico** para aplicaciones pequeñas

## 🛠️ Troubleshooting

### "Email address not verified"
- Verifica el email remitente en AWS SES Console

### Emails no llegan
- Revisa carpeta de spam
- En Sandbox: verifica también emails receptores
- Configura SPF/DKIM para tu dominio

### "AccessDenied"
- Verifica credenciales AWS en `.env`
- Usuario IAM necesita permiso `AmazonSESFullAccess`

### App no maneja verificación
- Recompila la app Flutter
- Verifica que el servidor esté corriendo
- Revisa logs del servidor

## 📱 Experiencia de Usuario

### ✅ Mejorado
- Registro seguro con verificación
- Emails profesionales con HTML
- Manejo claro de estados de cuenta
- Opción de reenvío automático

### 🔐 Seguridad
- Tokens únicos con expiración
- Validación dual (cliente/servidor)
- Emails únicos en BD
- Estados claros de verificación

## 🎉 ¡Listo!

Con esta implementación tienes un sistema profesional de verificación por email que:
- ✅ Asegura que los emails son reales
- ✅ Previene cuentas falsas
- ✅ Usa AWS Free Tier (económico)
- ✅ Interfaz clara en la app
- ✅ Manejo robusto de errores