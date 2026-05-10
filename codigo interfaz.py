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
        self.root.geometry("1100x850")
        self.root.configure(bg="#f4f7f6")

        # Ruta de la base de datos
        ruta_carpeta = os.path.dirname(os.path.abspath(__file__))
        self.ruta_db = os.path.join(ruta_carpeta, "gestion_proyectos.db")

        # Inicializar tablas necesarias
        self.inicializar_db_formal()
        self.configurar_estilos()

        self.usuario_actual = None
        self.rol_actual = None

        # Variables de publicidad
        self.img_original = None
        self.img_tk = None
        self.path_actual = ""

        self.pantalla_login()

    def inicializar_db_formal(self):
        conn = sqlite3.connect(self.ruta_db)
        c = conn.cursor()

        c.execute('''CREATE TABLE IF NOT EXISTS usuarios 
                     (id_usuario INTEGER PRIMARY KEY AUTOINCREMENT, 
                      nombre_completo TEXT, usuario_login TEXT UNIQUE, 
                      password TEXT, rol TEXT)''')

        c.execute('''CREATE TABLE IF NOT EXISTS clientes 
                     (id_cliente INTEGER PRIMARY KEY AUTOINCREMENT, 
                      nombre_empresa TEXT UNIQUE NOT NULL, 
                      telefono_referido TEXT, 
                      correo TEXT, 
                      direccion_empresa TEXT,
                      uuid_empresa TEXT UNIQUE)''')

        c.execute('''CREATE TABLE IF NOT EXISTS publicidad 
                     (id_pub INTEGER PRIMARY KEY AUTOINCREMENT, 
                      uuid_empresa TEXT, 
                      nombre_archivo TEXT, 
                      estado TEXT, 
                      fecha TEXT)''')

        c.execute('''CREATE TABLE IF NOT EXISTS proyectos 
                     (id_proyecto INTEGER PRIMARY KEY AUTOINCREMENT,
                      id_cliente INTEGER,
                      nombre TEXT NOT NULL,
                      fecha_inicio TEXT,
                      estado TEXT,
                      FOREIGN KEY (id_cliente) REFERENCES clientes (id_cliente))''')

        c.execute('''CREATE TABLE IF NOT EXISTS mensajes 
                     (id_mensaje INTEGER PRIMARY KEY AUTOINCREMENT, 
                      remitente TEXT, 
                      contenido TEXT, 
                      fecha_hora TEXT)''')

        c.execute("SELECT count(*) FROM usuarios")
        if c.fetchone()[0] == 0:
            c.execute("INSERT INTO usuarios (nombre_completo, usuario_login, password, rol) VALUES (?,?,?,?)",
                      ('Alejandro Coxaj', 'alejandro', 'prog123', 'Programador'))

        conn.commit()
        conn.close()

    def configurar_estilos(self):
        style = ttk.Style()
        style.theme_use("clam")
        self.root.option_add("*Font", "SegoeUI 10")
        style.configure("Treeview", rowheight=25)

    def obtener_lista_db(self, consulta, params=()):
        try:
            conn = sqlite3.connect(self.ruta_db)
            c = conn.cursor()
            c.execute(consulta, params)
            datos = c.fetchall()
            conn.close()
            return datos
        except:
            return []

    def limpiar_pantalla(self):
        for widget in self.root.winfo_children(): widget.destroy()

    def pantalla_login(self):
        self.limpiar_pantalla()
        bg_frame = tk.Frame(self.root, bg="#2c3e50")
        bg_frame.place(relwidth=1, relheight=1)

        login_card = tk.Frame(self.root, bg="white", padx=40, pady=40, highlightthickness=1,
                              highlightbackground="#dee2e6")
        login_card.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(login_card, text="🔐 INICIO DE SESIÓN", font=("Segoe UI", 18, "bold"), bg="white", fg="#2c3e50").pack(
            pady=(0, 20))

        usuarios_db = self.obtener_lista_db("SELECT usuario_login FROM usuarios")
        lista_nombres = [u[0] for u in usuarios_db]

        tk.Label(login_card, text="Usuario:", bg="white", fg="#7f8c8d").pack(anchor="w")
        user_c = ttk.Combobox(login_card, values=lista_nombres, state="readonly", width=28)
        if lista_nombres: user_c.current(0)
        user_c.pack(pady=(0, 15))

        tk.Label(login_card, text="Contraseña:", bg="white", fg="#7f8c8d").pack(anchor="w")
        pass_e = tk.Entry(login_card, font=("Segoe UI", 11), width=30, bd=1, relief="solid", show="*")
        pass_e.pack(pady=(0, 25))

        def ejecutar_login():
            res = self.obtener_lista_db(
                "SELECT nombre_completo, rol FROM usuarios WHERE usuario_login=? AND password=?",
                (user_c.get(), pass_e.get()))
            if res:
                self.usuario_actual, self.rol_actual = res[0]
                self.menu_principal()
            else:
                messagebox.showerror("Error", "Usuario o contraseña incorrecta")

        tk.Button(login_card, text="ENTRAR", bg="#1abc9c", fg="white", font=("Segoe UI", 10, "bold"), bd=0, width=25,
                  height=2, command=ejecutar_login).pack()

    def menu_principal(self):
        self.limpiar_pantalla()
        header = tk.Frame(self.root, bg="#34495e", height=70)
        header.pack(fill="x")

        tk.Label(header, text="ESPACIO CREATIVO 🖥️", fg="#ecf0f1", bg="#34495e", font=("Segoe UI", 16, "bold")).pack(
            side="left", padx=30, pady=20)

        btn_chat = tk.Button(header, text="📬 Mensajes", bg="#e74c3c", fg="white", font=("Segoe UI", 9, "bold"), bd=0,
                             padx=15, command=self.ventana_comunicacion)
        btn_chat.pack(side="right", padx=10, pady=20)

        info_user = f"👤 {self.usuario_actual} | 🛠️ {self.rol_actual}"
        tk.Label(header, text=info_user, fg="#bdc3c7", bg="#34495e", font=("Segoe UI", 10)).pack(side="right", padx=20)

        container = tk.Frame(self.root, bg="#f4f7f6")
        container.pack(expand=True, fill="both", padx=50, pady=20)

        modulos = [
            ("Registrar Publicidad", "#3498db", "👥", self.ventana_registrar_cliente_formal, "Ambos"),
            ("Crear Proyecto", "#2ecc71", "➕", self.ventana_crear_proyecto, "Ambos"),
            ("Historial Pro", "#9b59b6", "📋", self.ventana_historial, "Ambos"),
            ("Publicidad (Editor)", "#f1c40f", "🎨", self.ventana_publicidad_editor, "Ambos"),
            ("Continuar", "#e74c3c", "🚀", self.ventana_continuar_proyecto, "Ambos"),
            ("Pagos", "#e67e22", "💰", self.ventana_pagos, "Programador"),
            ("Facturas", "#9b59b6", "📋", self.ventana_facturas, "Ambos"),
            ("Portal ID", "#34495e", "🆔", self.ventana_portal_empresa, "Ambos")
        ]

        col_count, row_count = 0, 0
        for texto, color, icono, cmd, permiso in modulos:
            if permiso == "Ambos" or self.rol_actual == "Programador":
                card = tk.Frame(container, bg="white", padx=20, pady=20, highlightbackground="#dee2e6",
                                highlightthickness=1)
                card.grid(row=row_count, column=col_count, padx=15, pady=15)
                tk.Label(card, text=icono, font=("Segoe UI", 35), bg="white", fg=color).pack()
                tk.Label(card, text=texto.upper(), font=("Segoe UI", 10, "bold"), bg="white").pack(pady=10)
                tk.Button(card, text="ACCEDER", bg=color, fg="white", font=("Segoe UI", 8, "bold"), width=15,
                          command=cmd).pack()
                col_count += 1
                if col_count > 3:
                    col_count = 0
                    row_count += 1

        btn_logout = tk.Button(self.root, text="❌ CERRAR SESIÓN", font=("Segoe UI", 10, "bold"),
                               bg="#95a5a6", fg="white", bd=0, padx=25, pady=12, command=self.pantalla_login)
        btn_logout.pack(side="bottom", pady=30)

    def ventana_registrar_cliente_formal(self):
        v = tk.Toplevel(self.root)
        v.title("Registrar Publicidad (Empresa)")
        v.geometry("450x650")
        v.configure(bg="white")

        tk.Label(v, text="REGISTRAR PUBLICIDAD", font=("Segoe UI", 16, "bold"), bg="white", fg="#3498db").pack(pady=30)
        f = tk.Frame(v, bg="white", padx=40)
        f.pack(fill="both")

        tk.Label(f, text="🏢  Nombre de la Empresa:", bg="white").pack(anchor="w")
        nom_e = tk.Entry(f, relief="solid", bd=1);
        nom_e.pack(fill="x", pady=(5, 15))

        tk.Label(f, text="📞  Número Telefónico Referido:", bg="white").pack(anchor="w")
        tel_e = tk.Entry(f, relief="solid", bd=1);
        tel_e.pack(fill="x", pady=(5, 15))

        tk.Label(f, text="✉️  Correo Electrónico:", bg="white").pack(anchor="w")
        cor_e = tk.Entry(f, relief="solid", bd=1);
        cor_e.pack(fill="x", pady=(5, 15))

        tk.Label(f, text="📍  Dirección de la Empresa:", bg="white").pack(anchor="w")
        dir_e = tk.Entry(f, relief="solid", bd=1);
        dir_e.pack(fill="x", pady=(5, 30))

        def guardar():
            nombre = nom_e.get().strip()
            if not nombre:
                messagebox.showwarning("Atención", "El nombre de la empresa es obligatorio.")
                return

            existe = self.obtener_lista_db("SELECT nombre_empresa FROM clientes WHERE nombre_empresa=?", (nombre,))
            if existe:
                messagebox.showerror("Error", f"La empresa '{nombre}' ya está registrada.")
                return

            id_personal = "PUB-" + str(uuid.uuid4())[:8].upper()
            try:
                conn = sqlite3.connect(self.ruta_db)
                c = conn.cursor()
                c.execute(
                    "INSERT INTO clientes (nombre_empresa, telefono_referido, correo, direccion_empresa, uuid_empresa) VALUES (?,?,?,?,?)",
                    (nombre, tel_e.get(), cor_e.get(), dir_e.get(), id_personal))
                conn.commit()
                conn.close()
                messagebox.showinfo("Éxito", f"Empresa registrada.\nID PERSONAL: {id_personal}")
                v.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo guardar: {e}")

        tk.Button(v, text="Guardar Registro", bg="#2ecc71", fg="white", font=("Segoe UI", 11, "bold"), relief="flat",
                  height=2, width=30, command=guardar).pack(pady=10)

    def ventana_crear_proyecto(self):
        v = tk.Toplevel(self.root)
        v.title("Crear Nuevo Proyecto")
        v.geometry("450x550")
        v.configure(bg="white")

        tk.Label(v, text="NUEVO PROYECTO", font=("Segoe UI", 16, "bold"), bg="white", fg="#2ecc71").pack(pady=30)
        f = tk.Frame(v, bg="white", padx=40)
        f.pack(fill="both")

        tk.Label(f, text="Seleccionar Empresa:", bg="white").pack(anchor="w")
        clientes_db = self.obtener_lista_db("SELECT id_cliente, nombre_empresa FROM clientes")
        dict_clientes = {nombre: id_cli for id_cli, nombre in clientes_db}
        cb_clientes = ttk.Combobox(f, values=list(dict_clientes.keys()), state="readonly")
        cb_clientes.pack(fill="x", pady=(5, 15))

        tk.Label(f, text="Nombre del Proyecto:", bg="white").pack(anchor="w")
        ent_nombre_p = tk.Entry(f, relief="solid", bd=1)
        ent_nombre_p.pack(fill="x", pady=(5, 15))

        tk.Label(f, text="Fecha de Inicio:", bg="white").pack(anchor="w")
        ent_fecha = DateEntry(f, width=12, background='darkblue', foreground='white', borderwidth=2,
                              date_pattern='dd/mm/yyyy')
        ent_fecha.pack(fill="x", pady=(5, 15))

        tk.Label(f, text="Estado Inicial:", bg="white").pack(anchor="w")
        cb_estado = ttk.Combobox(f, values=["En Espera", "Trabajando", "Finalizado"], state="readonly")
        cb_estado.current(0)
        cb_estado.pack(fill="x", pady=(5, 30))

        def guardar_proy():
            emp, nom = cb_clientes.get(), ent_nombre_p.get().strip()
            if not emp or not nom: return messagebox.showwarning("Error", "Complete los campos.")
            try:
                conn = sqlite3.connect(self.ruta_db)
                conn.execute("INSERT INTO proyectos (id_cliente, nombre, fecha_inicio, estado) VALUES (?,?,?,?)",
                             (dict_clientes[emp], nom, ent_fecha.get(), cb_estado.get()))
                conn.commit()
                conn.close()
                messagebox.showinfo("Éxito", "Proyecto guardado correctamente.")
                v.destroy()
            except Exception as e:
                messagebox.showerror("Error", str(e))

        tk.Button(v, text="REGISTRAR PROYECTO", bg="#2ecc71", fg="white", font=("Segoe UI", 11, "bold"), relief="flat",
                  height=2, width=30, command=guardar_proy).pack(pady=10)

    def ventana_historial(self):
        v = tk.Toplevel(self.root)
        v.title("Historial de Proyectos")
        v.geometry("1100x750")
        v.configure(bg="#f4f7f6")

        frame_busqueda = tk.Frame(v, bg="#34495e", pady=15)
        frame_busqueda.pack(fill="x")

        tk.Label(frame_busqueda, text="🆔 BUSCAR POR ID:", fg="white", bg="#34495e", font=("Segoe UI", 9, "bold")).pack(
            side="left", padx=(20, 5))
        ent_id_busq = tk.Entry(frame_busqueda, font=("Consolas", 11), width=15)
        ent_id_busq.pack(side="left", padx=10)

        tk.Label(frame_busqueda, text="📂 NOMBRE PROYECTO:", fg="white", bg="#34495e",
                 font=("Segoe UI", 9, "bold")).pack(side="left", padx=(20, 5))
        ent_nom_busq = tk.Entry(frame_busqueda, font=("Segoe UI", 11), width=20)
        ent_nom_busq.pack(side="left", padx=10)

        cuerpo = tk.Frame(v, bg="white", padx=20, pady=20, highlightthickness=1, highlightbackground="#dee2e6")
        cuerpo.pack(expand=True, fill="both", padx=20, pady=20)

        tk.Label(cuerpo, text="DIRECTORIO DE EMPRESAS", font=("Segoe UI", 11, "bold"), bg="white", fg="#3498db").pack()
        cols_c = ("Empresa", "ID Personal")
        tree_clientes = ttk.Treeview(cuerpo, columns=cols_c, show="headings", height=5)
        for col in cols_c: tree_clientes.heading(col, text=col)
        tree_clientes.pack(fill="x", pady=10)

        tk.Label(cuerpo, text="▼ REGISTROS DE PROYECTOS ▼", font=("Segoe UI", 10, "bold"),
                 bg="white", fg="#2c3e50").pack(pady=(10, 5))
        cols_p = ("Proyecto", "Fecha Inicio", "Estado", "Empresa Relacionada")
        tree_proyectos = ttk.Treeview(cuerpo, columns=cols_p, show="headings")
        for col in cols_p: tree_proyectos.heading(col, text=col)
        tree_proyectos.pack(expand=True, fill="both")

        def actualizar_tablas(event=None):
            for i in tree_clientes.get_children(): tree_clientes.delete(i)
            id_busc = ent_id_busq.get().strip()
            query_c = "SELECT nombre_empresa, uuid_empresa FROM clientes"
            params_c = ()
            if id_busc:
                query_c += " WHERE uuid_empresa LIKE ?"
                params_c = (f"%{id_busc}%",)
            for d in self.obtener_lista_db(query_c, params_c): tree_clientes.insert("", "end", values=d)

            for i in tree_proyectos.get_children(): tree_proyectos.delete(i)
            nom_busc = ent_nom_busq.get().strip()

            query_p = """SELECT p.nombre, p.fecha_inicio, p.estado, c.nombre_empresa 
                         FROM proyectos p JOIN clientes c ON p.id_cliente = c.id_cliente 
                         WHERE 1=1"""
            params_p = []
            if id_busc:
                query_p += " AND c.uuid_empresa LIKE ?"
                params_p.append(f"%{id_busc}%")
            if nom_busc:
                query_p += " AND p.nombre LIKE ?"
                params_p.append(f"%{nom_busc}%")

            for p in self.obtener_lista_db(query_p, tuple(params_p)):
                tree_proyectos.insert("", "end", values=p)

        ent_id_busq.bind("<KeyRelease>", actualizar_tablas)
        ent_nom_busq.bind("<KeyRelease>", actualizar_tablas)

        def al_seleccionar_cliente(event):
            item = tree_clientes.selection()
            if item:
                uuid_sel = tree_clientes.item(item)['values'][1]
                ent_id_busq.delete(0, tk.END)
                ent_id_busq.insert(0, uuid_sel)
                actualizar_tablas()

        tree_clientes.bind("<<TreeviewSelect>>", al_seleccionar_cliente)
        actualizar_tablas()

    def ventana_portal_empresa(self):
        v = tk.Toplevel(self.root)
        v.title("Portal ID de Empresas")
        v.geometry("600x400")
        tk.Label(v, text="🆔 DIRECTORIO DE IDENTIFICADORES", font=("Segoe UI", 14, "bold"), pady=20).pack()
        cols = ("Empresa", "UUID / ID Personal")
        tree = ttk.Treeview(v, columns=cols, show="headings")
        tree.heading("Empresa", text="Empresa");
        tree.heading("UUID / ID Personal", text="UUID Personal")
        tree.pack(expand=True, fill="both", padx=20, pady=20)
        for d in self.obtener_lista_db("SELECT nombre_empresa, uuid_empresa FROM clientes"):
            tree.insert("", "end", values=d)

    def ventana_publicidad_editor(self, id_editar=None):
        v = tk.Toplevel(self.root)
        v.title("Editor de Publicidad")
        v.geometry("1000x750")
        v.configure(bg="#2c3e50")

        panel_datos = tk.Frame(v, bg="white", pady=10)
        panel_datos.pack(fill="x")

        tk.Label(panel_datos, text="ID Empresa (UUID):", bg="white").pack(side="left", padx=5)
        ent_uuid = tk.Entry(panel_datos, font=("Consolas", 11), relief="solid", width=15)
        ent_uuid.pack(side="left", padx=5)

        tk.Label(panel_datos, text="Proyecto:", bg="white").pack(side="left", padx=5)
        cb_proyectos = ttk.Combobox(panel_datos, state="readonly", width=20)
        cb_proyectos.pack(side="left", padx=5)

        tk.Label(panel_datos, text="Estado:", bg="white").pack(side="left", padx=5)
        cb_estado = ttk.Combobox(panel_datos, values=["Trabajando", "En Espera", "Finalizado"], state="readonly",
                                 width=12)
        cb_estado.current(1)
        cb_estado.pack(side="left", padx=5)

        canvas = tk.Canvas(v, bg="#ecf0f1", width=600, height=450)
        canvas.pack(pady=20)

        def cargar_proyectos_de_empresa(event=None):
            uuid_busqueda = ent_uuid.get().strip()

            proys = self.obtener_lista_db(
                "SELECT p.nombre FROM proyectos p JOIN clientes c ON p.id_cliente = c.id_cliente WHERE c.uuid_empresa=?",
                (uuid_busqueda,))
            lista = [p[0] for p in proys]
            cb_proyectos['values'] = lista
            if lista:
                cb_proyectos.current(0)
            else:
                cb_proyectos.set("Sin proyectos")

        ent_uuid.bind("<FocusOut>", cargar_proyectos_de_empresa)

        def actualizar_preview():
            if self.img_original:
                img_copy = self.img_original.copy()
                img_copy.thumbnail((600, 450))
                self.img_tk = ImageTk.PhotoImage(img_copy)
                canvas.delete("all")
                canvas.create_image(300, 225, image=self.img_tk)

        if id_editar:
            ent_uuid.insert(0, id_editar)
            cargar_proyectos_de_empresa()
            datos = self.obtener_lista_db(
                "SELECT nombre_archivo, estado FROM publicidad WHERE uuid_empresa=? ORDER BY id_pub DESC LIMIT 1",
                (id_editar,))
            if datos:
                self.path_actual = datos[0][0]
                cb_estado.set(datos[0][1])
                if os.path.exists(self.path_actual):
                    self.img_original = Image.open(self.path_actual)
                    actualizar_preview()

        def cargar_foto():
            path = filedialog.askopenfilename(filetypes=[("Imágenes", "*.jpg *.png *.jpeg")])
            if path:
                self.img_original = Image.open(path)
                self.path_actual = path
                actualizar_preview()

        def efektos(tipo):
            if not self.img_original: return
            if tipo == "crop":
                w, h = self.img_original.size
                self.img_original = self.img_original.crop((w * 0.1, h * 0.1, w * 0.9, h * 0.9))
            elif tipo == "gray":
                self.img_original = ImageOps.grayscale(self.img_original)
            actualizar_preview()

        def guardar_db():
            id_emp = ent_uuid.get().strip()
            proy_sel = cb_proyectos.get()
            if not id_emp or not self.img_original or proy_sel == "Sin proyectos":
                return messagebox.showwarning("Atención", "ID, Proyecto y foto requeridos.")

            conn = sqlite3.connect(self.ruta_db)
            conn.execute("INSERT INTO publicidad (uuid_empresa, nombre_archivo, estado, fecha) VALUES (?,?,?,?)",
                         (id_emp, self.path_actual, cb_estado.get(),
                          datetime.now().strftime("%d/%m/%Y")))
            conn.commit()
            conn.close()
            messagebox.showinfo("Éxito", f"Publicidad guardada para el proyecto: {proy_sel}")
            v.destroy()

        btns_f = tk.Frame(v, bg="#2c3e50")
        btns_f.pack(pady=10)
        tk.Button(btns_f, text="📂 SUBIR", command=cargar_foto, bg="#1abc9c", fg="white", width=12).pack(side="left",
                                                                                                        padx=5)
        tk.Button(btns_f, text="✂️ RECORTAR", command=lambda: efektos("crop"), bg="#f39c12", fg="white", width=12).pack(
            side="left", padx=5)
        tk.Button(btns_f, text="🌓 GRIS", command=lambda: efektos("gray"), bg="#95a5a6", fg="white", width=12).pack(
            side="left", padx=5)
        tk.Button(v, text="💾 GUARDAR", command=guardar_db, bg="#3498db", fg="white", height=2, width=20).pack(pady=20)

    def ventana_continuar_proyecto(self):
        v = tk.Toplevel(self.root)
        v.title("Panel de Continuidad de Trabajo")
        v.geometry("950x650")
        v.configure(bg="#f8f9fa")

        header_f = tk.Frame(v, bg="#2c3e50", pady=15)
        header_f.pack(fill="x")
        tk.Label(header_f, text="🚀 GESTIÓN DE TRABAJOS PENDIENTES", fg="white",
                 bg="#2c3e50", font=("Segoe UI", 12, "bold")).pack()

        search_f = tk.Frame(v, bg="#f8f9fa", pady=20)
        search_f.pack(fill="x")
        tk.Label(search_f, text="🔍 Ingrese ID de Empresa o Proyecto:", bg="#f8f9fa",
                 font=("Segoe UI", 10)).pack(side="left", padx=(40, 10))
        ent_id = tk.Entry(search_f, font=("Consolas", 12), width=30, relief="solid", bd=1)
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
            for i in tree.get_children(): tree.delete(i)
            id_b = ent_id.get().strip()
            if not id_b: return

            proy = self.obtener_lista_db(
                "SELECT 'Proyecto', p.nombre, p.estado, p.fecha_inicio, c.uuid_empresa FROM proyectos p "
                "JOIN clientes c ON p.id_cliente = c.id_cliente "
                "WHERE c.uuid_empresa LIKE ? OR p.nombre LIKE ?", (f"%{id_b}%", f"%{id_b}%"))

            pub = self.obtener_lista_db(
                "SELECT 'Publicidad', nombre_archivo, estado, fecha, uuid_empresa FROM publicidad "
                "WHERE uuid_empresa LIKE ? OR nombre_archivo LIKE ?", (f"%{id_b}%", f"%{id_b}%"))

            for r in (proy + pub):
                tree.insert("", "end", values=r)

        def ejecutar_accion(event):
            item_sel = tree.selection()
            if not item_sel: return
            tipo, nombre, estado, fecha, uuid_e = tree.item(item_sel, "values")

            if estado == "Finalizado":
                self.mostrar_vista_previa_final(nombre, tipo)
            else:
                v.destroy()
                if tipo == "Publicidad":
                    self.ventana_publicidad_editor(id_editar=uuid_e)
                else:
                    messagebox.showinfo("Proyectos", f"Redirigiendo al módulo de Proyectos para: {nombre}")

        ent_id.bind("<KeyRelease>", buscar)
        tree.bind("<Double-1>", ejecutar_accion)

        tk.Label(v, text="💡 Tip: Doble clic sobre un registro para continuar editando o ver resultado.",
                 fg="#7f8c8d", bg="#f8f9fa", font=("Segoe UI", 9, "italic")).pack(pady=10)

    def mostrar_vista_previa_final(self, nombre_recurso, tipo):
        vf = tk.Toplevel(self.root)
        vf.title(f"Resultado Final - {nombre_recurso}")
        vf.geometry("600x500")
        vf.configure(bg="white")

        tk.Label(vf, text=f"ARCHIVO FINALIZADO: {nombre_recurso}",
                 font=("Segoe UI", 12, "bold"), bg="white", pady=20).pack()

        canvas_preview = tk.Canvas(vf, bg="#f1f2f6", width=500, height=350, highlightthickness=0)
        canvas_preview.pack(pady=10)
        canvas_preview.create_text(250, 175, text="[ VISTA PREVIA DEL TRABAJO ]\n(Imagen cargada desde base de datos)",
                                   justify="center", fill="#95a5a6")

        tk.Button(vf, text="CERRAR VISTA", command=vf.destroy, bg="#e74c3c", fg="white",
                  relief="flat", width=20).pack(pady=10)

    def ventana_comunicacion(self):
        v = tk.Toplevel(self.root);
        v.title("Mensajes")
        chat = tk.Text(v, height=15, state="disabled");
        chat.pack(padx=20, pady=20)
        msj = tk.Entry(v);
        msj.pack(fill="x", padx=20)

        def enviar():
            if msj.get():
                conn = sqlite3.connect(self.ruta_db)
                conn.execute("INSERT INTO mensajes (remitente, contenido, fecha_hora) VALUES (?,?,?)",
                             (self.usuario_actual, msj.get(), datetime.now().strftime("%H:%M")))
                conn.commit();
                conn.close();
                msj.delete(0, tk.END);
                cargar()

        def cargar():
            chat.config(state="normal");
            chat.delete("1.0", tk.END)
            for m in self.obtener_lista_db(
                    "SELECT remitente, contenido, fecha_hora FROM mensajes ORDER BY id_mensaje ASC"):
                chat.insert(tk.END, f"{m[0]} [{m[2]}]: {m[1]}\n")
            chat.config(state="disabled");
            chat.see(tk.END)

        tk.Button(v, text="ENVIAR", command=enviar).pack(pady=10);
        cargar()

    def ventana_pagos(self):
        vp = tk.Toplevel(self.root)
        vp.title("Registro de Pagos")
        vp.geometry("450x550")
        vp.configure(bg="#f4f7f6")

        tk.Label(vp, text="💰 REGISTRAR NUEVO PAGO", font=("Segoe UI", 14, "bold"), bg="#f4f7f6", fg="#e67e22").pack(
            pady=20)

        f = tk.Frame(vp, bg="white", padx=30, pady=20, highlightthickness=1, highlightbackground="#dee2e6")
        f.pack(fill="both", expand=True, padx=20, pady=10)

        # ID de Empresa
        tk.Label(f, text="ID Empresa (UUID):", bg="white").pack(anchor="w")
        ent_uuid = tk.Entry(f, font=("Consolas", 11), relief="solid")
        ent_uuid.pack(fill="x", pady=(0, 15))

        # Proyecto
        tk.Label(f, text="Proyecto Asociado:", bg="white").pack(anchor="w")
        cb_proy = ttk.Combobox(f, state="readonly")
        cb_proy.pack(fill="x", pady=(0, 15))

        def cargar_proyectos(event=None):
            res = self.obtener_lista_db(
                "SELECT p.nombre FROM proyectos p JOIN clientes c ON p.id_cliente = c.id_cliente WHERE c.uuid_empresa=?",
                (ent_uuid.get().strip(),))
            cb_proy['values'] = [p[0] for p in res]
            if res: cb_proy.current(0)

        ent_uuid.bind("<FocusOut>", cargar_proyectos)


        tk.Label(f, text="Monto (Q):", bg="white").pack(anchor="w")
        ent_monto = tk.Entry(f, relief="solid");
        ent_monto.pack(fill="x", pady=(0, 15))

        tk.Label(f, text="Tipo de Pago:", bg="white").pack(anchor="w")
        cb_tipo = ttk.Combobox(f, values=["Efectivo", "Tarjeta"], state="readonly")
        cb_tipo.current(0);
        cb_tipo.pack(fill="x", pady=(0, 15))

        # Fecha Real
        fecha_real = datetime.now().strftime("%d/%m/%Y %H:%M")
        tk.Label(f, text="Fecha de Pago:", bg="white").pack(anchor="w")
        tk.Label(f, text=fecha_real, font=("Consolas", 10), bg="#ecf0f1", relief="sunken", anchor="w").pack(fill="x",
                                                                                                            pady=(0,
                                                                                                                  20))

        def guardar_pago():
            if not cb_proy.get() or not ent_monto.get():
                return messagebox.showwarning("Error", "Faltan datos")

            conn = sqlite3.connect(self.ruta_db)

            conn.execute(
                "CREATE TABLE IF NOT EXISTS pagos (id_pago INTEGER PRIMARY KEY AUTOINCREMENT, uuid_empresa TEXT, nombre_proyecto TEXT, monto REAL, metodo_pago TEXT, fecha_pago TEXT)")
            conn.execute(
                "INSERT INTO pagos (uuid_empresa, nombre_proyecto, monto, metodo_pago, fecha_pago) VALUES (?,?,?,?,?)",
                (ent_uuid.get().strip(), cb_proy.get(), ent_monto.get(), cb_tipo.get(), fecha_real))
            conn.commit();
            conn.close()
            messagebox.showinfo("Éxito", "Pago guardado")
            vp.destroy()

        tk.Button(vp, text="CONFIRMAR PAGO", bg="#e67e22", fg="white", font=("Segoe UI", 10, "bold"), height=2,
                  command=guardar_pago).pack(pady=10)
    def ventana_facturas(self):
        vf = tk.Toplevel(self.root)
        vf.title("Historial de Facturación")
        vf.geometry("800x500")

        tk.Label(vf, text="📄 PAGOS RECIBIDOS / FACTURAS", font=("Segoe UI", 14, "bold"), pady=20).pack()

        cols = ("ID", "Empresa (UUID)", "Proyecto", "Monto", "Método", "Fecha")
        tree = ttk.Treeview(vf, columns=cols, show="headings")
        for c in cols: tree.heading(c, text=c); tree.column(c, width=100)
        tree.pack(fill="both", expand=True, padx=20, pady=20)

        # Cargar datos de la tabla pagos
        datos = self.obtener_lista_db("SELECT * FROM pagos")
        for d in datos:
            tree.insert("", "end", values=d)


if __name__ == "__main__":
    root = tk.Tk()
    app = SistemaGestion(root)
    root.mainloop()