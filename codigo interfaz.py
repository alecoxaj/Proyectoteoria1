import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
import os
import uuid
import shutil
import zipfile
from datetime import datetime
from tkcalendar import DateEntry
from PIL import Image, ImageTk, ImageOps


class SistemaGestion:
    def __init__(self, root):
        self.root = root
        self.root.title("Espacio Creativo v3.0 - Gestion Pro")
        self.root.geometry("1200x850")

        self.modo_oscuro = False
        self.color_fondo = "#f9c784"
        self.color_header = "#f39c12"
        self.color_card = "white"
        self.color_texto = "#2c3e50"

        ruta_carpeta = os.path.dirname(os.path.abspath(__file__))
        self.ruta_db = os.path.join(ruta_carpeta, "gestion_proyectos.db")
        self.ruta_logo = os.path.join(ruta_carpeta, "NARANJA - VERTICAL-Photoroom.png")

        self.usuario_actual = ""
        self.rol_actual = ""
        self.img_original = None
        self.img_tk = None
        self.path_actual = ""
        self.menu_usuario_popup = None
        self.submenu_tema = None

        self.inicializar_db_formal()
        self.configurar_estilos()
        self.pantalla_login()

    def inicializar_db_formal(self):
        conn = sqlite3.connect(self.ruta_db)
        c = conn.cursor()

        c.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id_usuario INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre_completo TEXT,
            usuario_login TEXT UNIQUE,
            password TEXT,
            rol TEXT
        )
        """)

        c.execute("""
        CREATE TABLE IF NOT EXISTS mensajes (
            id_mensaje INTEGER PRIMARY KEY AUTOINCREMENT,
            remitente TEXT,
            contenido TEXT,
            fecha_hora TEXT
        )
        """)

        c.execute("""
        CREATE TABLE IF NOT EXISTS clientes (
            id_cliente INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre_empresa TEXT UNIQUE,
            telefono_referido TEXT,
            correo TEXT,
            direccion_empresa TEXT,
            uuid_empresa TEXT UNIQUE
        )
        """)

        c.execute("""
        CREATE TABLE IF NOT EXISTS proyectos (
            id_proyecto INTEGER PRIMARY KEY AUTOINCREMENT,
            id_cliente INTEGER,
            nombre TEXT,
            fecha_inicio TEXT,
            estado TEXT
        )
        """)

        c.execute("""
        CREATE TABLE IF NOT EXISTS publicidad (
            id_pub INTEGER PRIMARY KEY AUTOINCREMENT,
            uuid_empresa TEXT,
            nombre_archivo TEXT,
            estado TEXT,
            fecha TEXT,
            proyecto TEXT
        )
        """)

        c.execute("""
        CREATE TABLE IF NOT EXISTS pagos (
            id_pago INTEGER PRIMARY KEY AUTOINCREMENT,
            uuid_empresa TEXT,
            nombre_proyecto TEXT,
            monto REAL,
            metodo_pago TEXT,
            fecha_pago TEXT
        )
        """)

        c.execute("""
        CREATE TABLE IF NOT EXISTS egresos (
            id_egreso INTEGER PRIMARY KEY AUTOINCREMENT,
            concepto TEXT NOT NULL,
            categoria TEXT,
            monto REAL NOT NULL,
            fecha TEXT NOT NULL,
            nota TEXT
        )
        """)

        c.execute("""
        INSERT OR IGNORE INTO usuarios
        (nombre_completo, usuario_login, password, rol)
        VALUES (?, ?, ?, ?)
        """, ("Alejandro Coxaj", "alejandro", "prog123", "Programador"))

        c.execute("""
        INSERT OR IGNORE INTO usuarios
        (nombre_completo, usuario_login, password, rol)
        VALUES (?, ?, ?, ?)
        """, ("Francisco Contreras", "francisco", "prog123", "Programador"))

        conn.commit()
        conn.close()

        try:
            self.crear_respaldo_automatico()
        except Exception:
            pass

    def configurar_estilos(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", rowheight=28, font=("Segoe UI", 10))

    def obtener_lista_db(self, consulta, params=()):
        try:
            conn = sqlite3.connect(self.ruta_db)
            c = conn.cursor()
            c.execute(consulta, params)
            datos = c.fetchall()
            conn.close()
            return datos
        except Exception:
            return []

    def ejecutar_db(self, consulta, params=()):
        conn = sqlite3.connect(self.ruta_db)
        c = conn.cursor()
        c.execute(consulta, params)
        conn.commit()
        ultimo_id = c.lastrowid
        conn.close()
        return ultimo_id

    def limpiar_pantalla(self):
        self.cerrar_menus_usuario()
        for widget in self.root.winfo_children():
            widget.destroy()

    def obtener_usuarios(self):
        datos = self.obtener_lista_db(
            "SELECT usuario_login FROM usuarios ORDER BY nombre_completo"
        )
        return [d[0] for d in datos]

    def aplicar_tema(self, modo_oscuro):
        self.modo_oscuro = modo_oscuro

        if self.modo_oscuro:
            self.color_fondo = "#1e1e1e"
            self.color_header = "#111111"
            self.color_card = "#2c2c2c"
            self.color_texto = "white"
        else:
            self.color_fondo = "#f9c784"
            self.color_header = "#f39c12"
            self.color_card = "white"
            self.color_texto = "#2c3e50"

        self.cerrar_menus_usuario()
        self.menu_principal()

    def cambiar_tema(self):
        self.aplicar_tema(not self.modo_oscuro)

    def mostrar_soporte(self):
        self.cerrar_menus_usuario()
        messagebox.showinfo(
            "Soporte Tecnico",
            "Contactanos al:\n\n"
            "Correo: soporte@espaciocreativo.com\n"
            "Tel: +502 4560-7604, +502 4135-7899, +502 3067-8267"
        )

    def cerrar_sesion(self):
        self.cerrar_menus_usuario()
        self.usuario_actual = ""
        self.rol_actual = ""
        self.pantalla_login()

    def cerrar_menus_usuario(self):
        for ventana in (self.submenu_tema, self.menu_usuario_popup):
            try:
                if ventana and ventana.winfo_exists():
                    ventana.destroy()
            except Exception:
                pass

        self.submenu_tema = None
        self.menu_usuario_popup = None

    def crear_item_menu(self, padre, icono, texto, comando=None, flecha=False):
        item = tk.Frame(padre, bg="white", height=48, cursor="hand2")
        item.pack(fill="x")
        item.pack_propagate(False)

        tk.Label(
            item,
            text=icono,
            bg="white",
            fg="#2c3e50",
            font=("Segoe UI", 15),
            width=3
        ).pack(side="left", padx=(8, 4))

        tk.Label(
            item,
            text=texto,
            bg="white",
            fg="#2c3e50",
            font=("Segoe UI", 10, "bold"),
            anchor="w"
        ).pack(side="left", fill="x", expand=True)

        if flecha:
            tk.Label(
                item,
                text=">",
                bg="white",
                fg="#7f8c8d",
                font=("Segoe UI", 16, "bold")
            ).pack(side="right", padx=12)

        def entrar(event=None):
            item.configure(bg="#f4f6f7")
            for hijo in item.winfo_children():
                hijo.configure(bg="#f4f6f7")

        def salir(event=None):
            item.configure(bg="white")
            for hijo in item.winfo_children():
                hijo.configure(bg="white")

        def click(event=None):
            if comando:
                comando()

        item.bind("<Enter>", entrar)
        item.bind("<Leave>", salir)
        item.bind("<Button-1>", click)

        for hijo in item.winfo_children():
            hijo.bind("<Enter>", entrar)
            hijo.bind("<Leave>", salir)
            hijo.bind("<Button-1>", click)

        return item

    def mostrar_submenu_tema(self, menu_x, menu_y):
        if self.submenu_tema and self.submenu_tema.winfo_exists():
            self.submenu_tema.destroy()

        ancho_submenu = 190
        alto_submenu = 108
        pantalla_ancho = self.root.winfo_screenwidth()
        pantalla_alto = self.root.winfo_screenheight()

        submenu_x = menu_x + 210
        submenu_y = menu_y + 5

        if submenu_x + ancho_submenu > pantalla_ancho - 10:
            submenu_x = menu_x - ancho_submenu

        if submenu_y + alto_submenu > pantalla_alto - 10:
            submenu_y = pantalla_alto - alto_submenu - 10

        self.submenu_tema = tk.Toplevel(self.root)
        self.submenu_tema.overrideredirect(True)
        self.submenu_tema.configure(bg="#dddddd")
        self.submenu_tema.geometry(
            f"{ancho_submenu}x{alto_submenu}+{submenu_x}+{submenu_y}"
        )

        contenedor = tk.Frame(
            self.submenu_tema,
            bg="white",
            highlightthickness=1,
            highlightbackground="#e5e7eb"
        )
        contenedor.pack(fill="both", expand=True, padx=1, pady=1)

        claro_check = "✓" if not self.modo_oscuro else ""
        oscuro_check = "✓" if self.modo_oscuro else ""

        self.crear_item_menu(
            contenedor,
            "☼",
            f"Modo Claro {claro_check}",
            lambda: self.aplicar_tema(False)
        )

        self.crear_item_menu(
            contenedor,
            "●",
            f"Modo Oscuro {oscuro_check}",
            lambda: self.aplicar_tema(True)
        )
    def mostrar_menu_usuario(self, boton):
        if self.menu_usuario_popup and self.menu_usuario_popup.winfo_exists():
            self.cerrar_menus_usuario()
            return

        self.cerrar_menus_usuario()
        self.root.update_idletasks()

        ancho_menu = 210
        alto_menu = 156
        pantalla_ancho = self.root.winfo_screenwidth()
        pantalla_alto = self.root.winfo_screenheight()

        x = boton.winfo_rootx() + boton.winfo_width() - ancho_menu
        y = boton.winfo_rooty() + boton.winfo_height() + 8

        x = max(10, min(x, pantalla_ancho - ancho_menu - 10))
        y = max(10, min(y, pantalla_alto - alto_menu - 10))

        self.menu_usuario_popup = tk.Toplevel(self.root)
        self.menu_usuario_popup.overrideredirect(True)
        self.menu_usuario_popup.configure(bg="#dddddd")
        self.menu_usuario_popup.geometry(f"{ancho_menu}x{alto_menu}+{x}+{y}")

        contenedor = tk.Frame(
            self.menu_usuario_popup,
            bg="white",
            highlightthickness=1,
            highlightbackground="#e5e7eb"
        )
        contenedor.pack(fill="both", expand=True, padx=1, pady=1)

        item_ajustes = self.crear_item_menu(
            contenedor,
            "⚙",
            "Ajustes",
            lambda: self.mostrar_submenu_tema(x, y),
            flecha=True
        )
        item_ajustes.bind("<Enter>", lambda e: self.mostrar_submenu_tema(x, y))

        self.crear_item_menu(
            contenedor,
            "☏",
            "Soporte",
            self.mostrar_soporte
        )

        self.crear_item_menu(
            contenedor,
            "⇱",
            "Cerrar Sesión",
            self.cerrar_sesion
        )

    def seleccionar_registro(self, titulo, columnas, consulta):
        v = tk.Toplevel(self.root)
        v.title(titulo)
        v.geometry("760x420")

        tk.Label(
            v,
            text=titulo.upper(),
            font=("Segoe UI", 13, "bold"),
            pady=15
        ).pack()

        tree = ttk.Treeview(v, columns=columnas, show="headings")

        for col in columnas:
            tree.heading(col, text=col)
            tree.column(col, width=130, anchor="center")

        tree.pack(expand=True, fill="both", padx=20, pady=10)

        for registro in self.obtener_lista_db(consulta):
            tree.insert("", "end", values=registro)

        seleccion = {"values": None}

        def aceptar(event=None):
            item = tree.selection()
            if not item:
                messagebox.showwarning("Atención", "Selecciona un registro.")
                return

            seleccion["values"] = tree.item(item, "values")
            v.destroy()

        tk.Button(
            v,
            text="EDITAR SELECCIONADO",
            command=aceptar,
            bg="#3498db",
            fg="white"
        ).pack(pady=10)

        tree.bind("<Double-1>", aceptar)
        self.root.wait_window(v)
        return seleccion["values"]

    def ventana_recuperar_password(self):
        v = tk.Toplevel(self.root)
        v.title("Recuperar contraseña")
        v.geometry("430x430")
        v.configure(bg="white")
        v.resizable(False, False)

        tk.Label(
            v,
            text="¿Olvidaste tu contraseña?",
            font=("Segoe UI", 16, "bold"),
            bg="white",
            fg="#f39c12"
        ).pack(pady=(28, 8))

        tk.Label(
            v,
            text="Selecciona tu usuario y crea una contraseña nueva.",
            font=("Segoe UI", 10),
            bg="white",
            fg="#7f8c8d"
        ).pack(pady=(0, 22))

        formulario = tk.Frame(v, bg="white", padx=42)
        formulario.pack(fill="x")

        usuarios = self.obtener_lista_db(
            """
            SELECT usuario_login, nombre_completo
            FROM usuarios
            ORDER BY nombre_completo
            """
        )

        nombres_usuario = [
            f"{nombre} ({usuario})"
            for usuario, nombre in usuarios
        ]

        mapa_usuarios = {
            f"{nombre} ({usuario})": usuario
            for usuario, nombre in usuarios
        }

        tk.Label(
            formulario,
            text="Usuario:",
            bg="white",
            fg="#2c3e50",
            font=("Segoe UI", 10, "bold")
        ).pack(anchor="w")

        cb_usuario = ttk.Combobox(
            formulario,
            values=nombres_usuario,
            state="readonly"
        )
        cb_usuario.pack(fill="x", pady=(6, 16), ipady=4)

        if nombres_usuario:
            cb_usuario.current(0)

        tk.Label(
            formulario,
            text="Nueva contraseña:",
            bg="white",
            fg="#2c3e50",
            font=("Segoe UI", 10, "bold")
        ).pack(anchor="w")

        ent_nueva = tk.Entry(formulario, show="*", relief="solid", bd=1)
        ent_nueva.pack(fill="x", pady=(6, 16), ipady=5)

        tk.Label(
            formulario,
            text="Confirmar contraseña:",
            bg="white",
            fg="#2c3e50",
            font=("Segoe UI", 10, "bold")
        ).pack(anchor="w")

        ent_confirmar = tk.Entry(formulario, show="*", relief="solid", bd=1)
        ent_confirmar.pack(fill="x", pady=(6, 22), ipady=5)

        def guardar_password():
            etiqueta_usuario = cb_usuario.get()
            usuario_login = mapa_usuarios.get(etiqueta_usuario)
            nueva = ent_nueva.get().strip()
            confirmar = ent_confirmar.get().strip()

            if not usuario_login:
                messagebox.showwarning("Atención", "Selecciona un usuario.")
                return

            if not nueva or not confirmar:
                messagebox.showwarning("Atención", "Complete ambos campos.")
                return

            if len(nueva) < 4:
                messagebox.showwarning(
                    "Atención",
                    "La contraseña debe tener al menos 4 caracteres."
                )
                return

            if nueva != confirmar:
                messagebox.showerror(
                    "Error",
                    "Las contraseñas no coinciden."
                )
                return

            self.ejecutar_db(
                """
                UPDATE usuarios
                SET password=?
                WHERE usuario_login=?
                """,
                (nueva, usuario_login)
            )

            messagebox.showinfo(
                "Éxito",
                "Contraseña actualizada correctamente."
            )

            if hasattr(self, "combo_user"):
                self.combo_user.set(usuario_login)

            if hasattr(self, "entry_pass"):
                self.entry_pass.delete(0, tk.END)
                self.entry_pass.focus()

            v.destroy()

        ent_confirmar.bind("<Return>", lambda e: guardar_password())

        tk.Button(
            v,
            text="CAMBIAR CONTRASEÑA",
            bg="#f39c12",
            fg="white",
            font=("Segoe UI", 10, "bold"),
            bd=0,
            width=26,
            height=2,
            cursor="hand2",
            command=guardar_password
        ).pack(pady=6)

    def pantalla_login(self):
        self.limpiar_pantalla()

        self.root.state("normal")
        self.root.geometry("1200x850")
        self.root.configure(bg=self.color_fondo)

        card = tk.Frame(
            self.root,
            bg=self.color_card,
            padx=35,
            pady=25,
            highlightbackground="#f4a261",
            highlightthickness=2
        )
        card.place(relx=0.5, rely=0.5, anchor="center")

        try:
            if os.path.exists(self.ruta_logo):
                logo = Image.open(self.ruta_logo)
                logo = logo.resize((170, 170))
                self.logo_login = ImageTk.PhotoImage(logo)

                tk.Label(
                    card,
                    image=self.logo_login,
                    bg=self.color_card
                ).pack()
        except Exception as e:
            print("ERROR LOGO:", e)

        tk.Label(
            card,
            text="Iniciar Sesión",
            font=("Segoe UI", 18, "bold"),
            fg="#f39c12",
            bg=self.color_card
        ).pack(pady=(5, 20))

        tk.Label(
            card,
            text="Usuario",
            bg=self.color_card,
            fg=self.color_texto
        ).pack(anchor="w")

        usuarios = self.obtener_usuarios()

        self.combo_user = ttk.Combobox(
            card,
            values=usuarios,
            state="readonly",
            width=28
        )

        if usuarios:
            self.combo_user.current(0)

        self.combo_user.pack(pady=(6, 15), ipady=4)

        tk.Label(
            card,
            text="Contraseña",
            bg=self.color_card,
            fg=self.color_texto
        ).pack(anchor="w")

        self.entry_pass = tk.Entry(card, show="*", width=30)
        self.entry_pass.pack(pady=(6, 18), ipady=5)
        self.entry_pass.focus()

        def login():
            usuario = self.combo_user.get()
            password = self.entry_pass.get()

            res = self.obtener_lista_db(
                """
                SELECT nombre_completo, rol
                FROM usuarios
                WHERE usuario_login=? AND password=?
                """,
                (usuario, password)
            )

            if res:
                self.usuario_actual, self.rol_actual = res[0]
                self.menu_principal()
            else:
                messagebox.showerror(
                    "Error",
                    "Usuario o contraseña incorrecta"
                )

        self.entry_pass.bind("<Return>", lambda e: login())

        tk.Button(
            card,
            text="ENTRAR",
            bg="#f39c12",
            fg="white",
            font=("Segoe UI", 10, "bold"),
            bd=0,
            width=22,
            command=login
        ).pack(pady=8)

        tk.Button(
            card,
            text="¿Olvidaste tu contraseña?",
            bg=self.color_card,
            fg="#3498db",
            activebackground=self.color_card,
            activeforeground="#2980b9",
            font=("Segoe UI", 9, "underline"),
            bd=0,
            cursor="hand2",
            command=self.ventana_recuperar_password
        ).pack(pady=(2, 0))

    def menu_principal(self):
        self.limpiar_pantalla()

        try:
            self.root.state("zoomed")
        except Exception:
            self.root.attributes("-zoomed", True)

        self.root.configure(bg=self.color_fondo)

        header = tk.Frame(self.root, bg=self.color_header, height=120)
        header.pack(fill="x")
        header.pack_propagate(False)

        try:
            if os.path.exists(self.ruta_logo):
                logo = Image.open(self.ruta_logo)
                logo = logo.resize((90, 90))
                self.logo_menu = ImageTk.PhotoImage(logo)

                tk.Label(
                    header,
                    image=self.logo_menu,
                    bg=self.color_header
                ).place(x=25, y=15)
        except Exception as e:
            print("ERROR LOGO:", e)

        panel_usuario = tk.Frame(header, bg=self.color_header)
        panel_usuario.place(relx=0.98, rely=0.5, anchor="e")

        tk.Label(
            panel_usuario,
            text=f"👤 Hola, {self.usuario_actual}",
            bg=self.color_header,
            fg="white",
            font=("Segoe UI", 12, "bold")
        ).pack(side="left", padx=(0, 22))

        tk.Frame(
            panel_usuario,
            bg="#f7b267",
            width=2,
            height=40
        ).pack(side="left", padx=(0, 22))

        btn_menu_usuario = tk.Button(
            panel_usuario,
            text="☰  Menú",
            bg="#f28c18",
            fg="white",
            activebackground="#e67e22",
            activeforeground="white",
            font=("Segoe UI", 11, "bold"),
            bd=0,
            padx=22,
            pady=10,
            cursor="hand2"
        )
        btn_menu_usuario.pack(side="left")

        btn_menu_usuario.configure(
            command=lambda b=btn_menu_usuario: self.mostrar_menu_usuario(b)
        )

        tk.Button(
            header,
            text="🛡 Respaldo",
            bg="#34495e",
            fg="white",
            activebackground="#2c3e50",
            activeforeground="white",
            font=("Segoe UI", 10, "bold"),
            bd=0,
            padx=15,
            pady=8,
            cursor="hand2",
            command=self.ventana_respaldos
        ).place(relx=0.34, rely=0.5, anchor="center")

        tk.Button(
            header,
            text="📊 Reportes",
            bg="#16a085",
            fg="white",
            activebackground="#138d75",
            activeforeground="white",
            font=("Segoe UI", 10, "bold"),
            bd=0,
            padx=15,
            pady=8,
            cursor="hand2",
            command=self.ventana_reportes_financieros
        ).place(relx=0.46, rely=0.5, anchor="center")

        tk.Button(
            header,
            text="📬 Mensajes",
            bg="#e74c3c",
            fg="white",
            activebackground="#c0392b",
            activeforeground="white",
            font=("Segoe UI", 10, "bold"),
            bd=0,
            padx=15,
            pady=8,
            cursor="hand2",
            command=self.ventana_comunicacion
        ).place(relx=0.59, rely=0.5, anchor="center")

        contenedor = tk.Frame(self.root, bg=self.color_fondo)
        contenedor.pack(expand=True, fill="both")

        grid_frame = tk.Frame(contenedor, bg=self.color_fondo)
        grid_frame.place(relx=0.5, rely=0.5, anchor="center")

        modulos = [
            ("Registrar Publicidad", "#3498db", "👥", self.ventana_registrar_cliente_formal),
            ("Crear Proyecto", "#2ecc71", "➕", self.ventana_crear_proyecto),
            ("Historial Pro", "#9b59b6", "📋", self.ventana_historial),
            ("Publicidad", "#f1c40f", "🎨", self.ventana_publicidad_editor),
            ("Continuar", "#e74c3c", "🚀", self.ventana_continuar_proyecto),
            ("Pagos", "#e67e22", "💰", self.ventana_pagos),
            ("Facturas", "#8e44ad", "📄", self.ventana_facturas),
            ("Portal ID", "#34495e", "🆔", self.ventana_portal_empresa)
        ]

        fila = 0
        columna = 0

        for texto, color, icono, comando in modulos:
            card = tk.Frame(
                grid_frame,
                bg=self.color_card,
                width=190,
                height=220,
                highlightbackground="#f4a261",
                highlightthickness=2
            )
            card.grid(row=fila, column=columna, padx=18, pady=18)
            card.grid_propagate(False)

            contenido = tk.Frame(card, bg=self.color_card)
            contenido.place(relx=0.5, rely=0.5, anchor="center")

            tk.Label(
                contenido,
                text=icono,
                font=("Segoe UI Emoji", 48),
                fg=color,
                bg=self.color_card
            ).pack(pady=(0, 18))

            tk.Label(
                contenido,
                text=texto,
                font=("Segoe UI", 13, "bold"),
                fg=self.color_texto,
                bg=self.color_card
            ).pack(pady=(0, 22))

            tk.Button(
                contenido,
                text="ACCEDER",
                bg=color,
                fg="white",
                font=("Segoe UI", 10, "bold"),
                bd=0,
                width=18,
                height=2,
                cursor="hand2",
                command=comando
            ).pack()

            columna += 1
            if columna > 3:
                columna = 0
                fila += 1

    def ventana_registrar_cliente_formal(self, id_cliente_editar=None):
        v = tk.Toplevel(self.root)
        v.title("Registrar Publicidad (Empresa)")
        v.geometry("450x690")
        v.configure(bg="white")

        datos_editar = None

        if id_cliente_editar:
            datos = self.obtener_lista_db(
                """
                SELECT nombre_empresa, telefono_referido, correo, direccion_empresa
                FROM clientes
                WHERE id_cliente=?
                """,
                (id_cliente_editar,)
            )
            datos_editar = datos[0] if datos else None

        titulo = "EDITAR PUBLICIDAD" if id_cliente_editar else "REGISTRAR PUBLICIDAD"

        tk.Label(
            v,
            text=titulo,
            font=("Segoe UI", 16, "bold"),
            bg="white",
            fg="#3498db"
        ).pack(pady=30)

        f = tk.Frame(v, bg="white", padx=40)
        f.pack(fill="both")

        tk.Label(f, text="Nombre de la Empresa:", bg="white").pack(anchor="w")
        nom_e = tk.Entry(f, relief="solid", bd=1)
        nom_e.pack(fill="x", pady=(5, 15))

        tk.Label(f, text="Numero Telefonico Referido:", bg="white").pack(anchor="w")
        tel_e = tk.Entry(f, relief="solid", bd=1)
        tel_e.pack(fill="x", pady=(5, 15))

        tk.Label(f, text="Correo Electronico:", bg="white").pack(anchor="w")
        cor_e = tk.Entry(f, relief="solid", bd=1)
        cor_e.pack(fill="x", pady=(5, 15))

        tk.Label(f, text="Direccion de la Empresa:", bg="white").pack(anchor="w")
        dir_e = tk.Entry(f, relief="solid", bd=1)
        dir_e.pack(fill="x", pady=(5, 30))

        if datos_editar:
            nom_e.insert(0, datos_editar[0])
            tel_e.insert(0, datos_editar[1] or "")
            cor_e.insert(0, datos_editar[2] or "")
            dir_e.insert(0, datos_editar[3] or "")

        def editar_existente():
            seleccionado = self.seleccionar_registro(
                "Editar empresa registrada",
                ("ID", "Empresa", "UUID"),
                """
                SELECT id_cliente, nombre_empresa, uuid_empresa
                FROM clientes
                ORDER BY nombre_empresa
                """
            )

            if seleccionado:
                v.destroy()
                self.ventana_registrar_cliente_formal(int(seleccionado[0]))

        def guardar():
            nombre = nom_e.get().strip()

            if not nombre:
                messagebox.showwarning(
                    "Atencion",
                    "El nombre de la empresa es obligatorio."
                )
                return

            existe = self.obtener_lista_db(
                """
                SELECT id_cliente
                FROM clientes
                WHERE nombre_empresa=? AND id_cliente<>?
                """,
                (nombre, id_cliente_editar or 0)
            )

            if existe:
                messagebox.showerror(
                    "Error",
                    f"La empresa '{nombre}' ya esta registrada."
                )
                return

            try:
                if id_cliente_editar:
                    self.ejecutar_db(
                        """
                        UPDATE clientes
                        SET nombre_empresa=?, telefono_referido=?, correo=?, direccion_empresa=?
                        WHERE id_cliente=?
                        """,
                        (
                            nombre,
                            tel_e.get(),
                            cor_e.get(),
                            dir_e.get(),
                            id_cliente_editar
                        )
                    )

                    messagebox.showinfo(
                        "Exito",
                        "Empresa actualizada correctamente."
                    )
                else:
                    id_personal = "PUB-" + str(uuid.uuid4())[:8].upper()

                    self.ejecutar_db(
                        """
                        INSERT INTO clientes
                        (nombre_empresa, telefono_referido, correo, direccion_empresa, uuid_empresa)
                        VALUES (?, ?, ?, ?, ?)
                        """,
                        (
                            nombre,
                            tel_e.get(),
                            cor_e.get(),
                            dir_e.get(),
                            id_personal
                        )
                    )

                    messagebox.showinfo(
                        "Exito",
                        f"Empresa registrada.\nID PERSONAL: {id_personal}"
                    )

                v.destroy()

            except Exception as e:
                messagebox.showerror("Error", f"No se pudo guardar: {e}")

        tk.Button(
            v,
            text="Guardar Cambios" if id_cliente_editar else "Guardar Registro",
            bg="#2ecc71",
            fg="white",
            font=("Segoe UI", 11, "bold"),
            relief="flat",
            height=2,
            width=30,
            command=guardar
        ).pack(pady=6)

        tk.Button(
            v,
            text="Editar",
            bg="#3498db",
            fg="white",
            font=("Segoe UI", 10, "bold"),
            relief="flat",
            height=2,
            width=30,
            command=editar_existente
        ).pack(pady=6)

    def ventana_crear_proyecto(self, id_proyecto_editar=None):
        v = tk.Toplevel(self.root)
        v.title("Crear Nuevo Proyecto")
        v.geometry("450x590")
        v.configure(bg="white")

        datos_editar = None

        if id_proyecto_editar:
            datos = self.obtener_lista_db(
                """
                SELECT id_cliente, nombre, fecha_inicio, estado
                FROM proyectos
                WHERE id_proyecto=?
                """,
                (id_proyecto_editar,)
            )
            datos_editar = datos[0] if datos else None

        titulo = "EDITAR PROYECTO" if id_proyecto_editar else "NUEVO PROYECTO"

        tk.Label(
            v,
            text=titulo,
            font=("Segoe UI", 16, "bold"),
            bg="white",
            fg="#2ecc71"
        ).pack(pady=30)

        f = tk.Frame(v, bg="white", padx=40)
        f.pack(fill="both")

        tk.Label(f, text="Seleccionar Empresa:", bg="white").pack(anchor="w")

        clientes_db = self.obtener_lista_db(
            """
            SELECT id_cliente, nombre_empresa
            FROM clientes
            ORDER BY nombre_empresa
            """
        )

        dict_clientes = {
            nombre: id_cli
            for id_cli, nombre in clientes_db
        }

        cb_clientes = ttk.Combobox(
            f,
            values=list(dict_clientes.keys()),
            state="readonly"
        )
        cb_clientes.pack(fill="x", pady=(5, 15))

        tk.Label(f, text="Nombre del Proyecto:", bg="white").pack(anchor="w")
        ent_nombre_p = tk.Entry(f, relief="solid", bd=1)
        ent_nombre_p.pack(fill="x", pady=(5, 15))

        tk.Label(f, text="Fecha de Inicio:", bg="white").pack(anchor="w")

        ent_fecha = DateEntry(
            f,
            width=12,
            background="darkblue",
            foreground="white",
            borderwidth=2,
            date_pattern="dd/mm/yyyy"
        )
        ent_fecha.pack(fill="x", pady=(5, 15))

        tk.Label(f, text="Estado Inicial:", bg="white").pack(anchor="w")

        cb_estado = ttk.Combobox(
            f,
            values=["En Espera", "Trabajando", "Finalizado"],
            state="readonly"
        )
        cb_estado.current(0)
        cb_estado.pack(fill="x", pady=(5, 30))

        if datos_editar:
            id_cliente, nombre, fecha, estado = datos_editar

            for nombre_empresa, id_cli in dict_clientes.items():
                if id_cli == id_cliente:
                    cb_clientes.set(nombre_empresa)
                    break

            ent_nombre_p.insert(0, nombre)

            try:
                ent_fecha.set_date(datetime.strptime(fecha, "%d/%m/%Y"))
            except Exception:
                pass

            cb_estado.set(estado)

        def editar_existente():
            seleccionado = self.seleccionar_registro(
                "Editar proyecto",
                ("ID", "Proyecto", "Empresa", "Estado"),
                """
                SELECT p.id_proyecto, p.nombre, c.nombre_empresa, p.estado
                FROM proyectos p
                JOIN clientes c ON p.id_cliente = c.id_cliente
                ORDER BY p.id_proyecto DESC
                """
            )

            if seleccionado:
                v.destroy()
                self.ventana_crear_proyecto(int(seleccionado[0]))

        def guardar_proy():
            emp = cb_clientes.get()
            nom = ent_nombre_p.get().strip()

            if not emp or not nom:
                messagebox.showwarning("Error", "Complete los campos.")
                return

            try:
                if id_proyecto_editar:
                    self.ejecutar_db(
                        """
                        UPDATE proyectos
                        SET id_cliente=?, nombre=?, fecha_inicio=?, estado=?
                        WHERE id_proyecto=?
                        """,
                        (
                            dict_clientes[emp],
                            nom,
                            ent_fecha.get(),
                            cb_estado.get(),
                            id_proyecto_editar
                        )
                    )

                    messagebox.showinfo(
                        "Exito",
                        "Proyecto actualizado correctamente."
                    )
                else:
                    self.ejecutar_db(
                        """
                        INSERT INTO proyectos
                        (id_cliente, nombre, fecha_inicio, estado)
                        VALUES (?, ?, ?, ?)
                        """,
                        (
                            dict_clientes[emp],
                            nom,
                            ent_fecha.get(),
                            cb_estado.get()
                        )
                    )

                    messagebox.showinfo(
                        "Exito",
                        "Proyecto guardado correctamente."
                    )

                v.destroy()

            except Exception as e:
                messagebox.showerror("Error", str(e))

        tk.Button(
            v,
            text="GUARDAR CAMBIOS" if id_proyecto_editar else "REGISTRAR PROYECTO",
            bg="#2ecc71",
            fg="white",
            font=("Segoe UI", 11, "bold"),
            relief="flat",
            height=2,
            width=30,
            command=guardar_proy
        ).pack(pady=6)

        tk.Button(
            v,
            text="Editar",
            bg="#3498db",
            fg="white",
            font=("Segoe UI", 10, "bold"),
            relief="flat",
            height=2,
            width=30,
            command=editar_existente
        ).pack(pady=6)

    def ventana_historial(self):
        v = tk.Toplevel(self.root)
        v.title("Historial de Proyectos")
        v.geometry("1100x750")
        v.configure(bg="#f4f7f6")

        frame_busqueda = tk.Frame(v, bg="#34495e", pady=15)
        frame_busqueda.pack(fill="x")

        tk.Label(
            frame_busqueda,
            text="BUSCAR POR ID:",
            fg="white",
            bg="#34495e",
            font=("Segoe UI", 9, "bold")
        ).pack(side="left", padx=(20, 5))

        ent_id_busq = tk.Entry(frame_busqueda, font=("Consolas", 11), width=15)
        ent_id_busq.pack(side="left", padx=10)

        tk.Label(
            frame_busqueda,
            text="NOMBRE PROYECTO:",
            fg="white",
            bg="#34495e",
            font=("Segoe UI", 9, "bold")
        ).pack(side="left", padx=(20, 5))

        ent_nom_busq = tk.Entry(frame_busqueda, font=("Segoe UI", 11), width=20)
        ent_nom_busq.pack(side="left", padx=10)

        cuerpo = tk.Frame(
            v,
            bg="white",
            padx=20,
            pady=20,
            highlightthickness=1,
            highlightbackground="#dee2e6"
        )
        cuerpo.pack(expand=True, fill="both", padx=20, pady=20)

        tk.Label(
            cuerpo,
            text="DIRECTORIO DE EMPRESAS",
            font=("Segoe UI", 11, "bold"),
            bg="white",
            fg="#3498db"
        ).pack()

        cols_c = ("Empresa", "ID Personal")
        tree_clientes = ttk.Treeview(
            cuerpo,
            columns=cols_c,
            show="headings",
            height=5
        )

        for col in cols_c:
            tree_clientes.heading(col, text=col)

        tree_clientes.pack(fill="x", pady=10)

        tk.Label(
            cuerpo,
            text="REGISTROS DE PROYECTOS",
            font=("Segoe UI", 10, "bold"),
            bg="white",
            fg="#2c3e50"
        ).pack(pady=(10, 5))

        cols_p = ("Proyecto", "Fecha Inicio", "Estado", "Empresa Relacionada")

        tree_proyectos = ttk.Treeview(
            cuerpo,
            columns=cols_p,
            show="headings"
        )

        for col in cols_p:
            tree_proyectos.heading(col, text=col)

        tree_proyectos.pack(expand=True, fill="both")

        def actualizar_tablas(event=None):
            for i in tree_clientes.get_children():
                tree_clientes.delete(i)

            id_busc = ent_id_busq.get().strip()

            query_c = "SELECT nombre_empresa, uuid_empresa FROM clientes"
            params_c = ()

            if id_busc:
                query_c += " WHERE uuid_empresa LIKE ?"
                params_c = (f"%{id_busc}%",)

            for d in self.obtener_lista_db(query_c, params_c):
                tree_clientes.insert("", "end", values=d)

            for i in tree_proyectos.get_children():
                tree_proyectos.delete(i)

            nom_busc = ent_nom_busq.get().strip()

            query_p = """
                SELECT p.nombre, p.fecha_inicio, p.estado, c.nombre_empresa
                FROM proyectos p
                JOIN clientes c ON p.id_cliente = c.id_cliente
                WHERE 1=1
            """

            params_p = []

            if id_busc:
                query_p += " AND c.uuid_empresa LIKE ?"
                params_p.append(f"%{id_busc}%")

            if nom_busc:
                query_p += " AND p.nombre LIKE ?"
                params_p.append(f"%{nom_busc}%")

            for p in self.obtener_lista_db(query_p, tuple(params_p)):
                tree_proyectos.insert("", "end", values=p)

        def al_seleccionar_cliente(event):
            item = tree_clientes.selection()

            if item:
                uuid_sel = tree_clientes.item(item)["values"][1]
                ent_id_busq.delete(0, tk.END)
                ent_id_busq.insert(0, uuid_sel)
                actualizar_tablas()

        ent_id_busq.bind("<KeyRelease>", actualizar_tablas)
        ent_nom_busq.bind("<KeyRelease>", actualizar_tablas)
        tree_clientes.bind("<<TreeviewSelect>>", al_seleccionar_cliente)

        actualizar_tablas()

    def ventana_portal_empresa(self):
        v = tk.Toplevel(self.root)
        v.title("Portal ID de Empresas")
        v.geometry("600x400")

        tk.Label(
            v,
            text="DIRECTORIO DE IDENTIFICADORES",
            font=("Segoe UI", 14, "bold"),
            pady=20
        ).pack()

        cols = ("Empresa", "UUID / ID Personal")
        tree = ttk.Treeview(v, columns=cols, show="headings")

        tree.heading("Empresa", text="Empresa")
        tree.heading("UUID / ID Personal", text="UUID Personal")

        tree.pack(expand=True, fill="both", padx=20, pady=20)

        for d in self.obtener_lista_db(
            """
            SELECT nombre_empresa, uuid_empresa
            FROM clientes
            ORDER BY nombre_empresa
            """
        ):
            tree.insert("", "end", values=d)

    def ventana_publicidad_editor(self, id_editar=None, id_pub_editar=None):

        v = tk.Toplevel(self.root)
        v.title("Editor Profesional de Publicidad")
        v.geometry("1280x820")
        v.configure(bg="#edf2f7")
        v.minsize(1180, 760)

        self.img_original = None
        self.img_tk = None
        self.path_actual = ""

        historial_imagenes = []

        # =====================================================
        # HEADER
        # =====================================================

        header = tk.Frame(
            v,
            bg="#1e293b",
            height=75
        )

        header.pack(fill="x")
        header.pack_propagate(False)

        tk.Label(
            header,
            text="🎨 Editor Profesional de Publicidad",
            bg="#1e293b",
            fg="white",
            font=("Segoe UI", 20, "bold")
        ).pack(side="left", padx=25)

        tk.Label(
            header,
            text="Diseño • Transparencia • Recorte • Impresión",
            bg="#1e293b",
            fg="#cbd5e1",
            font=("Segoe UI", 10)
        ).pack(side="left")

        # =====================================================
        # CONTENEDOR PRINCIPAL
        # =====================================================

        main = tk.Frame(v, bg="#edf2f7")
        main.pack(fill="both", expand=True, padx=18, pady=18)

        # =====================================================
        # PANEL IZQUIERDO
        # =====================================================

        panel = tk.Frame(
            main,
            bg="white",
            width=360,
            padx=16,
            pady=16,
            highlightthickness=1,
            highlightbackground="#dbe2ea"
        )

        panel.pack(side="left", fill="y", padx=(0, 16))
        panel.pack_propagate(False)

        # =====================================================
        # VISOR
        # =====================================================

        visor_frame = tk.Frame(
            main,
            bg="white",
            padx=14,
            pady=14,
            highlightthickness=1,
            highlightbackground="#dbe2ea"
        )

        visor_frame.pack(side="right", fill="both", expand=True)

        canvas = tk.Canvas(
            visor_frame,
            bg="#f8fafc",
            highlightthickness=0
        )

        canvas.pack(fill="both", expand=True)

        # =====================================================
        # ESTILOS
        # =====================================================

        def titulo(txt):

            tk.Label(
                panel,
                text=txt,
                bg="white",
                fg="#1e293b",
                font=("Segoe UI", 11, "bold")
            ).pack(anchor="w", pady=(0, 7))

        def separador():

            tk.Frame(
                panel,
                bg="#e2e8f0",
                height=1
            ).pack(fill="x", pady=12)

        def boton_estilo(master, texto, color, comando):

            return tk.Button(
                master,
                text=texto,
                command=comando,
                bg=color,
                fg="white",
                activebackground=color,
                activeforeground="white",
                relief="flat",
                bd=0,
                cursor="hand2",
                font=("Segoe UI", 9, "bold"),
                height=2,
                padx=5,
                pady=2
            )

        # =====================================================
        # DATOS
        # =====================================================

        titulo("Datos del trabajo")

        tk.Label(
            panel,
            text="UUID Empresa",
            bg="white",
            fg="#475569",
            font=("Segoe UI", 9)
        ).pack(anchor="w")

        ent_uuid = tk.Entry(
            panel,
            font=("Consolas", 10),
            relief="solid",
            bd=1
        )

        ent_uuid.pack(fill="x", pady=(3, 10), ipady=4)

        tk.Label(
            panel,
            text="Proyecto",
            bg="white",
            fg="#475569",
            font=("Segoe UI", 9)
        ).pack(anchor="w")

        cb_proyectos = ttk.Combobox(
            panel,
            state="readonly"
        )

        cb_proyectos.pack(fill="x", pady=(3, 10), ipady=3)

        tk.Label(
            panel,
            text="Estado",
            bg="white",
            fg="#475569",
            font=("Segoe UI", 9)
        ).pack(anchor="w")

        cb_estado = ttk.Combobox(
            panel,
            values=[
                "Trabajando",
                "En Espera",
                "Finalizado"
            ],
            state="readonly"
        )

        cb_estado.current(1)

        cb_estado.pack(fill="x", pady=(3, 5), ipady=3)

        separador()

        # =====================================================
        # TRANSPARENCIA
        # =====================================================

        titulo("Transparencia")

        alpha = tk.IntVar(value=100)

        slider_frame = tk.Frame(
            panel,
            bg="white"
        )

        slider_frame.pack(fill="x")

        tk.Scale(
            slider_frame,
            from_=20,
            to=100,
            orient="horizontal",
            variable=alpha,
            bg="white",
            fg="#334155",
            highlightthickness=0,
            length=285
        ).pack()

        separador()

        # =====================================================
        # HERRAMIENTAS
        # =====================================================

        titulo("Herramientas")

        herramientas = tk.Frame(
            panel,
            bg="white"
        )

        herramientas.pack(fill="x")

        for i in range(2):
            herramientas.grid_columnconfigure(i, weight=1)

        # =====================================================
        # FUNCIONES
        # =====================================================

        def actualizar_preview():

            canvas.delete("all")
            canvas.update_idletasks()

            w = canvas.winfo_width()
            h = canvas.winfo_height()

            if self.img_original:

                img = self.img_original.copy()

                img.thumbnail((w - 40, h - 40))

                self.img_tk = ImageTk.PhotoImage(img)

                canvas.create_image(
                    w / 2,
                    h / 2,
                    image=self.img_tk
                )

            else:

                canvas.create_text(
                    w / 2,
                    h / 2 - 20,
                    text="🖼",
                    fill="#94a3b8",
                    font=("Segoe UI Emoji", 60)
                )

                canvas.create_text(
                    w / 2,
                    h / 2 + 45,
                    text="Sin imagen cargada",
                    fill="#64748b",
                    font=("Segoe UI", 13, "bold")
                )

        def guardar_estado():

            if self.img_original:
                historial_imagenes.append(
                    self.img_original.copy()
                )

        def cargar_proyectos_de_empresa(event=None):

            uuid_busqueda = ent_uuid.get().strip()

            proys = self.obtener_lista_db(
                """
                SELECT p.nombre
                FROM proyectos p
                         JOIN clientes c
                              ON p.id_cliente = c.id_cliente
                WHERE c.uuid_empresa = ?
                """,
                (uuid_busqueda,)
            )

            lista = [p[0] for p in proys]

            cb_proyectos["values"] = lista

            if lista:
                cb_proyectos.current(0)
            else:
                cb_proyectos.set("Sin proyectos")

        def cargar_foto():

            path = filedialog.askopenfilename(
                filetypes=[
                    ("Imágenes", "*.png *.jpg *.jpeg")
                ]
            )

            if path:
                self.img_original = Image.open(path)
                self.path_actual = path

                historial_imagenes.clear()

                actualizar_preview()

        def eliminar_imagen():

            if not self.img_original:
                messagebox.showwarning(
                    "Atención",
                    "No hay imagen cargada."
                )

                return

            confirmar = messagebox.askyesno(
                "Eliminar",
                "¿Desea eliminar la imagen?"
            )

            if not confirmar:
                return

            self.img_original = None
            self.img_tk = None
            self.path_actual = ""

            historial_imagenes.clear()

            actualizar_preview()

        def recortar_centro():

            if not self.img_original:
                return

            guardar_estado()

            w, h = self.img_original.size

            self.img_original = self.img_original.crop(
                (
                    w * 0.1,
                    h * 0.1,
                    w * 0.9,
                    h * 0.9
                )
            )

            actualizar_preview()

        def convertir_gris():

            if not self.img_original:
                return

            guardar_estado()

            self.img_original = ImageOps.grayscale(
                self.img_original
            )

            actualizar_preview()

        def hacer_transparente():

            if not self.img_original:
                return

            guardar_estado()

            img = self.img_original.convert("RGBA")

            datos = []

            for r, g, b, a in img.getdata():

                if r > 235 and g > 235 and b > 235:

                    datos.append(
                        (255, 255, 255, 0)
                    )

                else:

                    datos.append(
                        (
                            r,
                            g,
                            b,
                            int(a * (alpha.get() / 100))
                        )
                    )

            img.putdata(datos)

            self.img_original = img

            actualizar_preview()

        def deshacer_cambio():

            if historial_imagenes:
                self.img_original = historial_imagenes.pop()

                actualizar_preview()

        def editar_existente():

            seleccionado = self.seleccionar_registro(
                "Editar publicidad",
                (
                    "ID",
                    "UUID",
                    "Proyecto",
                    "Estado",
                    "Fecha"
                ),
                """
                SELECT id_pub,
                       uuid_empresa,
                       COALESCE(proyecto, ''),
                       estado,
                       fecha
                FROM publicidad
                ORDER BY id_pub DESC
                """
            )

            if seleccionado:
                v.destroy()

                self.ventana_publicidad_editor(
                    id_pub_editar=int(seleccionado[0])
                )

        def guardar_imagen_editada():

            if not self.img_original:
                messagebox.showwarning(
                    "Atención",
                    "No hay imagen."
                )

                return

            ruta = filedialog.asksaveasfilename(
                defaultextension=".png",
                filetypes=[
                    ("PNG", "*.png"),
                    ("JPEG", "*.jpg")
                ]
            )

            if not ruta:
                return

            img = self.img_original

            if ruta.lower().endswith(
                    (".jpg", ".jpeg")
            ):
                img = img.convert("RGB")

            img.save(ruta)

            self.path_actual = ruta

            messagebox.showinfo(
                "Guardado",
                "Imagen guardada correctamente."
            )

        def imprimir_imagen():

            if not self.img_original:
                return

            ruta_temp = os.path.join(
                os.path.dirname(self.ruta_db),
                "publicidad_temp.png"
            )

            self.img_original.save(ruta_temp)

            try:

                os.startfile(ruta_temp, "print")

            except Exception as e:

                messagebox.showerror(
                    "Error",
                    str(e)
                )

        def guardar_db():

            id_emp = ent_uuid.get().strip()
            proy_sel = cb_proyectos.get()

            if not id_emp or not self.img_original:
                messagebox.showwarning(
                    "Atención",
                    "Complete los datos requeridos."
                )

                return

            if id_pub_editar:

                self.ejecutar_db(
                    """
                    UPDATE publicidad
                    SET uuid_empresa=?,
                        nombre_archivo=?,
                        estado=?,
                        fecha=?,
                        proyecto=?
                    WHERE id_pub = ?
                    """,
                    (
                        id_emp,
                        self.path_actual,
                        cb_estado.get(),
                        datetime.now().strftime("%d/%m/%Y"),
                        proy_sel,
                        id_pub_editar
                    )
                )

            else:

                self.ejecutar_db(
                    """
                    INSERT INTO publicidad
                    (uuid_empresa,
                     nombre_archivo,
                     estado,
                     fecha,
                     proyecto)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        id_emp,
                        self.path_actual,
                        cb_estado.get(),
                        datetime.now().strftime("%d/%m/%Y"),
                        proy_sel
                    )
                )

            messagebox.showinfo(
                "Éxito",
                "Publicidad guardada correctamente."
            )

            v.destroy()

        def guardar_completo():

            guardar_imagen_editada()
            guardar_db()

        # =====================================================
        # BOTONES HERRAMIENTAS
        # =====================================================

        botones = [

            ("📂 Subir", "#10b981", cargar_foto),
            ("🗑 Eliminar", "#ef4444", eliminar_imagen),

            ("✂️ Recortar", "#f59e0b", recortar_centro),
            ("🌓 Escala gris", "#6b7280", convertir_gris),

            ("🪄 Transparencia", "#14b8a6", hacer_transparente),
            ("↶ Deshacer", "#64748b", deshacer_cambio),

            ("✏️ Editar", "#8b5cf6", editar_existente)

        ]

        fila = 0
        col = 0

        for texto, color, comando in botones:

            btn = boton_estilo(
                herramientas,
                texto,
                color,
                comando
            )

            btn.grid(
                row=fila,
                column=col,
                sticky="ew",
                padx=4,
                pady=4
            )

            col += 1

            if col > 1:
                col = 0
                fila += 1

        separador()

        # =====================================================
        # ACCIONES
        # =====================================================

        titulo("Archivo")

        acciones = tk.Frame(
            panel,
            bg="white"
        )

        acciones.pack(fill="x")

        boton_estilo(
            acciones,
            "💾 Guardar imagen",
            "#22c55e",
            guardar_imagen_editada
        ).pack(fill="x", pady=4)

        boton_estilo(
            acciones,
            "🖨 Imprimir publicidad",
            "#334155",
            imprimir_imagen
        ).pack(fill="x", pady=4)

        boton_estilo(
            acciones,
            "💾 Guardar publicidad",
            "#3b82f6",
            guardar_db
        ).pack(fill="x", pady=4)

        boton_estilo(
            acciones,
            "✅ Guardar",
            "#0f766e",
            guardar_completo
        ).pack(fill="x", pady=4)

        # =====================================================
        # EVENTOS
        # =====================================================

        ent_uuid.bind(
            "<FocusOut>",
            cargar_proyectos_de_empresa
        )

        canvas.bind(
            "<Configure>",
            lambda e: actualizar_preview()
        )

        # =====================================================
        # MODO EDITAR
        # =====================================================

        if id_editar:
            ent_uuid.insert(0, id_editar)

            cargar_proyectos_de_empresa()

        if id_pub_editar:

            datos = self.obtener_lista_db(
                """
                SELECT uuid_empresa,
                       nombre_archivo,
                       estado,
                       proyecto
                FROM publicidad
                WHERE id_pub = ?
                """,
                (id_pub_editar,)
            )

            if datos:

                uuid_emp, archivo, estado, proyecto = datos[0]

                ent_uuid.insert(0, uuid_emp)

                cargar_proyectos_de_empresa()

                cb_estado.set(estado)

                if proyecto:
                    cb_proyectos.set(proyecto)

                self.path_actual = archivo

                if archivo and os.path.exists(archivo):
                    self.img_original = Image.open(
                        archivo
                    )

        actualizar_preview()

    def ventana_continuar_proyecto(self):
        v = tk.Toplevel(self.root)
        v.title("Panel de Continuidad de Trabajo")
        v.geometry("950x650")
        v.configure(bg="#f8f9fa")

        header_f = tk.Frame(v, bg="#2c3e50", pady=15)
        header_f.pack(fill="x")

        tk.Label(
            header_f,
            text="GESTION DE TRABAJOS PENDIENTES",
            fg="white",
            bg="#2c3e50",
            font=("Segoe UI", 12, "bold")
        ).pack()

        search_f = tk.Frame(v, bg="#f8f9fa", pady=20)
        search_f.pack(fill="x")

        tk.Label(
            search_f,
            text="Ingrese ID de Empresa o Proyecto:",
            bg="#f8f9fa",
            font=("Segoe UI", 10)
        ).pack(side="left", padx=(40, 10))

        ent_id = tk.Entry(
            search_f,
            font=("Consolas", 12),
            width=30,
            relief="solid",
            bd=1
        )
        ent_id.pack(side="left", padx=10)

        tree_frame = tk.Frame(v, bg="white", padx=20, pady=10)
        tree_frame.pack(fill="both", expand=True, padx=30, pady=10)

        cols = ("Tipo", "Nombre / Archivo", "Estado", "Fecha", "UUID")
        tree = ttk.Treeview(tree_frame, columns=cols, show="headings", height=15)

        for c in cols:
            tree.heading(c, text=c.upper())
            tree.column(c, anchor="center", width=120)

        tree.pack(fill="both", expand=True)

        def buscar(event=None):
            for i in tree.get_children():
                tree.delete(i)

            id_b = ent_id.get().strip()

            if not id_b:
                return

            proy = self.obtener_lista_db(
                """
                SELECT 'Proyecto', p.nombre, p.estado, p.fecha_inicio, c.uuid_empresa
                FROM proyectos p
                JOIN clientes c ON p.id_cliente = c.id_cliente
                WHERE c.uuid_empresa LIKE ? OR p.nombre LIKE ?
                """,
                (f"%{id_b}%", f"%{id_b}%")
            )

            pub = self.obtener_lista_db(
                """
                SELECT 'Publicidad', nombre_archivo, estado, fecha, uuid_empresa
                FROM publicidad
                WHERE uuid_empresa LIKE ? OR nombre_archivo LIKE ?
                """,
                (f"%{id_b}%", f"%{id_b}%")
            )

            for r in proy + pub:
                tree.insert("", "end", values=r)

        def ejecutar_accion(event):
            item_sel = tree.selection()

            if not item_sel:
                return

            tipo, nombre, estado, fecha, uuid_e = tree.item(item_sel, "values")

            if estado == "Finalizado":
                self.mostrar_vista_previa_final(nombre, tipo)
            else:
                v.destroy()

                if tipo == "Publicidad":
                    self.ventana_publicidad_editor(id_editar=uuid_e)
                else:
                    messagebox.showinfo(
                        "Proyectos",
                        f"Redirigiendo al modulo de Proyectos para: {nombre}"
                    )

        ent_id.bind("<KeyRelease>", buscar)
        tree.bind("<Double-1>", ejecutar_accion)

        tk.Label(
            v,
            text="Tip: Doble clic sobre un registro para continuar editando o ver resultado.",
            fg="#7f8c8d",
            bg="#f8f9fa",
            font=("Segoe UI", 9, "italic")
        ).pack(pady=10)

    def mostrar_vista_previa_final(self, nombre_recurso, tipo):
        vf = tk.Toplevel(self.root)
        vf.title(f"Resultado Final - {nombre_recurso}")
        vf.geometry("600x500")
        vf.configure(bg="white")

        tk.Label(
            vf,
            text=f"ARCHIVO FINALIZADO: {nombre_recurso}",
            font=("Segoe UI", 12, "bold"),
            bg="white",
            pady=20
        ).pack()

        canvas_preview = tk.Canvas(
            vf,
            bg="#f1f2f6",
            width=500,
            height=350,
            highlightthickness=0
        )
        canvas_preview.pack(pady=10)

        if tipo == "Publicidad" and nombre_recurso and os.path.exists(nombre_recurso):
            img = Image.open(nombre_recurso)
            img.thumbnail((500, 350))
            self.img_preview_final = ImageTk.PhotoImage(img)
            canvas_preview.create_image(250, 175, image=self.img_preview_final)
        else:
            canvas_preview.create_text(
                250,
                175,
                text="[ VISTA PREVIA DEL TRABAJO ]\n(Imagen cargada desde base de datos)",
                justify="center",
                fill="#95a5a6"
            )

        tk.Button(
            vf,
            text="CERRAR VISTA",
            command=vf.destroy,
            bg="#e74c3c",
            fg="white",
            relief="flat",
            width=20
        ).pack(pady=10)

    def ventana_comunicacion(self):
        v = tk.Toplevel(self.root)
        v.title("Mensajes")
        v.geometry("760x580")
        v.configure(bg="#f4f6f8")

        seleccionado = {"id": None, "texto": "", "frame": None}

        header = tk.Frame(v, bg="#f39c12", height=64)
        header.pack(fill="x")
        header.pack_propagate(False)

        tk.Label(
            header,
            text="Mensajes",
            bg="#f39c12",
            fg="white",
            font=("Segoe UI", 17, "bold")
        ).pack(side="left", padx=24)

        tk.Label(
            header,
            text=f"Sesion: {self.usuario_actual}",
            bg="#f39c12",
            fg="white",
            font=("Segoe UI", 10)
        ).pack(side="right", padx=24)

        cuerpo = tk.Frame(v, bg="#f4f6f8")
        cuerpo.pack(fill="both", expand=True, padx=18, pady=(18, 10))

        canvas = tk.Canvas(cuerpo, bg="#f4f6f8", highlightthickness=0)
        scroll = ttk.Scrollbar(cuerpo, orient="vertical", command=canvas.yview)
        chat_frame = tk.Frame(canvas, bg="#f4f6f8")

        canvas_window = canvas.create_window((0, 0), window=chat_frame, anchor="nw")
        canvas.configure(yscrollcommand=scroll.set)
        canvas.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

        def ajustar_scroll(event=None):
            canvas.configure(scrollregion=canvas.bbox("all"))

        def ajustar_ancho(event):
            canvas.itemconfigure(canvas_window, width=event.width)

        chat_frame.bind("<Configure>", ajustar_scroll)
        canvas.bind("<Configure>", ajustar_ancho)

        panel_envio = tk.Frame(v, bg="#ffffff", padx=16, pady=14)
        panel_envio.pack(fill="x", padx=18, pady=(0, 18))

        msj = tk.Entry(panel_envio, font=("Segoe UI", 11), relief="solid", bd=1)
        msj.pack(side="left", fill="x", expand=True, ipady=9, padx=(0, 12))

        placeholder = "Escribe un mensaje"
        placeholder_activo = {"activo": False}

        def mostrar_placeholder():
            if not msj.get().strip():
                placeholder_activo["activo"] = True
                msj.config(fg="#95a5a6")
                msj.delete(0, tk.END)
                msj.insert(0, placeholder)

        def ocultar_placeholder(event=None):
            if placeholder_activo["activo"]:
                placeholder_activo["activo"] = False
                msj.config(fg="#2c3e50")
                msj.delete(0, tk.END)

        def obtener_texto_mensaje():
            if placeholder_activo["activo"]:
                return ""
            return msj.get().strip()

        msj.bind("<FocusIn>", ocultar_placeholder)
        msj.bind("<FocusOut>", lambda e: mostrar_placeholder())

        botones = tk.Frame(panel_envio, bg="#ffffff")
        botones.pack(side="right")

        def limpiar_seleccion():
            if seleccionado["frame"] and seleccionado["frame"].winfo_exists():
                seleccionado["frame"].configure(highlightthickness=0)

            seleccionado["id"] = None
            seleccionado["texto"] = ""
            seleccionado["frame"] = None

        def seleccionar_mensaje(id_mensaje, texto, frame_burbuja):
            if seleccionado["frame"] and seleccionado["frame"].winfo_exists():
                seleccionado["frame"].configure(highlightthickness=0)

            seleccionado["id"] = id_mensaje
            seleccionado["texto"] = texto
            seleccionado["frame"] = frame_burbuja

            frame_burbuja.configure(
                highlightthickness=2,
                highlightbackground="#2980b9"
            )

            placeholder_activo["activo"] = False
            msj.config(fg="#2c3e50")
            msj.delete(0, tk.END)
            msj.insert(0, texto)

        def cargar():
            for widget in chat_frame.winfo_children():
                widget.destroy()

            mensajes = self.obtener_lista_db(
                """
                SELECT id_mensaje, remitente, contenido, fecha_hora
                FROM mensajes
                ORDER BY id_mensaje ASC
                """
            )

            for id_mensaje, remitente, contenido, fecha_hora in mensajes:
                es_mio = remitente == self.usuario_actual

                fila = tk.Frame(chat_frame, bg="#f4f6f8")
                fila.pack(fill="x", pady=6, padx=8)

                color_burbuja = "#f39c12" if es_mio else "white"
                color_texto = "white" if es_mio else "#2c3e50"
                color_meta = "#fff3d9" if es_mio else "#7f8c8d"

                contenedor_burbuja = tk.Frame(
                    fila,
                    bg=color_burbuja,
                    padx=12,
                    pady=8,
                    highlightthickness=0
                )

                contenedor_burbuja.pack(
                    side="right" if es_mio else "left",
                    anchor="e" if es_mio else "w",
                    padx=(90, 0) if es_mio else (0, 90)
                )

                tk.Label(
                    contenedor_burbuja,
                    text=f"{remitente} - {fecha_hora}",
                    bg=color_burbuja,
                    fg=color_meta,
                    font=("Segoe UI", 8, "bold"),
                    anchor="w",
                    justify="left"
                ).pack(anchor="w")

                tk.Label(
                    contenedor_burbuja,
                    text=contenido,
                    bg=color_burbuja,
                    fg=color_texto,
                    font=("Segoe UI", 10),
                    wraplength=430,
                    justify="left",
                    anchor="w"
                ).pack(anchor="w", pady=(3, 0))

                def click_mensaje(event, id_sel=id_mensaje, texto_sel=contenido, frame_sel=contenedor_burbuja):
                    seleccionar_mensaje(id_sel, texto_sel, frame_sel)

                contenedor_burbuja.bind("<Button-1>", click_mensaje)

                for hijo in contenedor_burbuja.winfo_children():
                    hijo.bind("<Button-1>", click_mensaje)

            v.after(100, lambda: canvas.yview_moveto(1.0))

        def enviar():
            texto = obtener_texto_mensaje()

            if not texto:
                return

            self.ejecutar_db(
                """
                INSERT INTO mensajes
                (remitente, contenido, fecha_hora)
                VALUES (?, ?, ?)
                """,
                (self.usuario_actual, texto, datetime.now().strftime("%H:%M"))
            )

            msj.delete(0, tk.END)
            limpiar_seleccion()
            mostrar_placeholder()
            cargar()

        def editar_mensaje():
            if not seleccionado["id"]:
                messagebox.showwarning("Atencion", "Seleccione un mensaje para editar.")
                return

            texto = obtener_texto_mensaje()

            if not texto:
                messagebox.showwarning("Atencion", "El mensaje no puede quedar vacio.")
                return

            self.ejecutar_db(
                """
                UPDATE mensajes
                SET contenido=?, fecha_hora=?
                WHERE id_mensaje=?
                """,
                (texto, datetime.now().strftime("%H:%M"), seleccionado["id"])
            )

            msj.delete(0, tk.END)
            limpiar_seleccion()
            mostrar_placeholder()
            cargar()

        def eliminar_mensaje():
            if not seleccionado["id"]:
                messagebox.showwarning("Atencion", "Seleccione un mensaje para eliminar.")
                return

            confirmar = messagebox.askyesno(
                "Eliminar mensaje",
                "Desea eliminar el mensaje seleccionado?"
            )

            if not confirmar:
                return

            self.ejecutar_db(
                "DELETE FROM mensajes WHERE id_mensaje=?",
                (seleccionado["id"],)
            )

            msj.delete(0, tk.END)
            limpiar_seleccion()
            mostrar_placeholder()
            cargar()

        tk.Button(
            botones,
            text="Enviar",
            command=enviar,
            bg="#2ecc71",
            fg="white",
            font=("Segoe UI", 9, "bold"),
            bd=0,
            width=12,
            height=2,
            cursor="hand2"
        ).pack(side="left", padx=4)

        tk.Button(
            botones,
            text="Editar",
            command=editar_mensaje,
            bg="#3498db",
            fg="white",
            font=("Segoe UI", 9, "bold"),
            bd=0,
            width=12,
            height=2,
            cursor="hand2"
        ).pack(side="left", padx=4)

        tk.Button(
            botones,
            text="Eliminar",
            command=eliminar_mensaje,
            bg="#e74c3c",
            fg="white",
            font=("Segoe UI", 9, "bold"),
            bd=0,
            width=12,
            height=2,
            cursor="hand2"
        ).pack(side="left", padx=4)

        msj.bind("<Return>", lambda e: enviar())

        mostrar_placeholder()
        cargar()

    def ventana_pagos(self, id_pago_editar=None):
        vp = tk.Toplevel(self.root)
        vp.title("Registro de Pagos")
        vp.geometry("450x590")
        vp.configure(bg="#f4f7f6")

        datos_editar = None

        if id_pago_editar:
            datos = self.obtener_lista_db(
                """
                SELECT uuid_empresa, nombre_proyecto, monto, metodo_pago, fecha_pago
                FROM pagos
                WHERE id_pago=?
                """,
                (id_pago_editar,)
            )
            datos_editar = datos[0] if datos else None

        titulo = "EDITAR PAGO" if id_pago_editar else "REGISTRAR NUEVO PAGO"

        tk.Label(
            vp,
            text=titulo,
            font=("Segoe UI", 14, "bold"),
            bg="#f4f7f6",
            fg="#e67e22"
        ).pack(pady=20)

        f = tk.Frame(
            vp,
            bg="white",
            padx=30,
            pady=20,
            highlightthickness=1,
            highlightbackground="#dee2e6"
        )
        f.pack(fill="both", expand=True, padx=20, pady=10)

        tk.Label(f, text="ID Empresa (UUID):", bg="white").pack(anchor="w")

        ent_uuid = tk.Entry(f, font=("Consolas", 11), relief="solid")
        ent_uuid.pack(fill="x", pady=(0, 15))

        tk.Label(f, text="Proyecto Asociado:", bg="white").pack(anchor="w")

        cb_proy = ttk.Combobox(f, state="readonly")
        cb_proy.pack(fill="x", pady=(0, 15))

        def cargar_proyectos(event=None):
            res = self.obtener_lista_db(
                """
                SELECT p.nombre
                FROM proyectos p
                JOIN clientes c ON p.id_cliente = c.id_cliente
                WHERE c.uuid_empresa=?
                """,
                (ent_uuid.get().strip(),)
            )

            cb_proy["values"] = [p[0] for p in res]

            if res:
                cb_proy.current(0)

        ent_uuid.bind("<FocusOut>", cargar_proyectos)

        tk.Label(f, text="Monto (Q):", bg="white").pack(anchor="w")

        ent_monto = tk.Entry(f, relief="solid")
        ent_monto.pack(fill="x", pady=(0, 15))

        tk.Label(f, text="Tipo de Pago:", bg="white").pack(anchor="w")

        cb_tipo = ttk.Combobox(
            f,
            values=["Efectivo", "Tarjeta", "Transferencia"],
            state="readonly"
        )
        cb_tipo.current(0)
        cb_tipo.pack(fill="x", pady=(0, 15))

        fecha_real = datos_editar[4] if datos_editar else datetime.now().strftime("%d/%m/%Y %H:%M")

        tk.Label(f, text="Fecha de Pago:", bg="white").pack(anchor="w")

        tk.Label(
            f,
            text=fecha_real,
            font=("Consolas", 10),
            bg="#ecf0f1",
            relief="sunken",
            anchor="w"
        ).pack(fill="x", pady=(0, 20))

        if datos_editar:
            ent_uuid.insert(0, datos_editar[0])
            cargar_proyectos()
            cb_proy.set(datos_editar[1])
            ent_monto.insert(0, str(datos_editar[2]))
            cb_tipo.set(datos_editar[3])

        def editar_existente():
            seleccionado = self.seleccionar_registro(
                "Editar pago",
                ("ID", "UUID", "Proyecto", "Monto", "Metodo", "Fecha"),
                """
                SELECT id_pago, uuid_empresa, nombre_proyecto, monto, metodo_pago, fecha_pago
                FROM pagos
                ORDER BY id_pago DESC
                """
            )

            if seleccionado:
                vp.destroy()
                self.ventana_pagos(int(seleccionado[0]))

        def guardar_pago():
            if not cb_proy.get() or not ent_monto.get():
                messagebox.showwarning("Error", "Faltan datos")
                return

            try:
                monto = float(ent_monto.get())
            except ValueError:
                messagebox.showwarning("Error", "El monto debe ser numerico.")
                return

            if id_pago_editar:
                self.ejecutar_db(
                    """
                    UPDATE pagos
                    SET uuid_empresa=?, nombre_proyecto=?, monto=?, metodo_pago=?
                    WHERE id_pago=?
                    """,
                    (
                        ent_uuid.get().strip(),
                        cb_proy.get(),
                        monto,
                        cb_tipo.get(),
                        id_pago_editar
                    )
                )

                messagebox.showinfo("Exito", "Pago actualizado")
            else:
                self.ejecutar_db(
                    """
                    INSERT INTO pagos
                    (uuid_empresa, nombre_proyecto, monto, metodo_pago, fecha_pago)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        ent_uuid.get().strip(),
                        cb_proy.get(),
                        monto,
                        cb_tipo.get(),
                        fecha_real
                    )
                )

                messagebox.showinfo("Exito", "Pago guardado")

            vp.destroy()

        tk.Button(
            vp,
            text="GUARDAR CAMBIOS" if id_pago_editar else "CONFIRMAR PAGO",
            bg="#e67e22",
            fg="white",
            font=("Segoe UI", 10, "bold"),
            height=2,
            command=guardar_pago
        ).pack(pady=6)

        tk.Button(
            vp,
            text="Editar",
            bg="#3498db",
            fg="white",
            font=("Segoe UI", 10, "bold"),
            height=2,
            command=editar_existente
        ).pack(pady=6)

    def ventana_facturas(self):
        vf = tk.Toplevel(self.root)
        vf.title("Historial de Facturacion")
        vf.geometry("900x560")

        tk.Label(
            vf,
            text="PAGOS RECIBIDOS / FACTURAS",
            font=("Segoe UI", 14, "bold"),
            pady=20
        ).pack()

        barra = tk.Frame(vf)
        barra.pack(fill="x", padx=20)

        cols = ("ID", "Empresa (UUID)", "Proyecto", "Monto", "Metodo", "Fecha")
        tree = ttk.Treeview(vf, columns=cols, show="headings")

        for c in cols:
            tree.heading(c, text=c)
            tree.column(c, width=120, anchor="center")

        tree.pack(fill="both", expand=True, padx=20, pady=20)

        def cargar_datos():
            for item in tree.get_children():
                tree.delete(item)

            datos = self.obtener_lista_db(
                """
                SELECT id_pago, uuid_empresa, nombre_proyecto, monto, metodo_pago, fecha_pago
                FROM pagos
                ORDER BY id_pago DESC
                """
            )

            for d in datos:
                tree.insert("", "end", values=d)

        def obtener_pago_seleccionado():
            item = tree.selection()

            if not item:
                messagebox.showwarning("Atencion", "Seleccione una factura.")
                return None

            return tree.item(item, "values")

        def texto_factura(pago):
            id_pago, uuid_emp, proyecto, monto, metodo, fecha = pago

            empresa = self.obtener_lista_db(
                """
                SELECT nombre_empresa
                FROM clientes
                WHERE uuid_empresa=?
                """,
                (uuid_emp,)
            )

            nombre_empresa = empresa[0][0] if empresa else uuid_emp

            return (
                "ESPACIO CREATIVO\n"
                "FACTURA / COMPROBANTE DE PAGO\n"
                "================================\n"
                f"No. Factura: FAC-{int(id_pago):05d}\n"
                f"Empresa: {nombre_empresa}\n"
                f"UUID: {uuid_emp}\n"
                f"Proyecto: {proyecto}\n"
                f"Monto: Q {float(monto):.2f}\n"
                f"Metodo de pago: {metodo}\n"
                f"Fecha: {fecha}\n"
                "================================\n"
                "Gracias por confiar en Espacio Creativo.\n"
            )

        def guardar_factura():
            pago = obtener_pago_seleccionado()

            if not pago:
                return

            ruta = filedialog.asksaveasfilename(
                title="Guardar factura",
                defaultextension=".txt",
                initialfile=f"factura_FAC-{int(pago[0]):05d}.txt",
                filetypes=[("Archivo de texto", "*.txt")]
            )

            if not ruta:
                return

            with open(ruta, "w", encoding="utf-8") as archivo:
                archivo.write(texto_factura(pago))

            messagebox.showinfo("Exito", f"Factura guardada en:\n{ruta}")

        def imprimir_factura():
            pago = obtener_pago_seleccionado()

            if not pago:
                return

            ruta_temp = os.path.join(
                os.path.dirname(self.ruta_db),
                f"factura_FAC-{int(pago[0]):05d}.txt"
            )

            with open(ruta_temp, "w", encoding="utf-8") as archivo:
                archivo.write(texto_factura(pago))

            try:
                os.startfile(ruta_temp, "print")
                messagebox.showinfo("Impresion", "Factura enviada a imprimir.")
            except Exception as e:
                messagebox.showerror(
                    "Error",
                    f"No se pudo imprimir automaticamente:\n{e}\n\nArchivo generado:\n{ruta_temp}"
                )

        tk.Button(
            barra,
            text="Guardar Factura",
            command=guardar_factura,
            bg="#2ecc71",
            fg="white",
            width=18
        ).pack(side="left", padx=5)

        tk.Button(
            barra,
            text="Imprimir Factura",
            command=imprimir_factura,
            bg="#8e44ad",
            fg="white",
            width=18
        ).pack(side="left", padx=5)

        tk.Button(
            barra,
            text="Actualizar",
            command=cargar_datos,
            bg="#3498db",
            fg="white",
            width=18
        ).pack(side="left", padx=5)

        cargar_datos()

    def ventana_reportes_financieros(self):
        v = tk.Toplevel(self.root)
        v.title("Reportes financieros")
        v.geometry("1180x820")
        v.configure(bg="#f4f7f6")

        tk.Label(
            v,
            text="REPORTES FINANCIEROS",
            bg="#f4f7f6",
            fg="#16a085",
            font=("Segoe UI", 17, "bold")
        ).pack(pady=(16, 8))

        resumen = tk.Frame(v, bg="#f4f7f6")
        resumen.pack(fill="x", padx=20, pady=(4, 10))

        lbl_ingresos = self.crear_tarjeta_resumen(resumen, "Ingresos", "#2ecc71")
        lbl_egresos = self.crear_tarjeta_resumen(resumen, "Egresos", "#e74c3c")
        lbl_margen = self.crear_tarjeta_resumen(resumen, "Margen", "#3498db")
        lbl_estado = self.crear_tarjeta_resumen(resumen, "Resultado", "#8e44ad")

        cuerpo = tk.Frame(v, bg="#f4f7f6")
        cuerpo.pack(fill="both", expand=True, padx=20, pady=(0, 10))

        panel_egresos = tk.Frame(
            cuerpo,
            bg="white",
            width=190,
            padx=18,
            pady=16,
            highlightthickness=1,
            highlightbackground="#dfe6e9"
        )
        panel_egresos.pack(side="left", fill="y", padx=(0, 14))
        panel_egresos.pack_propagate(False)

        tk.Label(
            panel_egresos,
            text="Registrar egreso",
            bg="white",
            fg="#2c3e50",
            font=("Segoe UI", 12, "bold")
        ).pack(anchor="w", pady=(0, 12))

        ent_concepto = self.crear_campo(panel_egresos, "Concepto")

        tk.Label(panel_egresos, text="Categoria", bg="white").pack(anchor="w")
        cb_categoria = ttk.Combobox(
            panel_egresos,
            values=["Compra", "Materiales", "Impresion", "Transporte", "Servicios", "Otro"],
            state="readonly"
        )
        cb_categoria.current(0)
        cb_categoria.pack(fill="x", pady=(4, 12), ipady=3)

        ent_monto = self.crear_campo(panel_egresos, "Monto Q")
        ent_nota = self.crear_campo(panel_egresos, "Nota")

        panel_derecho = tk.Frame(cuerpo, bg="#f4f7f6")
        panel_derecho.pack(side="right", fill="both", expand=True)

        scroll_panel = ttk.Scrollbar(panel_derecho, orient="vertical")
        scroll_panel.pack(side="right", fill="y")

        canvas_panel = tk.Canvas(
            panel_derecho,
            bg="#f4f7f6",
            highlightthickness=0,
            yscrollcommand=scroll_panel.set
        )
        canvas_panel.pack(side="left", fill="both", expand=True)

        scroll_panel.config(command=canvas_panel.yview)

        contenido_panel = tk.Frame(canvas_panel, bg="#f4f7f6")
        ventana_panel = canvas_panel.create_window(
            (0, 0),
            window=contenido_panel,
            anchor="nw"
        )

        def ajustar_scroll_panel(event=None):
            canvas_panel.configure(scrollregion=canvas_panel.bbox("all"))

        def ajustar_ancho_panel(event):
            canvas_panel.itemconfigure(ventana_panel, width=event.width)

        contenido_panel.bind("<Configure>", ajustar_scroll_panel)
        canvas_panel.bind("<Configure>", ajustar_ancho_panel)

        grafica = tk.Canvas(
            contenido_panel,
            bg="white",
            height=390,
            highlightthickness=1,
            highlightbackground="#dfe6e9"
        )
        grafica.pack(fill="x", expand=False)

        tabla_panel = tk.Frame(
            contenido_panel,
            bg="white",
            padx=10,
            pady=10,
            highlightthickness=1,
            highlightbackground="#dfe6e9"
        )
        tabla_panel.pack(fill="x", pady=(12, 0))

        def mover_scroll_mouse(event):
            canvas_panel.yview_scroll(int(-1 * (event.delta / 120)), "units")

        canvas_panel.bind_all("<MouseWheel>", mover_scroll_mouse)

        tk.Label(
            tabla_panel,
            text="Detalle de movimientos",
            bg="white",
            fg="#2c3e50",
            font=("Segoe UI", 11, "bold")
        ).pack(anchor="w", pady=(0, 8))

        tabla_contenedor = tk.Frame(tabla_panel, bg="white", height=170)
        tabla_contenedor.pack(fill="x")
        tabla_contenedor.pack_propagate(False)

        cols = ("Tipo", "Detalle", "Monto", "Fecha")

        tree_scroll_y = ttk.Scrollbar(tabla_contenedor, orient="vertical")
        tree_scroll_x = ttk.Scrollbar(tabla_contenedor, orient="horizontal")

        tree = ttk.Treeview(
            tabla_contenedor,
            columns=cols,
            show="headings",
            height=6,
            yscrollcommand=tree_scroll_y.set,
            xscrollcommand=tree_scroll_x.set
        )

        tree_scroll_y.config(command=tree.yview)
        tree_scroll_x.config(command=tree.xview)

        tree.heading("Tipo", text="Tipo")
        tree.heading("Detalle", text="Detalle")
        tree.heading("Monto", text="Monto")
        tree.heading("Fecha", text="Fecha")

        tree.column("Tipo", width=120, anchor="center", stretch=False)
        tree.column("Detalle", width=520, anchor="w", stretch=False)
        tree.column("Monto", width=160, anchor="center", stretch=False)
        tree.column("Fecha", width=210, anchor="center", stretch=False)

        tree.grid(row=0, column=0, sticky="nsew")
        tree_scroll_y.grid(row=0, column=1, sticky="ns")
        tree_scroll_x.grid(row=1, column=0, sticky="ew")

        tabla_contenedor.grid_rowconfigure(0, weight=1)
        tabla_contenedor.grid_columnconfigure(0, weight=1)

        totales = {"ingresos": 0.0, "egresos": 0.0, "margen": 0.0}

        def leer_datos():
            ingresos = self.obtener_lista_db(
                """
                SELECT 'Ingreso', nombre_proyecto, monto, fecha_pago
                FROM pagos
                ORDER BY fecha_pago DESC
                """
            )

            egresos = self.obtener_lista_db(
                """
                SELECT 'Egreso', concepto || ' - ' || COALESCE(categoria, ''), monto, fecha
                FROM egresos
                ORDER BY id_egreso DESC
                """
            )

            return ingresos, egresos

        def actualizar():
            for item in tree.get_children():
                tree.delete(item)

            ingresos, egresos = leer_datos()
            total_ingresos = sum(float(r[2] or 0) for r in ingresos)
            total_egresos = sum(float(r[2] or 0) for r in egresos)
            margen = total_ingresos - total_egresos

            totales["ingresos"] = total_ingresos
            totales["egresos"] = total_egresos
            totales["margen"] = margen

            lbl_ingresos.config(text=f"Q {total_ingresos:,.2f}")
            lbl_egresos.config(text=f"Q {total_egresos:,.2f}")
            lbl_margen.config(text=f"Q {margen:,.2f}")
            lbl_estado.config(text="Ganancia" if margen >= 0 else "Perdida")

            for fila in ingresos + egresos:
                tree.insert(
                    "",
                    "end",
                    values=(fila[0], fila[1], f"Q {float(fila[2]):,.2f}", fila[3])
                )

            dibujar_grafica()

        def dibujar_grafica():
            grafica.delete("all")
            grafica.update_idletasks()

            w = max(grafica.winfo_width(), 500)
            h = max(grafica.winfo_height(), 320)

            grafica.create_text(
                w / 2,
                32,
                text="Ingresos vs egresos",
                font=("Segoe UI", 15, "bold"),
                fill="#2c3e50"
            )

            maximo = max(totales["ingresos"], totales["egresos"], 1)
            base_y = h - 80
            alto_max = h - 150

            barras = [
                ("Ingresos", totales["ingresos"], "#2ecc71", w * 0.35),
                ("Egresos", totales["egresos"], "#e74c3c", w * 0.65)
            ]

            for nombre, valor, color, x in barras:
                alto = (valor / maximo) * alto_max
                grafica.create_rectangle(
                    x - 55,
                    base_y - alto,
                    x + 55,
                    base_y,
                    fill=color,
                    outline=""
                )
                grafica.create_text(
                    x,
                    base_y + 24,
                    text=nombre,
                    font=("Segoe UI", 10, "bold"),
                    fill="#2c3e50"
                )
                grafica.create_text(
                    x,
                    base_y - alto - 18,
                    text=f"Q {valor:,.2f}",
                    font=("Segoe UI", 10),
                    fill="#2c3e50"
                )

            color_margen = "#2ecc71" if totales["margen"] >= 0 else "#e74c3c"

            grafica.create_text(
                w / 2,
                h - 25,
                text=f"Margen: Q {totales['margen']:,.2f}",
                font=("Segoe UI", 13, "bold"),
                fill=color_margen
            )

        def guardar_egreso():
            concepto = ent_concepto.get().strip()
            categoria = cb_categoria.get()
            nota = ent_nota.get().strip()

            try:
                monto = float(ent_monto.get())
            except ValueError:
                messagebox.showwarning("Error", "El monto debe ser numerico.")
                return

            if not concepto or monto <= 0:
                messagebox.showwarning("Error", "Ingrese concepto y monto valido.")
                return

            self.ejecutar_db(
                """
                INSERT INTO egresos (concepto, categoria, monto, fecha, nota)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    concepto,
                    categoria,
                    monto,
                    datetime.now().strftime("%d/%m/%Y %H:%M"),
                    nota
                )
            )

            ent_concepto.delete(0, tk.END)
            ent_monto.delete(0, tk.END)
            ent_nota.delete(0, tk.END)
            actualizar()

        def texto_reporte():
            ingresos, egresos = leer_datos()

            lineas = [
                "ESPACIO CREATIVO",
                "REPORTE FINANCIERO",
                "================================",
                f"Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}",
                f"Ingresos: Q {totales['ingresos']:,.2f}",
                f"Egresos: Q {totales['egresos']:,.2f}",
                f"Margen: Q {totales['margen']:,.2f}",
                f"Resultado: {'Ganancia' if totales['margen'] >= 0 else 'Perdida'}",
                "================================",
                "",
                "INGRESOS"
            ]

            lineas.extend(
                f"- {d[1]} | Q {float(d[2]):,.2f} | {d[3]}"
                for d in ingresos
            )

            lineas.append("")
            lineas.append("EGRESOS")

            lineas.extend(
                f"- {d[1]} | Q {float(d[2]):,.2f} | {d[3]}"
                for d in egresos
            )

            return "\n".join(lineas) + "\n"

        def guardar_reporte():
            ruta = filedialog.asksaveasfilename(
                title="Guardar reporte",
                defaultextension=".txt",
                initialfile="reporte_financiero.txt",
                filetypes=[("Archivo de texto", "*.txt")]
            )

            if not ruta:
                return

            with open(ruta, "w", encoding="utf-8") as archivo:
                archivo.write(texto_reporte())

            messagebox.showinfo("Exito", f"Reporte guardado en:\n{ruta}")

        def imprimir_reporte():
            ruta_temp = os.path.join(
                os.path.dirname(self.ruta_db),
                "reporte_financiero.txt"
            )

            with open(ruta_temp, "w", encoding="utf-8") as archivo:
                archivo.write(texto_reporte())

            try:
                os.startfile(ruta_temp, "print")
                messagebox.showinfo("Impresion", "Reporte enviado a imprimir.")
            except Exception as e:
                messagebox.showerror(
                    "Error",
                    f"No se pudo imprimir:\n{e}\n\nArchivo:\n{ruta_temp}"
                )

        tk.Button(
            panel_egresos,
            text="Guardar egreso",
            command=guardar_egreso,
            bg="#e74c3c",
            fg="white",
            bd=0,
            height=2,
            cursor="hand2"
        ).pack(fill="x", pady=(4, 10))

        tk.Button(
            panel_egresos,
            text="Guardar reporte",
            command=guardar_reporte,
            bg="#2ecc71",
            fg="white",
            bd=0,
            height=2,
            cursor="hand2"
        ).pack(fill="x", pady=5)

        tk.Button(
            panel_egresos,
            text="Imprimir reporte",
            command=imprimir_reporte,
            bg="#8e44ad",
            fg="white",
            bd=0,
            height=2,
            cursor="hand2"
        ).pack(fill="x", pady=5)

        grafica.bind("<Configure>", lambda e: dibujar_grafica())
        actualizar()



    def crear_tarjeta_resumen(self, padre, titulo, color):
        card = tk.Frame(
            padre,
            bg="white",
            padx=18,
            pady=12,
            highlightthickness=1,
            highlightbackground="#dfe6e9"
        )
        card.pack(side="left", expand=True, fill="x", padx=6)

        tk.Label(
            card,
            text=titulo,
            bg="white",
            fg=color,
            font=("Segoe UI", 10, "bold")
        ).pack(anchor="w")

        valor = tk.Label(
            card,
            text="Q 0.00",
            bg="white",
            fg="#2c3e50",
            font=("Segoe UI", 16, "bold")
        )
        valor.pack(anchor="w", pady=(4, 0))
        return valor

    def crear_campo(self, padre, etiqueta):
        tk.Label(padre, text=etiqueta, bg="white").pack(anchor="w")
        entrada = tk.Entry(padre, relief="solid", bd=1)
        entrada.pack(fill="x", pady=(4, 12), ipady=4)
        return entrada

    def crear_respaldo_automatico(self):
        carpeta = os.path.join(os.path.dirname(self.ruta_db), "respaldos")
        os.makedirs(carpeta, exist_ok=True)

        hoy = datetime.now().strftime("%Y-%m-%d")
        ruta = os.path.join(carpeta, f"respaldo_auto_{hoy}.zip")

        if os.path.exists(ruta):
            return ruta

        self.crear_archivo_respaldo(ruta)
        return ruta

    def crear_archivo_respaldo(self, ruta_zip):
        base = os.path.dirname(self.ruta_db)

        manifest = [
            "ESPACIO CREATIVO - RESPALDO",
            f"Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}",
            "",
            "Contenido:",
            "- Base de datos gestion_proyectos.db",
            "- Archivos .py del programa",
            "- Logo si existe",
            "- Imagenes vinculadas a publicidad",
            "",
            "Para una computadora nueva, copie tambien los archivos del programa",
            "o use la opcion Restaurar respaldo desde el sistema."
        ]

        with zipfile.ZipFile(ruta_zip, "w", zipfile.ZIP_DEFLATED) as zipf:
            if os.path.exists(self.ruta_db):
                zipf.write(self.ruta_db, "gestion_proyectos.db")

            for nombre in os.listdir(base):
                ruta = os.path.join(base, nombre)

                if os.path.isfile(ruta) and nombre.lower().endswith(".py"):
                    zipf.write(ruta, f"programa/{nombre}")

            if self.ruta_logo and os.path.exists(self.ruta_logo):
                zipf.write(
                    self.ruta_logo,
                    f"assets/{os.path.basename(self.ruta_logo)}"
                )

            imagenes = self.obtener_lista_db(
                """
                SELECT DISTINCT nombre_archivo
                FROM publicidad
                WHERE nombre_archivo IS NOT NULL AND nombre_archivo <> ''
                """
            )

            nombres_usados = set()

            for (ruta_img,) in imagenes:
                if not ruta_img or not os.path.exists(ruta_img):
                    continue

                nombre = os.path.basename(ruta_img)
                nombre_zip = nombre
                contador = 2

                while nombre_zip.lower() in nombres_usados:
                    raiz, ext = os.path.splitext(nombre)
                    nombre_zip = f"{raiz}_{contador}{ext}"
                    contador += 1

                nombres_usados.add(nombre_zip.lower())
                zipf.write(ruta_img, f"publicidad/{nombre_zip}")

            zipf.writestr("LEEME_RESPALDO.txt", "\n".join(manifest))

        return ruta_zip

    def ventana_respaldos(self):
        v = tk.Toplevel(self.root)
        v.title("Seguridad y respaldos")
        v.geometry("720x520")
        v.configure(bg="#f4f7f6")

        tk.Label(
            v,
            text="SEGURIDAD Y RESPALDOS",
            bg="#f4f7f6",
            fg="#34495e",
            font=("Segoe UI", 17, "bold")
        ).pack(pady=(24, 8))

        info = tk.Frame(
            v,
            bg="white",
            padx=22,
            pady=18,
            highlightthickness=1,
            highlightbackground="#dfe6e9"
        )
        info.pack(fill="x", padx=28, pady=12)

        tk.Label(
            info,
            text=(
                "Un respaldo guarda la base de datos, el programa y las imagenes de publicidad en un archivo ZIP.\n"
                "Conviene copiar ese ZIP a una USB, Google Drive, OneDrive o correo para protegerse si cambia la computadora."
            ),
            bg="white",
            fg="#2c3e50",
            justify="left",
            wraplength=640,
            font=("Segoe UI", 10)
        ).pack(anchor="w")

        carpeta_auto = os.path.join(os.path.dirname(self.ruta_db), "respaldos")

        tk.Label(
            info,
            text=f"Carpeta de respaldos automaticos:\n{carpeta_auto}",
            bg="white",
            fg="#7f8c8d",
            justify="left",
            wraplength=640,
            font=("Consolas", 9)
        ).pack(anchor="w", pady=(14, 0))

        acciones = tk.Frame(v, bg="#f4f7f6")
        acciones.pack(fill="x", padx=28, pady=10)

        def respaldo_manual():
            ruta = filedialog.asksaveasfilename(
                title="Guardar respaldo",
                defaultextension=".zip",
                initialfile=f"respaldo_espacio_creativo_{datetime.now().strftime('%Y%m%d_%H%M')}.zip",
                filetypes=[("Respaldo ZIP", "*.zip")]
            )

            if not ruta:
                return

            try:
                self.crear_archivo_respaldo(ruta)
                messagebox.showinfo("Exito", f"Respaldo guardado en:\n{ruta}")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo crear el respaldo:\n{e}")

        def abrir_carpeta_respaldos():
            os.makedirs(carpeta_auto, exist_ok=True)

            try:
                os.startfile(carpeta_auto)
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo abrir la carpeta:\n{e}")

        def restaurar_respaldo():
            ruta = filedialog.askopenfilename(
                title="Seleccionar respaldo",
                filetypes=[("Respaldo ZIP", "*.zip")]
            )

            if not ruta:
                return

            confirmar = messagebox.askyesno(
                "Restaurar respaldo",
                "Esto reemplazara la base de datos actual por la del respaldo seleccionado.\n\n"
                "Antes de continuar se creara un respaldo de seguridad del estado actual.\n\n"
                "Desea continuar?"
            )

            if not confirmar:
                return

            try:
                self.crear_respaldo_automatico()
                self.restaurar_archivo_respaldo(ruta)
                messagebox.showinfo(
                    "Restauracion completa",
                    "Los datos fueron restaurados. Cierre y abra de nuevo el programa para cargar todo correctamente."
                )
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo restaurar el respaldo:\n{e}")

        botones = [
            ("Crear respaldo ahora", "#2ecc71", respaldo_manual),
            ("Restaurar respaldo", "#e67e22", restaurar_respaldo),
            ("Abrir carpeta de respaldos", "#3498db", abrir_carpeta_respaldos)
        ]

        for texto, color, comando in botones:
            tk.Button(
                acciones,
                text=texto,
                command=comando,
                bg=color,
                fg="white",
                activebackground=color,
                activeforeground="white",
                font=("Segoe UI", 11, "bold"),
                bd=0,
                height=2,
                cursor="hand2"
            ).pack(fill="x", pady=7)

        tk.Label(
            v,
            text="Consejo: haga un respaldo manual al terminar cada dia de trabajo importante.",
            bg="#f4f7f6",
            fg="#7f8c8d",
            font=("Segoe UI", 9, "italic")
        ).pack(pady=8)

    def restaurar_archivo_respaldo(self, ruta_zip):
        base = os.path.dirname(self.ruta_db)
        carpeta_publicidad = os.path.join(base, "publicidad_restaurada")
        os.makedirs(carpeta_publicidad, exist_ok=True)

        with zipfile.ZipFile(ruta_zip, "r") as zipf:
            nombres = zipf.namelist()

            if "gestion_proyectos.db" not in nombres:
                raise ValueError("El respaldo no contiene gestion_proyectos.db.")

            respaldo_actual = os.path.join(
                base,
                f"gestion_proyectos_antes_restaurar_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
            )

            if os.path.exists(self.ruta_db):
                shutil.copy2(self.ruta_db, respaldo_actual)

            zipf.extract("gestion_proyectos.db", base)

            for nombre in nombres:
                if nombre.startswith("publicidad/") and not nombre.endswith("/"):
                    destino = os.path.join(
                        carpeta_publicidad,
                        os.path.basename(nombre)
                    )

                    with zipf.open(nombre) as origen, open(destino, "wb") as salida:
                        shutil.copyfileobj(origen, salida)

        self.reparar_rutas_publicidad_restaurada(carpeta_publicidad)

    def reparar_rutas_publicidad_restaurada(self, carpeta_publicidad):
        if not os.path.isdir(carpeta_publicidad):
            return

        archivos = {
            nombre.lower(): os.path.join(carpeta_publicidad, nombre)
            for nombre in os.listdir(carpeta_publicidad)
        }

        registros = self.obtener_lista_db(
            """
            SELECT id_pub, nombre_archivo
            FROM publicidad
            WHERE nombre_archivo IS NOT NULL AND nombre_archivo <> ''
            """
        )

        for id_pub, ruta_anterior in registros:
            nombre = os.path.basename(ruta_anterior or "").lower()
            nueva_ruta = archivos.get(nombre)

            if nueva_ruta:
                self.ejecutar_db(
                    "UPDATE publicidad SET nombre_archivo=? WHERE id_pub=?",
                    (nueva_ruta, id_pub)
                )


if __name__ == "__main__":
    root = tk.Tk()
    app = SistemaGestion(root)
    root.mainloop()