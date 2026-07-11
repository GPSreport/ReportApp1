from main import init_database


if __name__ == "__main__":
    print("Iniciando creacion de esquema MySQL local...")
    ok = init_database()
    if ok:
        print("Base de datos inicializada correctamente.")
        raise SystemExit(0)
    print("No se pudo inicializar la base de datos.")
    raise SystemExit(1)
