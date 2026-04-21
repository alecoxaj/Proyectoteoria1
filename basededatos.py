import sqlite3
import os

def crear_base_de_datos():
    ruta_carpeta = os.path.dirname(os.path.abspath(__file__))
    ruta_db = os.path.join(ruta_carpeta, "gestion_proyectos.db")

    conexion = sqlite3.connect(ruta_db)
    cursor = conexion.cursor()

    # 1. Tabla Usuarios (NUEVA)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id_usuario INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre_completo TEXT NOT NULL,
            usuario_login TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            rol TEXT NOT NULL
        )
    ''')

    # 2. Tabla Clientes
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS clientes (
            id_cliente INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            telefono TEXT,
            correo TEXT
        )
    ''')

    # 3. Tabla Proyectos
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS proyectos (
            id_proyecto INTEGER PRIMARY KEY AUTOINCREMENT,
            id_cliente INTEGER,
            nombre TEXT NOT NULL,
            fecha_inicio TEXT,
            fecha_fin TEXT,
            estado TEXT,
            FOREIGN KEY (id_cliente) REFERENCES clientes (id_cliente)
        )
    ''')

    # 4. Tabla Pagos
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pagos (
            id_pago INTEGER PRIMARY KEY AUTOINCREMENT,
            id_proyecto INTEGER,
            monto REAL,
            tipo_pago TEXT,
            fecha TEXT,
            FOREIGN KEY (id_proyecto) REFERENCES proyectos (id_proyecto)
        )
    ''')

    # INSERTAR LOS USUARIOS PREESTABLECIDOS (Solo si no existen)
    usuarios_iniciales = [
        ('Alejandro Coxaj', 'alejandro', 'prog123', 'Programador'),
        ('Francisco Contreras', 'francisco', 'foto345', 'Fotógrafo')
    ]

    cursor.executemany('''
        INSERT OR IGNORE INTO usuarios (nombre_completo, usuario_login, password, rol) 
        VALUES (?, ?, ?, ?)
    ''', usuarios_iniciales)

    conexion.commit()
    conexion.close()
    print(f"✅ Base de datos lista con usuarios preestablecidos en: {ruta_db}")

if __name__ == "__main__":
    crear_base_de_datos()