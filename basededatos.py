import sqlite3
import os
import uuid

def generar_uuid():
    """Genera un ID único corto para las empresas."""
    return str(uuid.uuid4())[:8].upper()

def preparar_sistema_completo():
    ruta_carpeta = os.path.dirname(os.path.abspath(__file__))
    nombre_db = "gestion_proyectos.db"
    ruta_db = os.path.join(ruta_carpeta, nombre_db)

    print("--- Iniciando Mantenimiento de Base de Datos ---")

    if os.path.exists(ruta_db):
        try:
            os.remove(ruta_db)
            print("✔ Base de datos antigua/corrupta eliminada.")
        except PermissionError:
            print("❌ ERROR CRÍTICO: El archivo está abierto en otro programa.")
            return

    try:
        conexion = sqlite3.connect(ruta_db)
        cursor = conexion.cursor()
        cursor.execute("PRAGMA foreign_keys = ON")

        # TABLA USUARIOS
        cursor.execute('''CREATE TABLE usuarios (
            id_usuario INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre_completo TEXT NOT NULL,
            usuario_login TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            rol TEXT NOT NULL)''')

        # TABLA CLIENTES
        cursor.execute('''CREATE TABLE clientes (
            id_cliente INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre_empresa TEXT UNIQUE NOT NULL,
            telefono_referido TEXT,
            correo TEXT,
            direccion_empresa TEXT,
            uuid_empresa TEXT UNIQUE NOT NULL)''')

        # TABLA PUBLICIDAD (Ajustada para guardar rutas largas)
        cursor.execute('''CREATE TABLE publicidad (
            id_pub INTEGER PRIMARY KEY AUTOINCREMENT, 
            uuid_empresa TEXT, 
            nombre_archivo TEXT, -- Aquí guardaremos la ruta completa del archivo
            estado TEXT DEFAULT 'Pendiente', 
            fecha TEXT,
            FOREIGN KEY (uuid_empresa) REFERENCES clientes (uuid_empresa) ON DELETE CASCADE)''')

        # TABLA PROYECTOS
        cursor.execute('''CREATE TABLE proyectos (
            id_proyecto INTEGER PRIMARY KEY AUTOINCREMENT,
            id_cliente INTEGER,
            nombre TEXT NOT NULL,
            fecha_inicio TEXT,
            fecha_fin TEXT,
            estado TEXT,
            FOREIGN KEY (id_cliente) REFERENCES clientes (id_cliente))''')

        # TABLA MENSAJES
        cursor.execute('''CREATE TABLE mensajes (
            id_mensaje INTEGER PRIMARY KEY AUTOINCREMENT,
            remitente TEXT NOT NULL,
            contenido TEXT NOT NULL,
            fecha_hora TEXT NOT NULL)''')

        # --- DATOS INICIALES ---
        usuarios = [
            ('Alejandro Coxaj', 'alejandro', 'prog123', 'Programador'),
            ('Francisco Contreras', 'francisco', 'foto345', 'Fotógrafo')
        ]
        cursor.executemany(
            'INSERT INTO usuarios (nombre_completo, usuario_login, password, rol) VALUES (?, ?, ?, ?)',
            usuarios)

        # Cliente de prueba
        id_prueba = generar_uuid()
        cursor.execute('''INSERT INTO clientes 
            (nombre_empresa, telefono_referido, correo, direccion_empresa, uuid_empresa) 
            VALUES (?, ?, ?, ?, ?)''',
                       ('Inversiones Global', '5555-1234', 'contacto@global.com', 'Ciudad de Guatemala', id_prueba))

        conexion.commit()
        conexion.close()

        print(f"\n✅ BASE DE DATOS LISTA")
        print(f"ID de prueba generado: {id_prueba}")

    except sqlite3.Error as e:
        print(f"❌ Error de SQLite: {e}")

if __name__ == "__main__":
    preparar_sistema_completo()