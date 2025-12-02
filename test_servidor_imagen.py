"""
Script de prueba para el servidor de procesamiento de imágenes
Ejecutar desde tu máquina local para verificar que el servidor responde correctamente
"""

import requests
import base64
import json
from datetime import datetime

# Configuración
SERVIDOR_IMAGEN_URL = "http://18.116.117.140:8000"
IMAGEN_TEST = "test_image.jpg"  # Cambiar por tu imagen de prueba

def test_health():
    """Verificar que el servidor está activo"""
    print("🏥 Verificando estado del servidor...")
    try:
        response = requests.get(f"{SERVIDOR_IMAGEN_URL}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Servidor activo")
            print(f"   - Modelo YOLO: {'✅ Cargado' if data['modelo_yolo'] else '❌ No cargado'}")
            print(f"   - Nombre modelo: {data['modelo_nombre']}")
            print(f"   - Imágenes procesadas: {data['imagenes_procesadas']}")
            return True
        else:
            print(f"❌ Servidor respondió con código: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Error conectando al servidor: {e}")
        print("💡 Verifica:")
        print("   1. El servidor está arrancado")
        print("   2. Puerto 8000 está abierto en el Security Group")
        print("   3. La IP es correcta: 18.116.117.140")
        return False

def test_stats():
    """Obtener estadísticas del servidor"""
    print("\n📊 Obteniendo estadísticas...")
    try:
        response = requests.get(f"{SERVIDOR_IMAGEN_URL}/stats", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Estadísticas:")
            print(f"   - Imágenes procesadas: {data['imagenes_procesadas']}")
            print(f"   - Aforo promedio: {data['aforo_promedio']:.1f}")
            print(f"   - Modelo: {data['modelo_nombre']}")
            return True
        else:
            print(f"❌ Error obteniendo estadísticas: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Error: {e}")
        return False

def test_procesar_imagen(imagen_path: str):
    """Enviar imagen para procesar"""
    print(f"\n🖼️ Procesando imagen: {imagen_path}")
    
    try:
        # Leer imagen y convertir a base64
        with open(imagen_path, "rb") as f:
            img_data = f.read()
            img_b64 = base64.b64encode(img_data).decode('utf-8')
        
        print(f"   Tamaño imagen: {len(img_data) / 1024:.1f} KB")
        print(f"   Tamaño base64: {len(img_b64) / 1024:.1f} KB")
        
        # Preparar payload
        payload = {
            "foto_base64": img_b64,
            "timestamp": datetime.now().isoformat(),
            "latitud": -12.0464,  # Lima, Perú (ejemplo)
            "longitud": -77.0428,
            "descripcion": "Prueba desde script de test",
            "tipo_reporte": "aforo_test"
        }
        
        print("   Enviando al servidor...")
        response = requests.post(
            f"{SERVIDOR_IMAGEN_URL}/procesar-imagen",
            json=payload,
            timeout=30  # Procesamiento puede tardar
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n✅ Procesamiento exitoso:")
            print(f"   - Aforo detectado: {data['aforo']} persona(s)")
            print(f"   - Tiempo de procesamiento: {data['processing_time_ms']:.1f} ms")
            print(f"   - Enviado a API principal: {'✅ Sí' if data['forwarded_to_api'] else '❌ No'}")
            print(f"   - Mensaje: {data['message']}")
            return True
        else:
            print(f"❌ Error procesando imagen: {response.status_code}")
            print(f"   Respuesta: {response.text}")
            return False
            
    except FileNotFoundError:
        print(f"❌ Archivo no encontrado: {imagen_path}")
        print("💡 Crea una imagen de prueba o cambia la ruta en IMAGEN_TEST")
        return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Error de conexión: {e}")
        return False
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False

def test_deteccion_simple(imagen_path: str):
    """Test de detección sin enviar a API principal"""
    print(f"\n🔍 Test de detección (sin enviar a API principal)...")
    
    try:
        with open(imagen_path, "rb") as f:
            img_b64 = base64.b64encode(f.read()).decode('utf-8')
        
        payload = {
            "foto_base64": img_b64,
            "timestamp": datetime.now().isoformat()
        }
        
        response = requests.post(
            f"{SERVIDOR_IMAGEN_URL}/test-deteccion",
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Detección completada:")
            print(f"   - Aforo: {data['aforo']}")
            print(f"   - Confianza promedio: {data['confianza_promedio']:.2f}")
            print(f"   - Detecciones:")
            
            for det in data['detecciones']:
                print(f"      • Persona #{det['id']}: Confianza {det['confianza']:.2f}")
            
            # Guardar imagen procesada si está disponible
            if data.get('imagen_procesada_base64'):
                output_path = "imagen_procesada_test.jpg"
                img_data = base64.b64decode(data['imagen_procesada_base64'])
                with open(output_path, "wb") as f:
                    f.write(img_data)
                print(f"\n💾 Imagen procesada guardada en: {output_path}")
            
            return True
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
            return False
            
    except FileNotFoundError:
        print(f"❌ Archivo no encontrado: {imagen_path}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Ejecutar todas las pruebas"""
    print("=" * 70)
    print("PRUEBAS DEL SERVIDOR DE PROCESAMIENTO DE IMÁGENES")
    print("=" * 70)
    print(f"URL: {SERVIDOR_IMAGEN_URL}")
    print("=" * 70)
    
    # Test 1: Health check
    if not test_health():
        print("\n❌ El servidor no está disponible. Abortando pruebas.")
        return
    
    # Test 2: Estadísticas
    test_stats()
    
    # Test 3: Procesar imagen (si existe archivo de prueba)
    try:
        # Intentar con archivo de prueba
        test_deteccion_simple(IMAGEN_TEST)
        
        # Si quieres probar el flujo completo (enviando a API principal):
        # test_procesar_imagen(IMAGEN_TEST)
        
    except Exception as e:
        print(f"\n⚠️ No se pudo realizar test con imagen: {e}")
        print(f"💡 Crea un archivo '{IMAGEN_TEST}' con una imagen que contenga personas")
    
    print("\n" + "=" * 70)
    print("✅ Pruebas completadas")
    print("=" * 70)

if __name__ == "__main__":
    main()
