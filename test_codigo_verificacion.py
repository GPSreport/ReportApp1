#!/usr/bin/env python3
"""
Script de prueba para los nuevos endpoints de verificación con código de 6 dígitos
"""

import requests
import json
import time

# Configuración
BASE_URL = "http://localhost:5000"
TEST_EMAIL = "gpsreportbaq@gmail.com"  # Email verificado en AWS SES

def test_enviar_codigo():
    """Probar endpoint de envío de código"""
    print("🔸 Probando envío de código de verificación...")
    
    url = f"{BASE_URL}/enviar-codigo"
    data = {"email": TEST_EMAIL}
    
    try:
        response = requests.post(url, json=data)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            print("✅ Código enviado correctamente")
            return True
        else:
            print(f"❌ Error enviando código: {response.json()}")
            return False
            
    except Exception as e:
        print(f"❌ Error en la petición: {e}")
        return False

def test_estado_usuario():
    """Probar endpoint de estado del usuario"""
    print("\n🔸 Probando consulta de estado de usuario...")
    
    url = f"{BASE_URL}/usuario-estado/{TEST_EMAIL}"
    
    try:
        response = requests.get(url)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Usuario: {data['nombre']}")
            print(f"✅ Verificado: {data['verificado']}")
            print(f"✅ Estado: {data['estado_texto']}")
            return True
        else:
            print(f"❌ Error consultando estado: {response.json()}")
            return False
            
    except Exception as e:
        print(f"❌ Error en la petición: {e}")
        return False

def test_verificar_codigo():
    """Probar endpoint de verificación de código"""
    print("\n🔸 Probando verificación de código...")
    
    # Solicitar código al usuario
    codigo = input("Ingresa el código de 6 dígitos recibido por email: ").strip()
    
    if len(codigo) != 6 or not codigo.isdigit():
        print("❌ Código inválido. Debe ser de 6 dígitos.")
        return False
    
    url = f"{BASE_URL}/verificar-codigo"
    data = {"codigo": codigo}
    
    try:
        response = requests.post(url, json=data)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            print("✅ Código verificado correctamente")
            return True
        else:
            print(f"❌ Error verificando código: {response.json()}")
            return False
            
    except Exception as e:
        print(f"❌ Error en la petición: {e}")
        return False

def main():
    """Función principal de pruebas"""
    print("🧪 Iniciando pruebas de verificación por código de 6 dígitos")
    print(f"📧 Email de prueba: {TEST_EMAIL}")
    print("-" * 60)
    
    # Probar estado inicial
    test_estado_usuario()
    
    # Enviar código
    if test_enviar_codigo():
        print("\n⏳ Revisa tu email y regresa para verificar el código...")
        
        # Preguntar si quiere verificar
        verificar = input("\n¿Quieres verificar el código ahora? (s/n): ").lower().strip()
        
        if verificar == 's':
            if test_verificar_codigo():
                # Probar estado después de verificación
                print("\n🔸 Consultando estado después de verificación...")
                test_estado_usuario()
    
    print("\n🏁 Pruebas completadas")

if __name__ == "__main__":
    main()