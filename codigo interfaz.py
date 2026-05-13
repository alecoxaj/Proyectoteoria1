import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
import os
import uuid
from datetime import datetime
from tkcalendar import DateEntry
from PIL import Image, ImageTk, ImageOps


class SistemaGestion:
    def __init__(self, root):
        self.root = root
        self.root.title("Espacio Creativo v3.0 - Gestión Pro")
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
            "Soporte Técnico",
            "ESPACIO CREATIVO\n\n"
            "Correo: soporte@espaciocreativo.com\n"
            "Tel: +502 5555-5555"
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
                text="›",
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
                messagebox.showwarning("Atención", "Seleccione un registro.")
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
                messagebox.showwarning("Atención", "Seleccione un usuario.")
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
        ).place(relx=0.58, rely=0.5, anchor="center")

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

        tk.Label(f, text="🏢  Nombre de la Empresa:", bg="white").pack(anchor="w")
        nom_e = tk.Entry(f, relief="solid", bd=1)
        nom_e.pack(fill="x", pady=(5, 15))

        tk.Label(f, text="📞  Número Telefónico Referido:", bg="white").pack(anchor="w")
        tel_e = tk.Entry(f, relief="solid", bd=1)
        tel_e.pack(fill="x", pady=(5, 15))

        tk.Label(f, text="✉️  Correo Electrónico:", bg="white").pack(anchor="w")
        cor_e = tk.Entry(f, relief="solid", bd=1)
        cor_e.pack(fill="x", pady=(5, 15))

        tk.Label(f, text="📍  Dirección de la Empresa:", bg="white").pack(anchor="w")
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
                    "Atención",
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
                    f"La empresa '{nombre}' ya está registrada."
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
                        "Éxito",
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
                        "Éxito",
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
                        "Éxito",
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
                        "Éxito",
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
            text="🆔 BUSCAR POR ID:",
            fg="white",
            bg="#34495e",
            font=("Segoe UI", 9, "bold")
        ).pack(side="left", padx=(20, 5))

        ent_id_busq = tk.Entry(frame_busqueda, font=("Consolas", 11), width=15)
        ent_id_busq.pack(side="left", padx=10)

        tk.Label(
            frame_busqueda,
            text="📂 NOMBRE PROYECTO:",
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
            text="▼ REGISTROS DE PROYECTOS ▼",
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
            text="🆔 DIRECTORIO DE IDENTIFICADORES",
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
        v.title("Editor de Publicidad")
        v.geometry("1000x790")
        v.configure(bg="#2c3e50")

        self.img_original = None
        self.img_tk = None
        self.path_actual = ""

        panel_datos = tk.Frame(v, bg="white", pady=10)
        panel_datos.pack(fill="x")

        tk.Label(
            panel_datos,
            text="ID Empresa (UUID):",
            bg="white"
        ).pack(side="left", padx=5)

        ent_uuid = tk.Entry(
            panel_datos,
            font=("Consolas", 11),
            relief="solid",
            width=15
        )
        ent_uuid.pack(side="left", padx=5)

        tk.Label(panel_datos, text="Proyecto:", bg="white").pack(side="left", padx=5)

        cb_proyectos = ttk.Combobox(panel_datos, state="readonly", width=20)
        cb_proyectos.pack(side="left", padx=5)

        tk.Label(panel_datos, text="Estado:", bg="white").pack(side="left", padx=5)

        cb_estado = ttk.Combobox(
            panel_datos,
            values=["Trabajando", "En Espera", "Finalizado"],
            state="readonly",
            width=12
        )
        cb_estado.current(1)
        cb_estado.pack(side="left", padx=5)

        canvas = tk.Canvas(v, bg="#ecf0f1", width=600, height=450)
        canvas.pack(pady=20)

        def cargar_proyectos_de_empresa(event=None):
            uuid_busqueda = ent_uuid.get().strip()

            proys = self.obtener_lista_db(
                """
                SELECT p.nombre
                FROM proyectos p
                JOIN clientes c ON p.id_cliente = c.id_cliente
                WHERE c.uuid_empresa=?
                """,
                (uuid_busqueda,)
            )

            lista = [p[0] for p in proys]
            cb_proyectos["values"] = lista

            if lista:
                cb_proyectos.current(0)
            else:
                cb_proyectos.set("Sin proyectos")

        def actualizar_preview():
            canvas.delete("all")

            if self.img_original:
                img_copy = self.img_original.copy()
                img_copy.thumbnail((600, 450))
                self.img_tk = ImageTk.PhotoImage(img_copy)
                canvas.create_image(300, 225, image=self.img_tk)
            else:
                canvas.create_text(
                    300,
                    225,
                    text="Sin imagen cargada",
                    fill="#7f8c8d"
                )

        ent_uuid.bind("<FocusOut>", cargar_proyectos_de_empresa)

        if id_editar:
            ent_uuid.insert(0, id_editar)
            cargar_proyectos_de_empresa()

        if id_pub_editar:
            datos = self.obtener_lista_db(
                """
                SELECT uuid_empresa, nombre_archivo, estado, proyecto
                FROM publicidad
                WHERE id_pub=?
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
                    self.img_original = Image.open(archivo)

        actualizar_preview()

        def cargar_foto():
            path = filedialog.askopenfilename(
                filetypes=[("Imágenes", "*.jpg *.png *.jpeg")]
            )

            if path:
                self.img_original = Image.open(path)
                self.path_actual = path
                actualizar_preview()

        def efectos(tipo):
            if not self.img_original:
                return

            if tipo == "crop":
                w, h = self.img_original.size
                self.img_original = self.img_original.crop(
                    (w * 0.1, h * 0.1, w * 0.9, h * 0.9)
                )
            elif tipo == "gray":
                self.img_original = ImageOps.grayscale(self.img_original)

            actualizar_preview()

        def editar_existente():
            seleccionado = self.seleccionar_registro(
                "Editar publicidad",
                ("ID", "UUID", "Proyecto", "Estado", "Fecha"),
                """
                SELECT id_pub, uuid_empresa, COALESCE(proyecto, ''), estado, fecha
                FROM publicidad
                ORDER BY id_pub DESC
                """
            )

            if seleccionado:
                v.destroy()
                self.ventana_publicidad_editor(id_pub_editar=int(seleccionado[0]))

        def guardar_db():
            id_emp = ent_uuid.get().strip()
            proy_sel = cb_proyectos.get()

            if not id_emp or not self.img_original or proy_sel == "Sin proyectos":
                messagebox.showwarning(
                    "Atención",
                    "ID, Proyecto y foto requeridos."
                )
                return

            if id_pub_editar:
                self.ejecutar_db(
                    """
                    UPDATE publicidad
                    SET uuid_empresa=?, nombre_archivo=?, estado=?, fecha=?, proyecto=?
                    WHERE id_pub=?
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

                messagebox.showinfo(
                    "Éxito",
                    f"Publicidad actualizada para el proyecto: {proy_sel}"
                )
            else:
                self.ejecutar_db(
                    """
                    INSERT INTO publicidad
                    (uuid_empresa, nombre_archivo, estado, fecha, proyecto)
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
                    f"Publicidad guardada para el proyecto: {proy_sel}"
                )

            v.destroy()

        btns_f = tk.Frame(v, bg="#2c3e50")
        btns_f.pack(pady=10)

        tk.Button(
            btns_f,
            text="📂 SUBIR",
            command=cargar_foto,
            bg="#1abc9c",
            fg="white",
            width=12
        ).pack(side="left", padx=5)

        tk.Button(
            btns_f,
            text="✂️ RECORTAR",
            command=lambda: efectos("crop"),
            bg="#f39c12",
            fg="white",
            width=12
        ).pack(side="left", padx=5)

        tk.Button(
            btns_f,
            text="🌓 GRIS",
            command=lambda: efectos("gray"),
            bg="#95a5a6",
            fg="white",
            width=12
        ).pack(side="left", padx=5)

        tk.Button(
            btns_f,
            text="EDITAR",
            command=editar_existente,
            bg="#8e44ad",
            fg="white",
            width=12
        ).pack(side="left", padx=5)

        tk.Button(
            v,
            text="💾 GUARDAR CAMBIOS" if id_pub_editar else "💾 GUARDAR",
            command=guardar_db,
            bg="#3498db",
            fg="white",
            height=2,
            width=22
        ).pack(pady=20)

    def ventana_continuar_proyecto(self):
        v = tk.Toplevel(self.root)
        v.title("Panel de Continuidad de Trabajo")
        v.geometry("950x650")
        v.configure(bg="#f8f9fa")

        header_f = tk.Frame(v, bg="#2c3e50", pady=15)
        header_f.pack(fill="x")

        tk.Label(
            header_f,
            text="🚀 GESTIÓN DE TRABAJOS PENDIENTES",
            fg="white",
            bg="#2c3e50",
            font=("Segoe UI", 12, "bold")
        ).pack()

        search_f = tk.Frame(v, bg="#f8f9fa", pady=20)
        search_f.pack(fill="x")

        tk.Label(
            search_f,
            text="🔍 Ingrese ID de Empresa o Proyecto:",
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
                        f"Redirigiendo al módulo de Proyectos para: {nombre}"
                    )

        ent_id.bind("<KeyRelease>", buscar)
        tree.bind("<Double-1>", ejecutar_accion)

        tk.Label(
            v,
            text="💡 Tip: Doble clic sobre un registro para continuar editando o ver resultado.",
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

        seleccionado = {
            "id": None,
            "texto": "",
            "frame": None
        }

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
            text=f"Sesión: {self.usuario_actual}",
            bg="#f39c12",
            fg="white",
            font=("Segoe UI", 10)
        ).pack(side="right", padx=24)

        cuerpo = tk.Frame(v, bg="#f4f6f8")
        cuerpo.pack(fill="both", expand=True, padx=18, pady=(18, 10))

        canvas = tk.Canvas(
            cuerpo,
            bg="#f4f6f8",
            highlightthickness=0
        )

        scroll = ttk.Scrollbar(
            cuerpo,
            orient="vertical",
            command=canvas.yview
        )

        chat_frame = tk.Frame(canvas, bg="#f4f6f8")

        canvas_window = canvas.create_window(
            (0, 0),
            window=chat_frame,
            anchor="nw"
        )

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

        msj = tk.Entry(
            panel_envio,
            font=("Segoe UI", 11),
            relief="solid",
            bd=1
        )
        msj.pack(side="left", fill="x", expand=True, ipady=9, padx=(0, 12))

        botones = tk.Frame(panel_envio, bg="#ffffff")
        botones.pack(side="right")

        def limpiar_seleccion():
            if seleccionado["frame"] and seleccionado["frame"].winfo_exists():
                seleccionado["frame"].configure(
                    highlightthickness=0,
                    highlightbackground="#ffffff"
                )

            seleccionado["id"] = None
            seleccionado["texto"] = ""
            seleccionado["frame"] = None

        def seleccionar_mensaje(id_mensaje, texto, frame_burbuja):
            if seleccionado["frame"] and seleccionado["frame"].winfo_exists():
                seleccionado["frame"].configure(
                    highlightthickness=0,
                    highlightbackground="#ffffff"
                )

            seleccionado["id"] = id_mensaje
            seleccionado["texto"] = texto
            seleccionado["frame"] = frame_burbuja

            frame_burbuja.configure(
                highlightthickness=2,
                highlightbackground="#2980b9"
            )

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
                    highlightthickness=0,
                    highlightbackground="#ffffff"
                )

                contenedor_burbuja.pack(
                    side="right" if es_mio else "left",
                    anchor="e" if es_mio else "w",
                    padx=(90, 0) if es_mio else (0, 90)
                )

                tk.Label(
                    contenedor_burbuja,
                    text=f"{remitente} · {fecha_hora}",
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

                def click_mensaje(
                    event,
                    id_sel=id_mensaje,
                    texto_sel=contenido,
                    frame_sel=contenedor_burbuja
                ):
                    seleccionar_mensaje(id_sel, texto_sel, frame_sel)

                contenedor_burbuja.bind("<Button-1>", click_mensaje)

                for hijo in contenedor_burbuja.winfo_children():
                    hijo.bind("<Button-1>", click_mensaje)

            v.after(100, lambda: canvas.yview_moveto(1.0))

        def enviar():
            texto = msj.get().strip()

            if not texto:
                return

            self.ejecutar_db(
                """
                INSERT INTO mensajes
                (remitente, contenido, fecha_hora)
                VALUES (?, ?, ?)
                """,
                (
                    self.usuario_actual,
                    texto,
                    datetime.now().strftime("%H:%M")
                )
            )

            msj.delete(0, tk.END)
            limpiar_seleccion()
            cargar()

        def editar_mensaje():
            if not seleccionado["id"]:
                messagebox.showwarning(
                    "Atención",
                    "Seleccione un mensaje para editar."
                )
                return

            texto = msj.get().strip()

            if not texto:
                messagebox.showwarning(
                    "Atención",
                    "El mensaje no puede quedar vacío."
                )
                return

            self.ejecutar_db(
                """
                UPDATE mensajes
                SET contenido=?, fecha_hora=?
                WHERE id_mensaje=?
                """,
                (
                    texto,
                    datetime.now().strftime("%H:%M"),
                    seleccionado["id"]
                )
            )

            msj.delete(0, tk.END)
            limpiar_seleccion()
            cargar()

        def eliminar_mensaje():
            if not seleccionado["id"]:
                messagebox.showwarning(
                    "Atención",
                    "Seleccione un mensaje para eliminar."
                )
                return

            confirmar = messagebox.askyesno(
                "Eliminar mensaje",
                "¿Desea eliminar el mensaje seleccionado?"
            )

            if not confirmar:
                return

            self.ejecutar_db(
                "DELETE FROM mensajes WHERE id_mensaje=?",
                (seleccionado["id"],)
            )

            msj.delete(0, tk.END)
            limpiar_seleccion()
            cargar()

        tk.Button(
            botones,
            text="Enviar",
            command=enviar,
            bg="#2ecc71",
            fg="white",
            activebackground="#27ae60",
            activeforeground="white",
            font=("Segoe UI", 9, "bold"),
            bd=0,
            width=12,
            height=2,
            cursor="hand2"
        ).pack(side="left", padx=4)

        tk.Button(
            botones,
            text="Editar mensaje",
            command=editar_mensaje,
            bg="#3498db",
            fg="white",
            activebackground="#2980b9",
            activeforeground="white",
            font=("Segoe UI", 9, "bold"),
            bd=0,
            width=15,
            height=2,
            cursor="hand2"
        ).pack(side="left", padx=4)

        tk.Button(
            botones,
            text="Eliminar mensaje",
            command=eliminar_mensaje,
            bg="#e74c3c",
            fg="white",
            activebackground="#c0392b",
            activeforeground="white",
            font=("Segoe UI", 9, "bold"),
            bd=0,
            width=16,
            height=2,
            cursor="hand2"
        ).pack(side="left", padx=4)

        msj.bind("<Return>", lambda e: enviar())

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

        titulo = "EDITAR PAGO" if id_pago_editar else "💰 REGISTRAR NUEVO PAGO"

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
            values=["Efectivo", "Tarjeta"],
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
                ("ID", "UUID", "Proyecto", "Monto", "Método", "Fecha"),
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
                messagebox.showwarning(
                    "Error",
                    "El monto debe ser numérico."
                )
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

                messagebox.showinfo("Éxito", "Pago actualizado")
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

                messagebox.showinfo("Éxito", "Pago guardado")

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
        vf.title("Historial de Facturación")
        vf.geometry("900x560")

        tk.Label(
            vf,
            text="📄 PAGOS RECIBIDOS / FACTURAS",
            font=("Segoe UI", 14, "bold"),
            pady=20
        ).pack()

        barra = tk.Frame(vf)
        barra.pack(fill="x", padx=20)

        cols = ("ID", "Empresa (UUID)", "Proyecto", "Monto", "Método", "Fecha")

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
                messagebox.showwarning(
                    "Atención",
                    "Seleccione una factura."
                )
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
                f"Método de pago: {metodo}\n"
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

            messagebox.showinfo(
                "Éxito",
                f"Factura guardada en:\n{ruta}"
            )

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
                messagebox.showinfo(
                    "Impresión",
                    "Factura enviada a imprimir."
                )
            except Exception as e:
                messagebox.showerror(
                    "Error",
                    f"No se pudo imprimir automáticamente:\n{e}\n\n"
                    f"Archivo generado:\n{ruta_temp}"
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


if __name__ == "__main__":
    root = tk.Tk()
    app = SistemaGestion(root)
    root.mainloop()