"""
Utilidad mínima para inspeccionar y editar reportes en reportes.db

Uso:
  python edit_reportes.py list
  python edit_reportes.py show <id>
  python edit_reportes.py update <id> [--lat 10.0] [--lng -74.0] [--tipo alerta] [--desc "texto"]
  python edit_reportes.py set-photo <id> <imagen.jpg>
  python edit_reportes.py backup

Asegúrate primero de hacer una copia manual: cp reportes.db reportes.db.bak
"""
import sqlite3, sys, base64, shutil, argparse, os

DB_PATH = os.path.join(os.path.dirname(__file__), 'reportes.db')

def connect():
    if not os.path.exists(DB_PATH):
        print(f"No se encuentra {DB_PATH}")
        sys.exit(1)
    return sqlite3.connect(DB_PATH)

def cmd_list(args):
    db = connect()
    cur = db.cursor()
    cur.execute("SELECT id, timestamp, latitud, longitud, tipo_reporte FROM reportes ORDER BY id DESC LIMIT 200")
    rows = cur.fetchall()
    for r in rows:
        print(f"id={r[0]} | {r[1]} | lat={r[2]} lng={r[3]} | tipo={r[4]}")
    db.close()

def cmd_show(args):
    db = connect()
    cur = db.cursor()
    cur.execute("SELECT * FROM reportes WHERE id=?", (args.id,))
    row = cur.fetchone()
    if not row:
        print("No encontrado")
    else:
        # Mostrar columnas por índice dinámico (más seguro si esquema cambia)
        cur2 = db.cursor()
        cur2.execute("PRAGMA table_info(reportes)")
        cols = [c[1] for c in cur2.fetchall()]
        for i, col in enumerate(cols):
            val = row[i]
            if col == 'foto_base64' and val is not None:
                print(f"{col}: <base64 len={len(val)}> (use set-photo to replace)")
            else:
                print(f"{col}: {val}")
    db.close()

def cmd_update(args):
    db = connect()
    cur = db.cursor()
    updates = {}
    if args.lat is not None: updates['latitud'] = args.lat
    if args.lng is not None: updates['longitud'] = args.lng
    if args.tipo is not None: updates['tipo_reporte'] = args.tipo
    if args.desc is not None: updates['descripcion'] = args.desc
    if not updates:
        print("Nada para actualizar.")
        return
    set_clause = ", ".join([f"{k}=?" for k in updates.keys()])
    params = list(updates.values()) + [args.id]
    sql = f"UPDATE reportes SET {set_clause} WHERE id=?"
    cur.execute(sql, params)
    db.commit()
    print(f"Actualizado id={args.id}")
    db.close()

def cmd_set_photo(args):
    if not os.path.exists(args.image):
        print("Imagen no encontrada.")
        return
    with open(args.image, "rb") as f:
        b = f.read()
    b64 = base64.b64encode(b).decode('utf-8')
    db = connect()
    cur = db.cursor()
    cur.execute("UPDATE reportes SET foto_base64=? WHERE id=?", (b64, args.id))
    db.commit()
    print(f"Foto actualizada para id={args.id} (base64 len={len(b64)})")
    db.close()

def cmd_backup(args):
    bak = DB_PATH + '.bak'
    shutil.copy2(DB_PATH, bak)
    print(f"Copiado {DB_PATH} -> {bak}")

def main():
    p = argparse.ArgumentParser(description="Editar reportes.db")
    sub = p.add_subparsers(dest='cmd')
    sub.add_parser('list')
    ps = sub.add_parser('show'); ps.add_argument('id', type=int)
    pu = sub.add_parser('update'); pu.add_argument('id', type=int); pu.add_argument('--lat', type=float); pu.add_argument('--lng', type=float); pu.add_argument('--tipo'); pu.add_argument('--desc')
    pp = sub.add_parser('set-photo'); pp.add_argument('id', type=int); pp.add_argument('image')
    sub.add_parser('backup')
    args = p.parse_args()
    if args.cmd == 'list': cmd_list(args)
    elif args.cmd == 'show': cmd_show(args)
    elif args.cmd == 'update': cmd_update(args)
    elif args.cmd == 'set-photo': cmd_set_photo(args)
    elif args.cmd == 'backup': cmd_backup(args)
    else:
        p.print_help()

if __name__ == "__main__":
    main()
