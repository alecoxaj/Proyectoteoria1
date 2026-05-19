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
        v.geometry("840x540")
        v.configure(bg="#eef2f5")

        header = tk.Frame(v, bg="#3498db", height=72)
        header.pack(fill="x")
        header.pack_propagate(False)

        tk.Label(
            header,
            text=f"✏️ {titulo}",
            bg="#3498db",
            fg="white",
            font=("Segoe UI", 18, "bold")
        ).pack(side="left", padx=24)

        contenedor = tk.Frame(
            v,
            bg="#eef2f5"
        )
        contenedor.pack(fill="both", expand=True, padx=22, pady=18)

        barra = tk.Frame(
            contenedor,
            bg="white",
            padx=14,
            pady=12,
            highlightthickness=1,
            highlightbackground="#d8dee4"
        )
        barra.pack(fill="x", pady=(0, 14))

        tk.Label(
            barra,
            text="Buscar:",
            bg="white",
            fg="#2c3e50",
            font=("Segoe UI", 10, "bold")
        ).pack(side="left", padx=(0, 8))

        ent_buscar = tk.Entry(
            barra,
            font=("Segoe UI", 10),
            relief="solid",
            bd=1,
            width=34
        )
        ent_buscar.pack(side="left", ipady=5, padx=(0, 12))

        lbl_total = tk.Label(
            barra,
            text="0 registros",
            bg="white",
            fg="#7f8c8d",
            font=("Segoe UI", 9, "bold")
        )
        lbl_total.pack(side="right")

        tabla_card = tk.Frame(
            contenedor,
            bg="white",
            padx=14,
            pady=14,
            highlightthickness=1,
            highlightbackground="#d8dee4"
        )
        tabla_card.pack(fill="both", expand=True)

        tk.Label(
            tabla_card,
            text="Selecciona un registro",
            bg="white",
            fg="#2c3e50",
            font=("Segoe UI", 13, "bold")
        ).pack(anchor="w", pady=(0, 10))

        tabla_frame = tk.Frame(tabla_card, bg="white")
        tabla_frame.pack(fill="both", expand=True)

        scroll_y = ttk.Scrollbar(tabla_frame, orient="vertical")
        scroll_x = ttk.Scrollbar(tabla_frame, orient="horizontal")

        tree = ttk.Treeview(
            tabla_frame,
            columns=columnas,
            show="headings",
            yscrollcommand=scroll_y.set,
            xscrollcommand=scroll_x.set
        )

        scroll_y.config(command=tree.yview)
        scroll_x.config(command=tree.xview)

        for col in columnas:
            tree.heading(col, text=col)
            tree.column(col, width=160, anchor="center", stretch=False)

        if len(columnas) >= 2:
            tree.column(columnas[1], width=260, anchor="w", stretch=False)

        tree.grid(row=0, column=0, sticky="nsew")
        scroll_y.grid(row=0, column=1, sticky="ns")
        scroll_x.grid(row=1, column=0, sticky="ew")

        tabla_frame.grid_rowconfigure(0, weight=1)
        tabla_frame.grid_columnconfigure(0, weight=1)

        botones = tk.Frame(contenedor, bg="#eef2f5")
        botones.pack(fill="x", pady=(14, 0))

        datos_originales = self.obtener_lista_db(consulta)
        seleccion = {"values": None}

        def cargar_tabla(event=None):
            texto = ent_buscar.get().strip().lower()
            contador = 0

            for item in tree.get_children():
                tree.delete(item)

            for registro in datos_originales:
                fila_texto = " ".join(str(x).lower() for x in registro)

                if texto and texto not in fila_texto:
                    continue

                tree.insert("", "end", values=registro)
                contador += 1

            lbl_total.config(text=f"{contador} registros")

        def aceptar(event=None):
            item = tree.selection()

            if not item:
                messagebox.showwarning("Atención", "Seleccione un registro.")
                return

            seleccion["values"] = tree.item(item, "values")
            v.destroy()

        def cancelar():
            seleccion["values"] = None
            v.destroy()

        tk.Button(
            botones,
            text="✅ SELECCIONAR",
            command=aceptar,
            bg="#2ecc71",
            fg="white",
            activebackground="#27ae60",
            activeforeground="white",
            font=("Segoe UI", 10, "bold"),
            bd=0,
            height=2,
            cursor="hand2"
        ).pack(side="left", fill="x", expand=True, padx=(0, 6))

        tk.Button(
            botones,
            text="Cancelar",
            command=cancelar,
            bg="#95a5a6",
            fg="white",
            activebackground="#7f8c8d",
            activeforeground="white",
            font=("Segoe UI", 10, "bold"),
            bd=0,
            height=2,
            cursor="hand2"
        ).pack(side="left", fill="x", expand=True, padx=(6, 0))

        ent_buscar.bind("<KeyRelease>", cargar_tabla)
        tree.bind("<Double-1>", aceptar)

        cargar_tabla()
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
        v.title("Registrar Publicidad / Empresa")
        v.geometry("540x660")
        v.configure(bg="#eef2f5")
        v.resizable(False, False)

        datos_editar = None
        uuid_editar = ""

        if id_cliente_editar:
            datos = self.obtener_lista_db(
                """
                SELECT nombre_empresa, telefono_referido, correo, direccion_empresa, uuid_empresa
                FROM clientes
                WHERE id_cliente=?
                """,
                (id_cliente_editar,)
            )

            if datos:
                datos_editar = datos[0]
                uuid_editar = datos_editar[4]

        titulo_formulario = "Editar empresa registrada" if id_cliente_editar else "Registrar nueva empresa"

        header = tk.Frame(v, bg="#3498db", height=78)
        header.pack(fill="x")
        header.pack_propagate(False)

        tk.Label(
            header,
            text="👥 Registrar Publicidad",
            bg="#3498db",
            fg="white",
            font=("Segoe UI", 20, "bold")
        ).pack(side="left", padx=28)

        contenedor = tk.Frame(
            v,
            bg="white",
            padx=32,
            pady=24,
            highlightthickness=1,
            highlightbackground="#d8dee4"
        )
        contenedor.pack(fill="both", expand=True, padx=28, pady=24)

        tk.Label(
            contenedor,
            text=titulo_formulario,
            bg="white",
            fg="#2c3e50",
            font=("Segoe UI", 16, "bold")
        ).pack(anchor="w", pady=(0, 6))

        tk.Label(
            contenedor,
            text="Guarda los datos de la empresa para asociarla a proyectos, pagos y publicidad.",
            bg="white",
            fg="#7f8c8d",
            font=("Segoe UI", 9),
            wraplength=440,
            justify="left"
        ).pack(anchor="w", pady=(0, 16))

        id_texto = f"ID Personal: {uuid_editar}" if id_cliente_editar else "El ID Personal se generará automáticamente al guardar."

        tk.Label(
            contenedor,
            text=id_texto,
            bg="#f4f6f8",
            fg="#2c3e50",
            font=("Consolas", 10, "bold"),
            relief="solid",
            bd=1,
            anchor="w",
            padx=10
        ).pack(fill="x", pady=(0, 18), ipady=7)

        def etiqueta(texto):
            tk.Label(
                contenedor,
                text=texto,
                bg="white",
                fg="#2c3e50",
                font=("Segoe UI", 9, "bold")
            ).pack(anchor="w")

        def campo():
            entrada = tk.Entry(
                contenedor,
                font=("Segoe UI", 10),
                relief="solid",
                bd=1
            )
            entrada.pack(fill="x", pady=(4, 12), ipady=5)
            return entrada

        etiqueta("Nombre de la empresa:")
        nom_e = campo()

        etiqueta("Número telefónico referido:")
        tel_e = campo()

        etiqueta("Correo electrónico:")
        cor_e = campo()

        etiqueta("Dirección de la empresa:")
        dir_e = campo()

        if datos_editar:
            nom_e.insert(0, datos_editar[0])
            tel_e.insert(0, datos_editar[1] or "")
            cor_e.insert(0, datos_editar[2] or "")
            dir_e.insert(0, datos_editar[3] or "")

        botones = tk.Frame(contenedor, bg="white")
        botones.pack(fill="x", pady=(8, 0))

        def limpiar_campos():
            nom_e.delete(0, tk.END)
            tel_e.delete(0, tk.END)
            cor_e.delete(0, tk.END)
            dir_e.delete(0, tk.END)
            nom_e.focus()

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
            telefono = tel_e.get().strip()
            correo = cor_e.get().strip()
            direccion = dir_e.get().strip()

            if not nombre:
                messagebox.showwarning(
                    "Atención",
                    "El nombre de la empresa es obligatorio."
                )
                return

            if correo and "@" not in correo:
                messagebox.showwarning(
                    "Atención",
                    "Ingrese un correo válido o deje el campo vacío."
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
                            telefono,
                            correo,
                            direccion,
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
                            telefono,
                            correo,
                            direccion,
                            id_personal
                        )
                    )

                    messagebox.showinfo(
                        "Éxito",
                        f"Empresa registrada correctamente.\n\nID PERSONAL: {id_personal}"
                    )

                v.destroy()

            except Exception as e:
                messagebox.showerror("Error", f"No se pudo guardar:\n{e}")

        tk.Button(
            botones,
            text="💾 GUARDAR CAMBIOS" if id_cliente_editar else "💾 GUARDAR REGISTRO",
            bg="#2ecc71",
            fg="white",
            activebackground="#27ae60",
            activeforeground="white",
            font=("Segoe UI", 10, "bold"),
            bd=0,
            height=2,
            cursor="hand2",
            command=guardar
        ).pack(fill="x", pady=(0, 8))

        fila_botones = tk.Frame(botones, bg="white")
        fila_botones.pack(fill="x")

        tk.Button(
            fila_botones,
            text="✏️ EDITAR EXISTENTE",
            bg="#3498db",
            fg="white",
            activebackground="#2980b9",
            activeforeground="white",
            font=("Segoe UI", 10, "bold"),
            bd=0,
            height=3,
            cursor="hand2",
            command=editar_existente
        ).pack(side="left", fill="x", expand=True, padx=(0, 6))

        tk.Button(
            fila_botones,
            text="🧹 LIMPIAR",
            bg="#95a5a6",
            fg="white",
            activebackground="#7f8c8d",
            activeforeground="white",
            font=("Segoe UI", 10, "bold"),
            bd=0,
            height=3,
            cursor="hand2",
            command=limpiar_campos
        ).pack(side="left", fill="x", expand=True, padx=(6, 0))

    def ventana_crear_proyecto(self, id_proyecto_editar=None):
        v = tk.Toplevel(self.root)
        v.title("Crear Proyecto")
        v.geometry("540x650")
        v.configure(bg="#eef2f5")
        v.resizable(False, False)

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

        titulo_formulario = "Editar proyecto" if id_proyecto_editar else "Crear nuevo proyecto"

        header = tk.Frame(v, bg="#2ecc71", height=78)
        header.pack(fill="x")
        header.pack_propagate(False)

        tk.Label(
            header,
            text="➕ Crear Proyecto",
            bg="#2ecc71",
            fg="white",
            font=("Segoe UI", 20, "bold")
        ).pack(side="left", padx=28)

        contenedor = tk.Frame(
            v,
            bg="white",
            padx=32,
            pady=24,
            highlightthickness=1,
            highlightbackground="#d8dee4"
        )
        contenedor.pack(fill="both", expand=True, padx=28, pady=24)

        tk.Label(
            contenedor,
            text=titulo_formulario,
            bg="white",
            fg="#2c3e50",
            font=("Segoe UI", 16, "bold")
        ).pack(anchor="w", pady=(0, 6))

        tk.Label(
            contenedor,
            text="Asocia un proyecto a una empresa y define su fecha de inicio y estado.",
            bg="white",
            fg="#7f8c8d",
            font=("Segoe UI", 9),
            wraplength=440,
            justify="left"
        ).pack(anchor="w", pady=(0, 18))

        def etiqueta(texto):
            tk.Label(
                contenedor,
                text=texto,
                bg="white",
                fg="#2c3e50",
                font=("Segoe UI", 9, "bold")
            ).pack(anchor="w")

        def campo():
            entrada = tk.Entry(
                contenedor,
                font=("Segoe UI", 10),
                relief="solid",
                bd=1
            )
            entrada.pack(fill="x", pady=(4, 14), ipady=5)
            return entrada

        etiqueta("Empresa:")
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
            contenedor,
            values=list(dict_clientes.keys()),
            state="readonly",
            font=("Segoe UI", 10)
        )
        cb_clientes.pack(fill="x", pady=(4, 14), ipady=4)

        etiqueta("Nombre del proyecto:")
        ent_nombre_p = campo()

        etiqueta("Fecha de inicio:")
        ent_fecha = DateEntry(
            contenedor,
            width=12,
            background="#2ecc71",
            foreground="white",
            borderwidth=2,
            date_pattern="dd/mm/yyyy",
            font=("Segoe UI", 10)
        )
        ent_fecha.pack(fill="x", pady=(4, 14), ipady=4)

        etiqueta("Estado:")
        cb_estado = ttk.Combobox(
            contenedor,
            values=["En Espera", "Trabajando", "Finalizado"],
            state="readonly",
            font=("Segoe UI", 10)
        )
        cb_estado.current(0)
        cb_estado.pack(fill="x", pady=(4, 18), ipady=4)

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

        botones = tk.Frame(contenedor, bg="white")
        botones.pack(fill="x", pady=(10, 0))

        def limpiar_campos():
            cb_clientes.set("")
            ent_nombre_p.delete(0, tk.END)
            cb_estado.current(0)
            ent_nombre_p.focus()

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
            emp = cb_clientes.get().strip()
            nom = ent_nombre_p.get().strip()
            estado = cb_estado.get().strip()
            fecha = ent_fecha.get()

            if not emp:
                messagebox.showwarning("Atención", "Selecciona una empresa.")
                return

            if not nom:
                messagebox.showwarning("Atención", "Ingresa el nombre del proyecto.")
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
                            fecha,
                            estado,
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
                            fecha,
                            estado
                        )
                    )

                    messagebox.showinfo(
                        "Éxito",
                        "Proyecto guardado correctamente."
                    )

                v.destroy()

            except Exception as e:
                messagebox.showerror("Error", f"No se pudo guardar:\n{e}")

        tk.Button(
            botones,
            text="💾 GUARDAR CAMBIOS" if id_proyecto_editar else "💾 REGISTRAR PROYECTO",
            bg="#2ecc71",
            fg="white",
            activebackground="#27ae60",
            activeforeground="white",
            font=("Segoe UI", 10, "bold"),
            bd=0,
            height=2,
            cursor="hand2",
            command=guardar_proy
        ).pack(fill="x", pady=(0, 8))

        fila_botones = tk.Frame(botones, bg="white")
        fila_botones.pack(fill="x")

        tk.Button(
            fila_botones,
            text="✏️ EDITAR EXISTENTE",
            bg="#3498db",
            fg="white",
            activebackground="#2980b9",
            activeforeground="white",
            font=("Segoe UI", 10, "bold"),
            bd=0,
            height=3,
            cursor="hand2",
            command=editar_existente
        ).pack(side="left", fill="x", expand=True, padx=(0, 6))

        tk.Button(
            fila_botones,
            text="🧹 LIMPIAR",
            bg="#95a5a6",
            fg="white",
            activebackground="#7f8c8d",
            activeforeground="white",
            font=("Segoe UI", 10, "bold"),
            bd=0,
            height=3,
            cursor="hand2",
            command=limpiar_campos
        ).pack(side="left", fill="x", expand=True, padx=(6, 0))

    def ventana_historial(self):
        v = tk.Toplevel(self.root)
        v.title("Historial de Proyecto y Empresas")
        v.geometry("1120x720")
        v.configure(bg="#eef2f5")

        header = tk.Frame(v, bg="#9b59b6", height=78)
        header.pack(fill="x")
        header.pack_propagate(False)

        tk.Label(
            header,
            text="📋 Historial",
            bg="#9b59b6",
            fg="white",
            font=("Segoe UI", 20, "bold")
        ).pack(side="left", padx=28)

        tk.Label(
            header,
            text="Consulta empresas y proyectos registrados",
            bg="#9b59b6",
            fg="#f4e9fb",
            font=("Segoe UI", 10)
        ).pack(side="left", padx=8)

        contenedor = tk.Frame(v, bg="#eef2f5")
        contenedor.pack(fill="both", expand=True, padx=22, pady=20)

        filtros = tk.Frame(
            contenedor,
            bg="white",
            padx=16,
            pady=14,
            highlightthickness=1,
            highlightbackground="#d8dee4"
        )
        filtros.pack(fill="x", pady=(0, 14))

        tk.Label(
            filtros,
            text="Buscar por ID:",
            bg="white",
            fg="#2c3e50",
            font=("Segoe UI", 10, "bold")
        ).pack(side="left", padx=(0, 8))

        ent_id_busq = tk.Entry(
            filtros,
            font=("Consolas", 10),
            relief="solid",
            bd=1,
            width=20
        )
        ent_id_busq.pack(side="left", ipady=5, padx=(0, 18))

        tk.Label(
            filtros,
            text="Proyecto:",
            bg="white",
            fg="#2c3e50",
            font=("Segoe UI", 10, "bold")
        ).pack(side="left", padx=(0, 8))

        ent_nom_busq = tk.Entry(
            filtros,
            font=("Segoe UI", 10),
            relief="solid",
            bd=1,
            width=30
        )
        ent_nom_busq.pack(side="left", ipady=5, padx=(0, 18))

        lbl_resumen = tk.Label(
            filtros,
            text="0 empresas · 0 proyectos",
            bg="white",
            fg="#7f8c8d",
            font=("Segoe UI", 9, "bold")
        )
        lbl_resumen.pack(side="right")

        cuerpo = tk.Frame(contenedor, bg="#eef2f5")
        cuerpo.pack(fill="both", expand=True)

        panel_empresas = tk.Frame(
            cuerpo,
            bg="white",
            padx=14,
            pady=14,
            highlightthickness=1,
            highlightbackground="#d8dee4"
        )
        panel_empresas.pack(side="left", fill="both", expand=True, padx=(0, 8))

        panel_proyectos = tk.Frame(
            cuerpo,
            bg="white",
            padx=14,
            pady=14,
            highlightthickness=1,
            highlightbackground="#d8dee4"
        )
        panel_proyectos.pack(side="right", fill="both", expand=True, padx=(8, 0))

        tk.Label(
            panel_empresas,
            text="Empresas",
            bg="white",
            fg="#2c3e50",
            font=("Segoe UI", 13, "bold")
        ).pack(anchor="w", pady=(0, 10))

        frame_empresas = tk.Frame(panel_empresas, bg="white")
        frame_empresas.pack(fill="both", expand=True)

        cols_c = ("Empresa", "ID Personal")

        scroll_c_y = ttk.Scrollbar(frame_empresas, orient="vertical")
        scroll_c_x = ttk.Scrollbar(frame_empresas, orient="horizontal")

        tree_clientes = ttk.Treeview(
            frame_empresas,
            columns=cols_c,
            show="headings",
            yscrollcommand=scroll_c_y.set,
            xscrollcommand=scroll_c_x.set
        )

        scroll_c_y.config(command=tree_clientes.yview)
        scroll_c_x.config(command=tree_clientes.xview)

        tree_clientes.heading("Empresa", text="Empresa")
        tree_clientes.heading("ID Personal", text="ID Personal")

        tree_clientes.column("Empresa", width=260, anchor="w", stretch=False)
        tree_clientes.column("ID Personal", width=170, anchor="center", stretch=False)

        tree_clientes.grid(row=0, column=0, sticky="nsew")
        scroll_c_y.grid(row=0, column=1, sticky="ns")
        scroll_c_x.grid(row=1, column=0, sticky="ew")

        frame_empresas.grid_rowconfigure(0, weight=1)
        frame_empresas.grid_columnconfigure(0, weight=1)

        tk.Label(
            panel_proyectos,
            text="Proyectos",
            bg="white",
            fg="#2c3e50",
            font=("Segoe UI", 13, "bold")
        ).pack(anchor="w", pady=(0, 10))

        frame_proyectos = tk.Frame(panel_proyectos, bg="white")
        frame_proyectos.pack(fill="both", expand=True)

        cols_p = ("Proyecto", "Fecha Inicio", "Estado", "Empresa Relacionada")

        scroll_p_y = ttk.Scrollbar(frame_proyectos, orient="vertical")
        scroll_p_x = ttk.Scrollbar(frame_proyectos, orient="horizontal")

        tree_proyectos = ttk.Treeview(
            frame_proyectos,
            columns=cols_p,
            show="headings",
            yscrollcommand=scroll_p_y.set,
            xscrollcommand=scroll_p_x.set
        )

        scroll_p_y.config(command=tree_proyectos.yview)
        scroll_p_x.config(command=tree_proyectos.xview)

        for col in cols_p:
            tree_proyectos.heading(col, text=col)

        tree_proyectos.column("Proyecto", width=240, anchor="w", stretch=False)
        tree_proyectos.column("Fecha Inicio", width=120, anchor="center", stretch=False)
        tree_proyectos.column("Estado", width=120, anchor="center", stretch=False)
        tree_proyectos.column("Empresa Relacionada", width=240, anchor="w", stretch=False)

        tree_proyectos.grid(row=0, column=0, sticky="nsew")
        scroll_p_y.grid(row=0, column=1, sticky="ns")
        scroll_p_x.grid(row=1, column=0, sticky="ew")

        frame_proyectos.grid_rowconfigure(0, weight=1)
        frame_proyectos.grid_columnconfigure(0, weight=1)

        acciones = tk.Frame(contenedor, bg="#eef2f5")
        acciones.pack(fill="x", pady=(14, 0))

        def actualizar_tablas(event=None):
            for i in tree_clientes.get_children():
                tree_clientes.delete(i)

            for i in tree_proyectos.get_children():
                tree_proyectos.delete(i)

            id_busc = ent_id_busq.get().strip()
            nom_busc = ent_nom_busq.get().strip()

            query_c = """
                SELECT nombre_empresa, uuid_empresa
                FROM clientes
                WHERE 1=1
            """
            params_c = []

            if id_busc:
                query_c += " AND uuid_empresa LIKE ?"
                params_c.append(f"%{id_busc}%")

            query_c += " ORDER BY nombre_empresa"

            total_empresas = 0

            for d in self.obtener_lista_db(query_c, tuple(params_c)):
                tree_clientes.insert("", "end", values=d)
                total_empresas += 1

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

            query_p += " ORDER BY p.id_proyecto DESC"

            total_proyectos = 0

            for p in self.obtener_lista_db(query_p, tuple(params_p)):
                tree_proyectos.insert("", "end", values=p)
                total_proyectos += 1

            lbl_resumen.config(
                text=f"{total_empresas} empresas · {total_proyectos} proyectos"
            )

        def al_seleccionar_cliente(event=None):
            item = tree_clientes.selection()

            if item:
                uuid_sel = tree_clientes.item(item)["values"][1]
                ent_id_busq.delete(0, tk.END)
                ent_id_busq.insert(0, uuid_sel)
                actualizar_tablas()

        def limpiar_filtros():
            ent_id_busq.delete(0, tk.END)
            ent_nom_busq.delete(0, tk.END)
            actualizar_tablas()

        def copiar_id():
            item = tree_clientes.selection()

            if not item:
                messagebox.showwarning("Atención", "Selecciona una empresa.")
                return

            uuid_sel = tree_clientes.item(item)["values"][1]
            v.clipboard_clear()
            v.clipboard_append(uuid_sel)
            messagebox.showinfo("Copiado", f"ID copiado:\n{uuid_sel}")

        def boton_accion(texto, color, comando):
            tk.Button(
                acciones,
                text=texto,
                command=comando,
                bg=color,
                fg="white",
                activebackground=color,
                activeforeground="white",
                font=("Segoe UI", 10, "bold"),
                bd=0,
                height=2,
                cursor="hand2"
            ).pack(side="left", fill="x", expand=True, padx=5)

        boton_accion("📋 Copiar ID", "#34495e", copiar_id)
        boton_accion("🧹 Limpiar filtros", "#95a5a6", limpiar_filtros)
        boton_accion("🔄 Actualizar", "#3498db", actualizar_tablas)

        ent_id_busq.bind("<KeyRelease>", actualizar_tablas)
        ent_nom_busq.bind("<KeyRelease>", actualizar_tablas)
        tree_clientes.bind("<<TreeviewSelect>>", al_seleccionar_cliente)

        actualizar_tablas()

    def ventana_portal_empresa(self):
        v = tk.Toplevel(self.root)
        v.title("Portal ID de Empresas")
        v.geometry("760x560")
        v.configure(bg="#eef2f5")

        header = tk.Frame(v, bg="#34495e", height=78)
        header.pack(fill="x")
        header.pack_propagate(False)

        tk.Label(
            header,
            text="🆔 Portal ID",
            bg="#34495e",
            fg="white",
            font=("Segoe UI", 20, "bold")
        ).pack(side="left", padx=28)

        tk.Label(
            header,
            text="Directorio de identificadores de empresas",
            bg="#34495e",
            fg="#dfe6e9",
            font=("Segoe UI", 10)
        ).pack(side="left", padx=8)

        contenedor = tk.Frame(v, bg="#eef2f5")
        contenedor.pack(fill="both", expand=True, padx=22, pady=20)

        barra = tk.Frame(
            contenedor,
            bg="white",
            padx=14,
            pady=12,
            highlightthickness=1,
            highlightbackground="#d8dee4"
        )
        barra.pack(fill="x", pady=(0, 14))

        tk.Label(
            barra,
            text="Buscar:",
            bg="white",
            fg="#2c3e50",
            font=("Segoe UI", 10, "bold")
        ).pack(side="left", padx=(0, 8))

        ent_buscar = tk.Entry(
            barra,
            font=("Segoe UI", 10),
            relief="solid",
            bd=1,
            width=34
        )
        ent_buscar.pack(side="left", ipady=5, padx=(0, 12))

        lbl_total = tk.Label(
            barra,
            text="0 empresas",
            bg="white",
            fg="#7f8c8d",
            font=("Segoe UI", 9, "bold")
        )
        lbl_total.pack(side="right")

        tabla_card = tk.Frame(
            contenedor,
            bg="white",
            padx=14,
            pady=14,
            highlightthickness=1,
            highlightbackground="#d8dee4"
        )
        tabla_card.pack(fill="both", expand=True)

        tk.Label(
            tabla_card,
            text="Empresas registradas",
            bg="white",
            fg="#2c3e50",
            font=("Segoe UI", 13, "bold")
        ).pack(anchor="w", pady=(0, 10))

        tabla_frame = tk.Frame(tabla_card, bg="white")
        tabla_frame.pack(fill="both", expand=True)

        cols = ("Empresa", "UUID / ID Personal")

        scroll_y = ttk.Scrollbar(tabla_frame, orient="vertical")
        scroll_x = ttk.Scrollbar(tabla_frame, orient="horizontal")

        tree = ttk.Treeview(
            tabla_frame,
            columns=cols,
            show="headings",
            yscrollcommand=scroll_y.set,
            xscrollcommand=scroll_x.set
        )

        scroll_y.config(command=tree.yview)
        scroll_x.config(command=tree.xview)

        tree.heading("Empresa", text="Empresa")
        tree.heading("UUID / ID Personal", text="UUID / ID Personal")

        tree.column("Empresa", width=320, anchor="w", stretch=False)
        tree.column("UUID / ID Personal", width=260, anchor="center", stretch=False)

        tree.grid(row=0, column=0, sticky="nsew")
        scroll_y.grid(row=0, column=1, sticky="ns")
        scroll_x.grid(row=1, column=0, sticky="ew")

        tabla_frame.grid_rowconfigure(0, weight=1)
        tabla_frame.grid_columnconfigure(0, weight=1)

        botones = tk.Frame(contenedor, bg="#eef2f5")
        botones.pack(fill="x", pady=(14, 0))

        def obtener_datos():
            return self.obtener_lista_db(
                """
                SELECT nombre_empresa, uuid_empresa
                FROM clientes
                ORDER BY nombre_empresa
                """
            )

        def cargar_datos(event=None):
            texto = ent_buscar.get().strip().lower()
            contador = 0

            for item in tree.get_children():
                tree.delete(item)

            for empresa, uuid_emp in obtener_datos():
                fila_texto = f"{empresa} {uuid_emp}".lower()

                if texto and texto not in fila_texto:
                    continue

                tree.insert("", "end", values=(empresa, uuid_emp))
                contador += 1

            lbl_total.config(text=f"{contador} empresas")

        def obtener_seleccion():
            item = tree.selection()

            if not item:
                messagebox.showwarning(
                    "Atención",
                    "Selecciona una empresa."
                )
                return None

            return tree.item(item, "values")

        def copiar_id():
            seleccionado = obtener_seleccion()

            if not seleccionado:
                return

            uuid_emp = seleccionado[1]
            v.clipboard_clear()
            v.clipboard_append(uuid_emp)
            messagebox.showinfo("Copiado", f"ID copiado:\n{uuid_emp}")

        def ver_detalle():
            seleccionado = obtener_seleccion()

            if not seleccionado:
                return

            empresa, uuid_emp = seleccionado

            datos = self.obtener_lista_db(
                """
                SELECT telefono_referido, correo, direccion_empresa
                FROM clientes
                WHERE uuid_empresa=?
                """,
                (uuid_emp,)
            )

            telefono, correo, direccion = datos[0] if datos else ("", "", "")

            detalle = tk.Toplevel(v)
            detalle.title("Detalle de empresa")
            detalle.geometry("480x360")
            detalle.configure(bg="#eef2f5")

            card = tk.Frame(
                detalle,
                bg="white",
                padx=24,
                pady=22,
                highlightthickness=1,
                highlightbackground="#d8dee4"
            )
            card.pack(fill="both", expand=True, padx=22, pady=22)

            tk.Label(
                card,
                text=empresa,
                bg="white",
                fg="#2c3e50",
                font=("Segoe UI", 15, "bold"),
                wraplength=400,
                justify="left"
            ).pack(anchor="w", pady=(0, 12))

            texto = (
                f"ID Personal: {uuid_emp}\n\n"
                f"Teléfono: {telefono or 'No registrado'}\n"
                f"Correo: {correo or 'No registrado'}\n"
                f"Dirección: {direccion or 'No registrada'}"
            )

            tk.Label(
                card,
                text=texto,
                bg="white",
                fg="#2c3e50",
                font=("Segoe UI", 10),
                justify="left",
                wraplength=400
            ).pack(anchor="w")

            tk.Button(
                card,
                text="📋 Copiar ID",
                bg="#34495e",
                fg="white",
                activebackground="#2c3e50",
                activeforeground="white",
                font=("Segoe UI", 10, "bold"),
                bd=0,
                height=2,
                cursor="hand2",
                command=copiar_id
            ).pack(fill="x", pady=(22, 0))

        def editar_empresa():
            seleccionado = obtener_seleccion()

            if not seleccionado:
                return

            empresa, uuid_emp = seleccionado

            datos = self.obtener_lista_db(
                """
                SELECT id_cliente
                FROM clientes
                WHERE uuid_empresa=?
                """,
                (uuid_emp,)
            )

            if not datos:
                messagebox.showerror(
                    "Error",
                    "No se encontró la empresa seleccionada."
                )
                return

            v.destroy()
            self.ventana_registrar_cliente_formal(int(datos[0][0]))

        def boton_accion(texto, color, comando):
            tk.Button(
                botones,
                text=texto,
                command=comando,
                bg=color,
                fg="white",
                activebackground=color,
                activeforeground="white",
                font=("Segoe UI", 10, "bold"),
                bd=0,
                height=2,
                cursor="hand2"
            ).pack(side="left", fill="x", expand=True, padx=5)

        boton_accion("📋 Copiar ID", "#34495e", copiar_id)
        boton_accion("👁 Detalle", "#3498db", ver_detalle)
        boton_accion("✏️ Editar", "#8e44ad", editar_empresa)
        boton_accion("🔄 Actualizar", "#2ecc71", cargar_datos)

        ent_buscar.bind("<KeyRelease>", cargar_datos)
        tree.bind("<Double-1>", lambda e: ver_detalle())

        cargar_datos()

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

        main = tk.Frame(v, bg="#edf2f7")
        main.pack(fill="both", expand=True, padx=18, pady=18)

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

        titulo("Herramientas")

        herramientas = tk.Frame(
            panel,
            bg="white"
        )

        herramientas.pack(fill="x")

        for i in range(2):
            herramientas.grid_columnconfigure(i, weight=1)

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

            if self.img_original and self.path_actual:
                self.img_original.save(self.path_actual)

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

        botones = [

            ("📂 Subir", "#10b981", cargar_foto),
            ("🗑 Eliminar", "#ef4444", eliminar_imagen),

            ("✂️ Recortar", "#f59e0b", recortar_centro),
            ("🌓 Escala gris", "#6b7280", convertir_gris),

            ("🪄 Transparencia", "#14b8a6", hacer_transparente),
            ("↶ Deshacer", "#64748b", deshacer_cambio),

            ("✏️ Editar", "#8b5cf6", editar_existente),
            ("✅ Guardar", "#0f766e", guardar_db)

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

        titulo("Acciones")

        acciones = tk.Frame(
            panel,
            bg="white"
        )

        acciones.pack(fill="x")

        for i in range(2):
            acciones.grid_columnconfigure(i, weight=1)

        boton_estilo(
            acciones,
            "🖨 Imprimir",
            "#334155",
            imprimir_imagen
        ).grid(
            row=0,
            column=0,
            sticky="ew",
            padx=4,
            pady=4
        )

        ent_uuid.bind(
            "<FocusOut>",
            cargar_proyectos_de_empresa
        )

        canvas.bind(
            "<Configure>",
            lambda e: actualizar_preview()
        )

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
        v.title("Continuar Proyecto")
        v.geometry("1050x680")
        v.configure(bg="#eef2f5")

        header = tk.Frame(v, bg="#e74c3c", height=78)
        header.pack(fill="x")
        header.pack_propagate(False)

        tk.Label(
            header,
            text="🚀 Continuar Proyecto",
            bg="#e74c3c",
            fg="white",
            font=("Segoe UI", 20, "bold")
        ).pack(side="left", padx=28)

        tk.Label(
            header,
            text="Retoma trabajos pendientes o revisa resultados finalizados",
            bg="#e74c3c",
            fg="#fdecea",
            font=("Segoe UI", 10)
        ).pack(side="left", padx=8)

        contenedor = tk.Frame(v, bg="#eef2f5")
        contenedor.pack(fill="both", expand=True, padx=22, pady=20)

        barra = tk.Frame(
            contenedor,
            bg="white",
            padx=16,
            pady=14,
            highlightthickness=1,
            highlightbackground="#d8dee4"
        )
        barra.pack(fill="x", pady=(0, 14))

        tk.Label(
            barra,
            text="Buscar:",
            bg="white",
            fg="#2c3e50",
            font=("Segoe UI", 10, "bold")
        ).pack(side="left", padx=(0, 8))

        ent_buscar = tk.Entry(
            barra,
            font=("Segoe UI", 10),
            relief="solid",
            bd=1,
            width=42
        )
        ent_buscar.pack(side="left", ipady=5, padx=(0, 12))

        tk.Label(
            barra,
            text="ID empresa, proyecto o archivo",
            bg="white",
            fg="#7f8c8d",
            font=("Segoe UI", 9)
        ).pack(side="left")

        lbl_total = tk.Label(
            barra,
            text="0 resultados",
            bg="white",
            fg="#7f8c8d",
            font=("Segoe UI", 9, "bold")
        )
        lbl_total.pack(side="right")

        tabla_card = tk.Frame(
            contenedor,
            bg="white",
            padx=14,
            pady=14,
            highlightthickness=1,
            highlightbackground="#d8dee4"
        )
        tabla_card.pack(fill="both", expand=True)

        tk.Label(
            tabla_card,
            text="Trabajos encontrados",
            bg="white",
            fg="#2c3e50",
            font=("Segoe UI", 13, "bold")
        ).pack(anchor="w", pady=(0, 10))

        tabla_frame = tk.Frame(tabla_card, bg="white")
        tabla_frame.pack(fill="both", expand=True)

        cols = ("Tipo", "Nombre / Archivo", "Estado", "Fecha", "UUID")

        scroll_y = ttk.Scrollbar(tabla_frame, orient="vertical")
        scroll_x = ttk.Scrollbar(tabla_frame, orient="horizontal")

        tree = ttk.Treeview(
            tabla_frame,
            columns=cols,
            show="headings",
            yscrollcommand=scroll_y.set,
            xscrollcommand=scroll_x.set
        )

        scroll_y.config(command=tree.yview)
        scroll_x.config(command=tree.xview)

        for c in cols:
            tree.heading(c, text=c)

        tree.column("Tipo", width=120, anchor="center", stretch=False)
        tree.column("Nombre / Archivo", width=360, anchor="w", stretch=False)
        tree.column("Estado", width=130, anchor="center", stretch=False)
        tree.column("Fecha", width=140, anchor="center", stretch=False)
        tree.column("UUID", width=170, anchor="center", stretch=False)

        tree.tag_configure("pendiente", background="#fff7e6")
        tree.tag_configure("trabajando", background="#eaf4ff")
        tree.tag_configure("finalizado", background="#eafaf1")

        tree.grid(row=0, column=0, sticky="nsew")
        scroll_y.grid(row=0, column=1, sticky="ns")
        scroll_x.grid(row=1, column=0, sticky="ew")

        tabla_frame.grid_rowconfigure(0, weight=1)
        tabla_frame.grid_columnconfigure(0, weight=1)

        acciones = tk.Frame(contenedor, bg="#eef2f5")
        acciones.pack(fill="x", pady=(14, 0))

        def etiqueta_estado(estado):
            estado_l = (estado or "").lower()

            if "finalizado" in estado_l:
                return "finalizado"

            if "trabajando" in estado_l:
                return "trabajando"

            return "pendiente"

        def obtener_resultados(filtro):
            if not filtro:
                return []

            proy = self.obtener_lista_db(
                """
                SELECT 'Proyecto', p.nombre, p.estado, p.fecha_inicio, c.uuid_empresa
                FROM proyectos p
                JOIN clientes c ON p.id_cliente = c.id_cliente
                WHERE c.uuid_empresa LIKE ? OR p.nombre LIKE ? OR c.nombre_empresa LIKE ?
                """,
                (f"%{filtro}%", f"%{filtro}%", f"%{filtro}%")
            )

            pub = self.obtener_lista_db(
                """
                SELECT 'Publicidad', COALESCE(proyecto, nombre_archivo), estado, fecha, uuid_empresa
                FROM publicidad
                WHERE uuid_empresa LIKE ? OR nombre_archivo LIKE ? OR proyecto LIKE ?
                """,
                (f"%{filtro}%", f"%{filtro}%", f"%{filtro}%")
            )

            return proy + pub

        def buscar(event=None):
            for item in tree.get_children():
                tree.delete(item)

            filtro = ent_buscar.get().strip()
            resultados = obtener_resultados(filtro)

            for r in resultados:
                tree.insert(
                    "",
                    "end",
                    values=r,
                    tags=(etiqueta_estado(r[2]),)
                )

            lbl_total.config(text=f"{len(resultados)} resultados")

        def obtener_seleccion():
            item_sel = tree.selection()

            if not item_sel:
                messagebox.showwarning("Atención", "Selecciona un registro.")
                return None

            return tree.item(item_sel, "values")

        def ejecutar_accion(event=None):
            seleccionado = obtener_seleccion()

            if not seleccionado:
                return

            tipo, nombre, estado, fecha, uuid_e = seleccionado

            if estado == "Finalizado":
                self.mostrar_vista_previa_final(nombre, tipo)
                return

            v.destroy()

            if tipo == "Publicidad":
                self.ventana_publicidad_editor(id_editar=uuid_e)
            else:
                messagebox.showinfo(
                    "Proyecto",
                    f"Proyecto pendiente:\n\n{nombre}\n\nPuedes editarlo desde el módulo Crear Proyecto."
                )

        def abrir_publicidad():
            seleccionado = obtener_seleccion()

            if not seleccionado:
                return

            tipo, nombre, estado, fecha, uuid_e = seleccionado

            if tipo != "Publicidad":
                messagebox.showwarning(
                    "Atención",
                    "Selecciona un registro de publicidad."
                )
                return

            v.destroy()
            self.ventana_publicidad_editor(id_editar=uuid_e)

        def ver_finalizado():
            seleccionado = obtener_seleccion()

            if not seleccionado:
                return

            tipo, nombre, estado, fecha, uuid_e = seleccionado
            self.mostrar_vista_previa_final(nombre, tipo)

        def limpiar_busqueda():
            ent_buscar.delete(0, tk.END)

            for item in tree.get_children():
                tree.delete(item)

            lbl_total.config(text="0 resultados")
            ent_buscar.focus()

        def boton_accion(texto, color, comando):
            tk.Button(
                acciones,
                text=texto,
                command=comando,
                bg=color,
                fg="white",
                activebackground=color,
                activeforeground="white",
                font=("Segoe UI", 10, "bold"),
                bd=0,
                height=2,
                cursor="hand2"
            ).pack(side="left", fill="x", expand=True, padx=5)

        boton_accion("🚀 Continuar seleccionado", "#e74c3c", ejecutar_accion)
        boton_accion("🎨 Abrir publicidad", "#f39c12", abrir_publicidad)
        boton_accion("👁 Ver finalizado", "#34495e", ver_finalizado)
        boton_accion("🧹 Limpiar", "#95a5a6", limpiar_busqueda)

        ent_buscar.bind("<KeyRelease>", buscar)
        ent_buscar.bind("<Return>", ejecutar_accion)
        tree.bind("<Double-1>", ejecutar_accion)

        ent_buscar.focus()

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
        vp.geometry("520x620")
        vp.configure(bg="#eef2f5")
        vp.resizable(False, False)

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

        fecha_real = datos_editar[4] if datos_editar else datetime.now().strftime("%d/%m/%Y %H:%M")
        titulo_formulario = "Editar comprobante de pago" if id_pago_editar else "Nuevo comprobante de pago"

        header = tk.Frame(vp, bg="#e67e22", height=70)
        header.pack(fill="x")
        header.pack_propagate(False)

        tk.Label(
            header,
            text="💰 Registro de Pagos",
            bg="#e67e22",
            fg="white",
            font=("Segoe UI", 19, "bold")
        ).pack(side="left", padx=26)

        contenedor = tk.Frame(
            vp,
            bg="white",
            padx=28,
            pady=18,
            highlightthickness=1,
            highlightbackground="#d8dee4"
        )
        contenedor.pack(fill="both", expand=True, padx=24, pady=20)

        tk.Label(
            contenedor,
            text=titulo_formulario,
            bg="white",
            fg="#2c3e50",
            font=("Segoe UI", 15, "bold")
        ).pack(anchor="w", pady=(0, 2))

        tk.Label(
            contenedor,
            text="Completa los datos del pago recibido.",
            bg="white",
            fg="#7f8c8d",
            font=("Segoe UI", 9)
        ).pack(anchor="w", pady=(0, 12))

        def etiqueta(texto):
            tk.Label(
                contenedor,
                text=texto,
                bg="white",
                fg="#2c3e50",
                font=("Segoe UI", 9, "bold")
            ).pack(anchor="w")

        def campo_entry():
            entrada = tk.Entry(
                contenedor,
                font=("Segoe UI", 10),
                relief="solid",
                bd=1
            )
            entrada.pack(fill="x", pady=(4, 10), ipady=4)
            return entrada

        etiqueta("Fecha de pago:")
        lbl_fecha = tk.Label(
            contenedor,
            text=fecha_real,
            font=("Consolas", 10, "bold"),
            bg="#f4f6f8",
            fg="#2c3e50",
            relief="solid",
            bd=1,
            anchor="w",
            padx=10
        )
        lbl_fecha.pack(fill="x", pady=(4, 12), ipady=6)

        etiqueta("ID Empresa (UUID):")
        ent_uuid = campo_entry()

        etiqueta("Proyecto asociado:")
        cb_proy = ttk.Combobox(
            contenedor,
            state="readonly",
            font=("Segoe UI", 10)
        )
        cb_proy.pack(fill="x", pady=(4, 10), ipady=4)

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
            else:
                cb_proy.set("")

        ent_uuid.bind("<FocusOut>", cargar_proyectos)
        ent_uuid.bind("<Return>", cargar_proyectos)

        etiqueta("Monto pagado (Q):")
        ent_monto = campo_entry()

        etiqueta("Método de pago:")
        cb_tipo = ttk.Combobox(
            contenedor,
            values=["Efectivo", "Tarjeta", "Transferencia", "Depósito", "Cheque"],
            state="readonly",
            font=("Segoe UI", 10)
        )
        cb_tipo.current(0)
        cb_tipo.pack(fill="x", pady=(4, 14), ipady=4)

        if datos_editar:
            ent_uuid.insert(0, datos_editar[0])
            cargar_proyectos()
            cb_proy.set(datos_editar[1])
            ent_monto.insert(0, str(datos_editar[2]))
            cb_tipo.set(datos_editar[3])

        botones = tk.Frame(contenedor, bg="white")
        botones.pack(fill="x", pady=(4, 0))

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
            uuid_emp = ent_uuid.get().strip()
            proyecto = cb_proy.get().strip()
            monto_txt = ent_monto.get().strip()
            metodo = cb_tipo.get().strip()

            if not uuid_emp:
                messagebox.showwarning("Atención", "Ingrese el ID de empresa.")
                return

            if not proyecto:
                messagebox.showwarning("Atención", "Seleccione un proyecto asociado.")
                return

            if not monto_txt:
                messagebox.showwarning("Atención", "Ingrese el monto del pago.")
                return

            try:
                monto = float(monto_txt)
            except ValueError:
                messagebox.showwarning("Error", "El monto debe ser numérico.")
                return

            if monto <= 0:
                messagebox.showwarning("Error", "El monto debe ser mayor que cero.")
                return

            if id_pago_editar:
                self.ejecutar_db(
                    """
                    UPDATE pagos
                    SET uuid_empresa=?, nombre_proyecto=?, monto=?, metodo_pago=?
                    WHERE id_pago=?
                    """,
                    (
                        uuid_emp,
                        proyecto,
                        monto,
                        metodo,
                        id_pago_editar
                    )
                )

                messagebox.showinfo("Éxito", "Pago actualizado correctamente.")
            else:
                self.ejecutar_db(
                    """
                    INSERT INTO pagos
                    (uuid_empresa, nombre_proyecto, monto, metodo_pago, fecha_pago)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        uuid_emp,
                        proyecto,
                        monto,
                        metodo,
                        fecha_real
                    )
                )

                messagebox.showinfo("Éxito", "Pago guardado correctamente.")

            vp.destroy()

        tk.Button(
            botones,
            text="💾 CONFIRMAR" if not id_pago_editar else "💾 GUARDAR",
            bg="#e67e22",
            fg="white",
            activebackground="#d35400",
            activeforeground="white",
            font=("Segoe UI", 9, "bold"),
            bd=0,
            height=2,
            cursor="hand2",
            command=guardar_pago
        ).pack(side="left", fill="x", expand=True, padx=(0, 5))

        tk.Button(
            botones,
            text="✏️ EDITAR",
            bg="#3498db",
            fg="white",
            activebackground="#2980b9",
            activeforeground="white",
            font=("Segoe UI", 9, "bold"),
            bd=0,
            height=2,
            cursor="hand2",
            command=editar_existente
        ).pack(side="left", fill="x", expand=True, padx=(5, 0))

    def ventana_facturas(self):
        vf = tk.Toplevel(self.root)
        vf.title("Historial de Facturación")
        vf.geometry("980x640")
        vf.configure(bg="#eef2f5")

        header = tk.Frame(vf, bg="#8e44ad", height=78)
        header.pack(fill="x")
        header.pack_propagate(False)

        tk.Label(
            header,
            text="📄 Facturas y Pagos",
            bg="#8e44ad",
            fg="white",
            font=("Segoe UI", 20, "bold")
        ).pack(side="left", padx=28)

        tk.Label(
            header,
            text="Consulta, guarda o imprime comprobantes de pago",
            bg="#8e44ad",
            fg="#f4e9fb",
            font=("Segoe UI", 10)
        ).pack(side="left", padx=8)

        contenedor = tk.Frame(vf, bg="#eef2f5")
        contenedor.pack(fill="both", expand=True, padx=22, pady=20)

        barra = tk.Frame(
            contenedor,
            bg="white",
            padx=14,
            pady=12,
            highlightthickness=1,
            highlightbackground="#d8dee4"
        )
        barra.pack(fill="x", pady=(0, 14))

        tk.Label(
            barra,
            text="Buscar:",
            bg="white",
            fg="#2c3e50",
            font=("Segoe UI", 10, "bold")
        ).pack(side="left", padx=(0, 8))

        ent_buscar = tk.Entry(
            barra,
            font=("Segoe UI", 10),
            relief="solid",
            bd=1,
            width=34
        )
        ent_buscar.pack(side="left", ipady=5, padx=(0, 12))

        tabla_card = tk.Frame(
            contenedor,
            bg="white",
            padx=14,
            pady=14,
            highlightthickness=1,
            highlightbackground="#d8dee4"
        )
        tabla_card.pack(fill="both", expand=True)

        tk.Label(
            tabla_card,
            text="Pagos registrados",
            bg="white",
            fg="#2c3e50",
            font=("Segoe UI", 13, "bold")
        ).pack(anchor="w", pady=(0, 10))

        tabla_frame = tk.Frame(tabla_card, bg="white")
        tabla_frame.pack(fill="both", expand=True)

        cols = ("ID", "Empresa (UUID)", "Proyecto", "Monto", "Método", "Fecha")

        scroll_y = ttk.Scrollbar(tabla_frame, orient="vertical")
        scroll_x = ttk.Scrollbar(tabla_frame, orient="horizontal")

        tree = ttk.Treeview(
            tabla_frame,
            columns=cols,
            show="headings",
            yscrollcommand=scroll_y.set,
            xscrollcommand=scroll_x.set
        )

        scroll_y.config(command=tree.yview)
        scroll_x.config(command=tree.xview)

        for c in cols:
            tree.heading(c, text=c)

        tree.column("ID", width=70, anchor="center", stretch=False)
        tree.column("Empresa (UUID)", width=170, anchor="center", stretch=False)
        tree.column("Proyecto", width=260, anchor="w", stretch=False)
        tree.column("Monto", width=120, anchor="center", stretch=False)
        tree.column("Método", width=130, anchor="center", stretch=False)
        tree.column("Fecha", width=170, anchor="center", stretch=False)

        tree.grid(row=0, column=0, sticky="nsew")
        scroll_y.grid(row=0, column=1, sticky="ns")
        scroll_x.grid(row=1, column=0, sticky="ew")

        tabla_frame.grid_rowconfigure(0, weight=1)
        tabla_frame.grid_columnconfigure(0, weight=1)

        botones = tk.Frame(contenedor, bg="#eef2f5")
        botones.pack(fill="x", pady=(14, 0))

        def obtener_datos():
            return self.obtener_lista_db(
                """
                SELECT id_pago, uuid_empresa, nombre_proyecto, monto, metodo_pago, fecha_pago
                FROM pagos
                ORDER BY id_pago DESC
                """
            )

        def cargar_datos(event=None):
            texto = ent_buscar.get().strip().lower()

            for item in tree.get_children():
                tree.delete(item)

            for d in obtener_datos():
                fila_texto = " ".join(str(x).lower() for x in d)

                if texto and texto not in fila_texto:
                    continue

                id_pago, uuid_emp, proyecto, monto, metodo, fecha = d
                tree.insert(
                    "",
                    "end",
                    values=(
                        id_pago,
                        uuid_emp,
                        proyecto,
                        f"Q {float(monto):,.2f}",
                        metodo,
                        fecha
                    )
                )

        def obtener_pago_seleccionado():
            item = tree.selection()

            if not item:
                messagebox.showwarning(
                    "Atención",
                    "Selecciona una factura."
                )
                return None

            valores = tree.item(item, "values")
            id_pago = valores[0]

            datos = self.obtener_lista_db(
                """
                SELECT id_pago, uuid_empresa, nombre_proyecto, monto, metodo_pago, fecha_pago
                FROM pagos
                WHERE id_pago=?
                """,
                (id_pago,)
            )

            return datos[0] if datos else None

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

            messagebox.showinfo("Éxito", f"Factura guardada en:\n{ruta}")

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
                messagebox.showinfo("Impresión", "Factura enviada a imprimir.")
            except Exception as e:
                messagebox.showerror(
                    "Error",
                    f"No se pudo imprimir automáticamente:\n{e}\n\nArchivo generado:\n{ruta_temp}"
                )

        def ver_factura():
            pago = obtener_pago_seleccionado()

            if not pago:
                return

            preview = tk.Toplevel(vf)
            preview.title("Vista previa de factura")
            preview.geometry("520x500")
            preview.configure(bg="#eef2f5")

            tk.Label(
                preview,
                text="Vista previa de factura",
                bg="#eef2f5",
                fg="#2c3e50",
                font=("Segoe UI", 15, "bold")
            ).pack(pady=(18, 8))

            txt = tk.Text(
                preview,
                font=("Consolas", 10),
                wrap="word",
                relief="solid",
                bd=1
            )
            txt.pack(fill="both", expand=True, padx=20, pady=12)
            txt.insert("1.0", texto_factura(pago))
            txt.config(state="disabled")

        def boton_accion(texto, color, comando):
            tk.Button(
                botones,
                text=texto,
                command=comando,
                bg=color,
                fg="white",
                activebackground=color,
                activeforeground="white",
                font=("Segoe UI", 10, "bold"),
                bd=0,
                height=2,
                cursor="hand2"
            ).pack(side="left", fill="x", expand=True, padx=5)

        boton_accion("👁 Vista previa", "#34495e", ver_factura)
        boton_accion("💾 Guardar factura", "#2ecc71", guardar_factura)
        boton_accion("🖨 Imprimir factura", "#8e44ad", imprimir_factura)
        boton_accion("🔄 Actualizar", "#3498db", cargar_datos)

        ent_buscar.bind("<KeyRelease>", cargar_datos)

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
                "Antes de continuar se creará un respaldo de seguridad del estado actual.\n\n"
                "Deseas continuar?"
            )

            if not confirmar:
                return

            try:
                self.crear_respaldo_automatico()
                self.restaurar_archivo_respaldo(ruta)
                messagebox.showinfo(
                    "Restauración completa",
                    "Los datos fueron restaurados. Cierra y abre de nuevo el programa para cargar todo correctamente."
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
            text="Consejo: haz un respaldo manual al terminar cada dia de trabajo importante.",
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