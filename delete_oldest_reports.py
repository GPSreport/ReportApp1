#!/usr/bin/env python3
"""
delete_oldest_reports.py

Script seguro para eliminar los 2 registros con menor `id` de la tabla `reportes`.
También intenta eliminar los archivos de imagen asociados en la carpeta `imagenes_reportes`.

Uso:
  python3 delete_oldest_reports.py        # pide confirmación interactiva
  python3 delete_oldest_reports.py -y     # no pide confirmación
"""
import os
import argparse
from dotenv import load_dotenv
import mysql.connector
from mysql.connector import Error


def load_db_config_from_env():
    load_dotenv()
    return {
        'host': os.getenv('DB_HOST'),
        'port': int(os.getenv('DB_PORT', 3306)),
        'database': os.getenv('DB_NAME'),
        'user': os.getenv('DB_USER'),
        'password': os.getenv('DB_PASSWORD')
    }


def get_db_connection(db_config):
    try:
        conn = mysql.connector.connect(**db_config)
        return conn
    except Error as e:
        print(f"Error conectando a MySQL: {e}")
        return None


def find_oldest_reports(conn, limit=2):
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, foto_base64 FROM reportes ORDER BY id ASC LIMIT %s", (limit,))
    rows = cursor.fetchall()
    cursor.close()
    return rows


def delete_reports_by_ids(conn, ids):
    cursor = conn.cursor()
    # Construir placeholders según cantidad
    placeholders = ','.join(['%s'] * len(ids))
    query = f"DELETE FROM reportes WHERE id IN ({placeholders})"
    cursor.execute(query, tuple(ids))
    conn.commit()
    cursor.close()


def try_remove_image_file(image_ref):
    if not image_ref:
        return False
    # Normalizar rutas relativas que usamos en la app: "imagenes_reportes/<file>"
    # Aceptar con o sin slash inicial
    img = image_ref.lstrip('/')
    base_dir = os.path.dirname(os.path.abspath(__file__))
    img_path = os.path.join(base_dir, img)
    if os.path.exists(img_path):
        try:
            os.remove(img_path)
            return True
        except Exception as e:
            print(f"No se pudo eliminar archivo de imagen '{img_path}': {e}")
            return False
    return False


def main():
    parser = argparse.ArgumentParser(description='Eliminar los 2 registros más antiguos de la tabla reportes (y sus imágenes).')
    parser.add_argument('-y', '--yes', action='store_true', help='No pedir confirmación')
    parser.add_argument('-n', '--number', type=int, default=2, help='Cantidad de registros a eliminar (por defecto 2)')
    args = parser.parse_args()

    db_config = load_db_config_from_env()
    conn = get_db_connection(db_config)
    if conn is None:
        print('No se pudo conectar a la base de datos. Revisa las variables en el .env y la conectividad.')
        return

    rows = find_oldest_reports(conn, limit=args.number)
    if not rows:
        print('No hay registros para eliminar.')
        conn.close()
        return

    print('Registros candidatos a eliminación:')
    for r in rows:
        print(f" - id={r['id']}, foto_base64={r.get('foto_base64')}")

    if not args.yes:
        confirm = input(f"¿Eliminar estos {len(rows)} registros? Escribe 'si' para confirmar: ").strip().lower()
        if confirm != 'si':
            print('Operación cancelada por el usuario.')
            conn.close()
            return

    # Eliminar archivos de imagen asociados si existen
    removed_files = 0
    for r in rows:
        foto = r.get('foto_base64')
        if try_remove_image_file(foto):
            removed_files += 1

    ids = [r['id'] for r in rows]
    delete_reports_by_ids(conn, ids)
    conn.close()

    print(f"Eliminados {len(ids)} registros. Archivos de imagen eliminados: {removed_files} (si existían).")


if __name__ == '__main__':
    main()
