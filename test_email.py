#!/usr/bin/env python3
"""
Script de prueba para verificar la configuración de AWS SES
Ejecutar: python test_email.py
"""

import os
import sys
from dotenv import load_dotenv
import boto3
from botocore.exceptions import ClientError

# Cargar variables de entorno
load_dotenv()

def test_aws_ses():
    """Prueba la configuración de AWS SES"""
    print("🧪 Probando configuración AWS SES...")
    
    # Obtener configuración
    aws_region = os.getenv('AWS_REGION', 'us-east-1')
    aws_access_key = os.getenv('AWS_ACCESS_KEY_ID')
    aws_secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
    sender_email = os.getenv('AWS_SES_SENDER_EMAIL')
    
    # Verificar variables
    if not aws_access_key:
        print("❌ AWS_ACCESS_KEY_ID no configurado")
        return False
    
    if not aws_secret_key:
        print("❌ AWS_SECRET_ACCESS_KEY no configurado")
        return False
        
    if not sender_email:
        print("❌ AWS_SES_SENDER_EMAIL no configurado")
        return False
    
    print(f"📍 Región: {aws_region}")
    print(f"📧 Email remitente: {sender_email}")
    print(f"🔑 Access Key: {aws_access_key[:10]}...")
    
    try:
        # Crear cliente SES
        ses_client = boto3.client(
            'ses',
            region_name=aws_region,
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key
        )
        
        # Obtener información de cuenta
        print("\n📊 Información de cuenta SES:")
        
        # Cuota de envío
        quota = ses_client.get_send_quota()
        print(f"  • Máximo por día: {quota['Max24HourSend']}")
        print(f"  • Enviados en 24h: {quota['SentLast24Hours']}")
        print(f"  • Velocidad máxima: {quota['MaxSendRate']}/segundo")
        
        # Estadísticas de envío
        stats = ses_client.get_send_statistics()
        if stats['SendDataPoints']:
            latest = stats['SendDataPoints'][-1]
            print(f"  • Último período - Entregas: {latest['DeliveryAttempts']}")
            print(f"  • Último período - Rebotes: {latest['Bounces']}")
            print(f"  • Último período - Quejas: {latest['Complaints']}")
        
        # Identidades verificadas
        identities = ses_client.list_verified_email_addresses()
        print(f"\n✅ Emails verificados ({len(identities['VerifiedEmailAddresses'])}):")
        for email in identities['VerifiedEmailAddresses']:
            print(f"  • {email}")
        
        # Verificar si el email remitente está verificado
        if sender_email not in identities['VerifiedEmailAddresses']:
            print(f"\n⚠️  ADVERTENCIA: {sender_email} NO está verificado en AWS SES")
            print("   Necesitas verificar este email en la consola de AWS SES")
            return False
        
        print(f"\n✅ ¡Configuración correcta! El sistema puede enviar emails desde {sender_email}")
        
        # Preguntar si enviar email de prueba
        test_email = input(f"\n¿Enviar email de prueba a {sender_email}? (s/n): ").lower()
        if test_email == 's':
            send_test_email(ses_client, sender_email)
        
        return True
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        error_message = e.response['Error']['Message']
        
        print(f"\n❌ Error de AWS SES: {error_code}")
        print(f"   Mensaje: {error_message}")
        
        if error_code == "InvalidClientTokenId":
            print("💡 Solución: Verifica tu AWS_ACCESS_KEY_ID")
        elif error_code == "SignatureDoesNotMatch":
            print("💡 Solución: Verifica tu AWS_SECRET_ACCESS_KEY")
        elif error_code == "UnauthorizedOperation":
            print("💡 Solución: Verifica los permisos IAM para SES")
        
        return False
        
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False

def send_test_email(ses_client, sender_email):
    """Envía un email de prueba"""
    try:
        print(f"📧 Enviando email de prueba a {sender_email}...")
        
        response = ses_client.send_email(
            Source=sender_email,
            Destination={'ToAddresses': [sender_email]},
            Message={
                'Subject': {
                    'Data': '🧪 Prueba de configuración AWS SES - GPS Reporter',
                    'Charset': 'UTF-8'
                },
                'Body': {
                    'Html': {
                        'Data': """
                        <html>
                        <body style="font-family: Arial, sans-serif;">
                            <h2 style="color: #16a34a;">✅ ¡Configuración exitosa!</h2>
                            <p>Este es un email de prueba del sistema GPS Reporter.</p>
                            <p>Tu configuración de AWS SES está funcionando correctamente.</p>
                            <hr>
                            <p style="font-size: 12px; color: #666;">
                                GPS Reporter - Sistema de verificación por email
                            </p>
                        </body>
                        </html>
                        """,
                        'Charset': 'UTF-8'
                    },
                    'Text': {
                        'Data': """
¡Configuración exitosa!

Este es un email de prueba del sistema GPS Reporter.
Tu configuración de AWS SES está funcionando correctamente.

GPS Reporter - Sistema de verificación por email
                        """,
                        'Charset': 'UTF-8'
                    }
                }
            }
        )
        
        message_id = response['MessageId']
        print(f"✅ Email enviado exitosamente!")
        print(f"   Message ID: {message_id}")
        print(f"   Revisa tu bandeja de entrada en {sender_email}")
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        error_message = e.response['Error']['Message']
        print(f"❌ Error enviando email: {error_code} - {error_message}")

def main():
    """Función principal"""
    print("🚀 GPS Reporter - Test de configuración AWS SES")
    print("=" * 50)
    
    # Verificar archivo .env
    if not os.path.exists('.env'):
        print("❌ Archivo .env no encontrado")
        print("💡 Copia .env.example a .env y configura las variables")
        return
    
    # Probar configuración
    success = test_aws_ses()
    
    if success:
        print("\n🎉 ¡Todo listo! El sistema de verificación por email está configurado.")
        print("   Ahora puedes ejecutar: python main.py")
    else:
        print("\n❌ Hay problemas con la configuración.")
        print("   Revisa la guía en AWS_SES_SETUP.md")

if __name__ == "__main__":
    main()