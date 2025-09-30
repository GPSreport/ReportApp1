# Guía de Configuración AWS SES para Verificación de Email

## ¿Qué es AWS SES?
Amazon Simple Email Service (SES) es un servicio de email escalable y económico de AWS.

## Free Tier de AWS SES
- **50,000 emails gratuitos por mes** si envías desde EC2
- **200 emails gratuitos por día** si envías desde otros servicios
- Ideal para aplicaciones pequeñas y medianas

## Pasos de Configuración

### 1. Crear cuenta de AWS
1. Ve a [aws.amazon.com](https://aws.amazon.com)
2. Crea una cuenta gratuita
3. Verifica tu tarjeta de crédito (no se cobrará en free tier)

### 2. Configurar AWS SES
1. **Ir al servicio SES:**
   - En la consola de AWS, busca "SES"
   - Selecciona "Simple Email Service"

2. **Verificar email remitente:**
   - Ve a "Verified identities"
   - Click "Create identity"
   - Selecciona "Email address"
   - Ingresa tu email (ej: `noreply@tudominio.com`)
   - Revisa tu email y haz click en el enlace de verificación

3. **Crear credenciales IAM:**
   - Ve a "IAM" en la consola AWS
   - "Users" → "Create user"
   - Nombre: `ses-email-sender`
   - Selecciona "Programmatic access"
   - Attach policy: `AmazomSESFullAccess`
   - Guarda Access Key ID y Secret Access Key

### 3. Configurar variables de entorno
Copia `.env.example` a `.env` y completa:

```env
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=AKIA...
AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI...
AWS_SES_SENDER_EMAIL=noreply@tudominio.com
```

### 4. Limitaciones del Sandbox
**AWS SES inicia en modo "Sandbox":**
- Solo puedes enviar emails a direcciones verificadas
- Máximo 200 emails por día
- Máximo 1 email por segundo

**Para salir del Sandbox:**
1. Ve a "Account dashboard" en SES
2. Click "Request production access"
3. Completa el formulario explicando tu uso
4. AWS revisará en 24-48 horas

### 5. Verificar emails de destino (solo en Sandbox)
En modo Sandbox, debes verificar cada email receptor:
1. "Verified identities" → "Create identity"
2. Selecciona "Email address"
3. Ingresa el email del usuario que se registrará
4. El usuario debe verificar su email en AWS SES

## Instalación de Dependencias

```bash
pip install boto3 botocore
```

## Prueba de Configuración

```python
import boto3

try:
    ses = boto3.client('ses', 
        region_name='us-east-1',
        aws_access_key_id='tu_access_key',
        aws_secret_access_key='tu_secret_key'
    )
    
    response = ses.get_send_quota()
    print(f"Emails restantes hoy: {response['MaxSendRate']}")
    print(f"Emails enviados en 24h: {response['SentLast24Hours']}")
    print("✅ Configuración correcta")
    
except Exception as e:
    print(f"❌ Error: {e}")
```

## Estados de Verificación en la App

- **activo = 1**: Usuario registrado, no verificado
- **activo = 3**: Usuario verificado, puede usar la app
- **activo = 0**: Usuario inactivo/bloqueado

## Endpoints Nuevos

- `POST /usuarios/crear` - Crea usuario y envía email de verificación
- `GET /verificar-email?token=xxx` - Verifica cuenta desde email
- `POST /verificar-email` - API para verificar cuenta
- `POST /reenviar-verificacion` - Reenvía email de verificación

## Troubleshooting

### Error: "Email address not verified"
- Verifica el email remitente en AWS SES console

### Error: "MessageRejected" 
- En Sandbox: verifica también el email receptor
- Fuera de Sandbox: revisa que el email sea válido

### Error: "AccessDenied"
- Verifica las credenciales AWS
- Asegúrate que el usuario IAM tenga permisos SES

### Emails no llegan
- Revisa spam/junk
- Verifica que el dominio tenga SPF/DKIM configurado
- En Gmail, revisa la pestaña "Promociones"

## Costos
- **Free Tier**: 200 emails/día gratis
- **Después**: $0.10 por cada 1,000 emails
- **Muy económico** para aplicaciones pequeñas