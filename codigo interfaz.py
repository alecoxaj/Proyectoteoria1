import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import os


class SistemaGestion:
    def __init__(self, root):
        self.root = root
        self.root.title("Espacio Creativo v3.0 - Gestión Pro")
        self.root.geometry("1000x650")
        self.root.configure(bg="#f4f7f6")

        ruta_carpeta = os.path.dirname(os.path.abspath(__file__))
        self.ruta_db = os.path.join(ruta_carpeta, "gestion_proyectos.db")

        self.configurar_estilos()
        self.usuario_actual = None
        self.rol_actual = None
        self.pantalla_login()

    def configurar_estilos(self):
        style = ttk.Style()
        style.theme_use("clam")
        self.root.option_add("*Font", "SegoeUI 10")
        self.root.option_add("*Label.Font", "SegoeUI 10")
        self.root.option_add("*Entry.Font", "SegoeUI 10")
        style.configure("TCombobox", fieldbackground="white", background="white")

    def obtener_lista_db(self, consulta):
        try:
            conn = sqlite3.connect(self.ruta_db)
            c = conn.cursor()
            c.execute(consulta)
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

        # OBTENER USUARIOS DE LA BASE DE DATOS (PARA QUE SEA DINÁMICO)
        usuarios_db = self.obtener_lista_db("SELECT nombre_completo FROM usuarios")
        lista_nombres = [u[0] for u in usuarios_db]

        tk.Label(login_card, text="Usuario:", bg="white", fg="#7f8c8d").pack(anchor="w")
        user_c = ttk.Combobox(login_card, values=lista_nombres, state="readonly", width=28)
        if lista_nombres: user_c.current(0)
        user_c.pack(pady=(0, 15))

        tk.Label(login_card, text="Contraseña:", bg="white", fg="#7f8c8d").pack(anchor="w")
        pass_e = tk.Entry(login_card, font=("Segoe UI", 11), width=30, bd=1, relief="solid", show="*")
        pass_e.pack(pady=(0, 25))

        # FUNCIÓN DE LOGGING CORREGIDA
        def ejecutar_login():
            user_sel = user_c.get()
            pass_ingresada = pass_e.get()

            if not user_sel or not pass_ingresada:
                messagebox.showwarning("Aviso", "Complete todos los campos")
                return

            conn = sqlite3.connect(self.ruta_db)
            c = conn.cursor()
            c.execute("SELECT nombre_completo, rol FROM usuarios WHERE nombre_completo=? AND password=?",
                      (user_sel, pass_ingresada))
            resultado = c.fetchone()
            conn.close()

            if resultado:
                self.usuario_actual = resultado[0]
                self.rol_actual = resultado[1]
                self.menu_principal()
            else:
                messagebox.showerror("Error", "Contraseña incorrecta")

        tk.Button(login_card, text="ENTRAR", bg="#1abc9c", fg="white", font=("Segoe UI", 10, "bold"),
                  bd=0, width=25, height=2, command=ejecutar_login).pack()

    def menu_principal(self):
        self.limpiar_pantalla()
        header = tk.Frame(self.root, bg="#34495e", height=70)
        header.pack(fill="x")
        tk.Label(header, text="ESPACIO CREATIVO 🖥️", fg="#ecf0f1", bg="#34495e", font=("Segoe UI", 16, "bold")).pack(
            side="left", padx=30, pady=20)

        info_user = f"👤 {self.usuario_actual} | 🛠️ {self.rol_actual}"
        tk.Label(header, text=info_user, fg="#bdc3c7", bg="#34495e", font=("Segoe UI", 10)).pack(side="right", padx=30)

        container = tk.Frame(self.root, bg="#f4f7f6")
        container.pack(expand=True, fill="both", padx=50, pady=50)

        modulos = [
            ("Registro de Clientes", "#3498db", "👥", self.ventana_clientes, "Programador"),
            ("Registro de Proyectos", "#2ecc71", "⚙️", self.ventana_proyectos, "Ambos"),
            ("Control de Pagos", "#e67e22", "💰", self.ventana_pagos, "Programador")
        ]

        col_count = 0
        for texto, color, icono, cmd, permiso in modulos:
            if permiso == "Ambos" or self.rol_actual == "Programador":
                card = tk.Frame(container, bg="white", padx=30, pady=30, highlightbackground="#dee2e6",
                                highlightthickness=1)
                card.grid(row=0, column=col_count, padx=25)
                tk.Label(card, text=icono, font=("Segoe UI", 40), bg="white", fg=color).pack()
                tk.Label(card, text=texto.upper(), font=("Segoe UI", 11, "bold"), bg="white", fg="#2c3e50").pack(
                    pady=15)
                tk.Button(card, text="ACCEDER", bg=color, fg="white", font=("Segoe UI", 9, "bold"), bd=0, width=18,
                          height=2, command=cmd).pack()
                col_count += 1

        tk.Button(self.root, text="Cerrar Sesión", command=self.pantalla_login, bd=0, fg="#e74c3c", bg="#f4f7f6",
                  font=("Segoe UI", 9, "underline")).pack(side="bottom", pady=20)

    # --- LAS VENTANAS SIGUEN IGUAL (CLIENTES, PROYECTOS, PAGOS) ---
    def ventana_clientes(self):
        v = tk.Toplevel(self.root);
        v.title("👥 Clientes");
        v.geometry("400x500");
        v.configure(bg="white")
        tk.Label(v, text="NUEVO CLIENTE", font=("Segoe UI", 14, "bold"), bg="white", fg="#3498db").pack(pady=20)
        f = tk.Frame(v, bg="white", padx=30);
        f.pack(fill="both")
        tk.Label(f, text="👤 Nombre Completo:", bg="white").pack(anchor="w")
        nom_e = tk.Entry(f, relief="solid");
        nom_e.pack(fill="x", pady=5)
        tk.Label(f, text="📞 Teléfono:", bg="white").pack(anchor="w")
        tel_e = tk.Entry(f, relief="solid");
        tel_e.pack(fill="x", pady=5)
        tk.Label(f, text="✉️ Correo:", bg="white").pack(anchor="w")
        cor_e = tk.Entry(f, relief="solid");
        cor_e.pack(fill="x", pady=5)

        def guardar():
            if not nom_e.get(): return
            try:
                conn = sqlite3.connect(self.ruta_db)
                c = conn.cursor()
                c.execute("INSERT INTO clientes (nombre, telefono, correo) VALUES (?,?,?)",
                          (nom_e.get(), tel_e.get(), cor_e.get()))
                conn.commit();
                conn.close()
                messagebox.showinfo("Éxito", "Guardado");
                v.destroy()
            except Exception as e:
                messagebox.showerror("Error", str(e))

        tk.Button(f, text="Guardar Cliente", bg="#27ae60", fg="white", height=2, command=guardar).pack(fill="x",
                                                                                                       pady=20)

    def ventana_proyectos(self):
        v = tk.Toplevel(self.root);
        v.title("⚙️ Proyectos");
        v.geometry("400x600");
        v.configure(bg="white")
        tk.Label(v, text="NUEVO PROYECTO", font=("Segoe UI", 14, "bold"), bg="white", fg="#2ecc71").pack(pady=20)
        f = tk.Frame(v, bg="white", padx=30);
        f.pack(fill="both")
        clientes_db = self.obtener_lista_db("SELECT id_cliente, nombre FROM clientes")
        dict_clientes = {nombre: id_c for id_c, nombre in clientes_db}
        tk.Label(f, text="👥 Cliente:", bg="white").pack(anchor="w")
        cli_c = ttk.Combobox(f, values=list(dict_clientes.keys()), state="readonly");
        cli_c.pack(fill="x", pady=5)
        tk.Label(f, text="🎬 Nombre:", bg="white").pack(anchor="w")
        nom_e = tk.Entry(f, relief="solid");
        nom_e.pack(fill="x", pady=5)
        tk.Label(f, text="📅 Inicio:", bg="white").pack(anchor="w")
        f_i = tk.Entry(f, relief="solid");
        f_i.pack(fill="x", pady=5)
        tk.Label(f, text="🎁 Fin:", bg="white").pack(anchor="w")
        f_e = tk.Entry(f, relief="solid");
        f_e.pack(fill="x", pady=5)
        tk.Label(f, text="🚥 Estado:", bg="white").pack(anchor="w")
        est_c = ttk.Combobox(f, values=["Pendiente", "En Proceso", "Finalizado"], state="readonly");
        est_c.pack(fill="x", pady=5)

        def guardar():
            if not nom_e.get() or not cli_c.get(): return
            try:
                conn = sqlite3.connect(self.ruta_db)
                c = conn.cursor()
                c.execute(
                    "INSERT INTO proyectos (id_cliente, nombre, fecha_inicio, fecha_fin, estado) VALUES (?,?,?,?,?)",
                    (dict_clientes[cli_c.get()], nom_e.get(), f_i.get(), f_e.get(), est_c.get()))
                conn.commit();
                conn.close()
                messagebox.showinfo("Éxito", "Creado");
                v.destroy()
            except Exception as e:
                messagebox.showerror("Error", str(e))

        tk.Button(f, text="Crear Proyecto", bg="#27ae60", fg="white", height=2, command=guardar).pack(fill="x", pady=20)

    def ventana_pagos(self):
        v = tk.Toplevel(self.root);
        v.title("💰 Pagos");
        v.geometry("400x550");
        v.configure(bg="white")
        tk.Label(v, text="REGISTRO DE PAGO", font=("Segoe UI", 14, "bold"), bg="white", fg="#e67e22").pack(pady=20)
        f = tk.Frame(v, bg="white", padx=30);
        f.pack(fill="both")
        proyectos_db = self.obtener_lista_db("SELECT id_proyecto, nombre FROM proyectos")
        dict_proyectos = {nombre: id_p for id_p, nombre in proyectos_db}
        tk.Label(f, text="🎬 Proyecto:", bg="white").pack(anchor="w")
        pro_c = ttk.Combobox(f, values=list(dict_proyectos.keys()), state="readonly");
        pro_c.pack(fill="x", pady=5)
        tk.Label(f, text="💵 Monto:", bg="white").pack(anchor="w")
        mon_e = tk.Entry(f, relief="solid");
        mon_e.pack(fill="x", pady=5)
        tk.Label(f, text="📅 Fecha:", bg="white").pack(anchor="w")
        fec_e = tk.Entry(f, relief="solid");
        fec_e.pack(fill="x", pady=5)

        def guardar():
            if not mon_e.get(): return
            try:
                conn = sqlite3.connect(self.ruta_db)
                c = conn.cursor()
                c.execute("INSERT INTO pagos (id_proyecto, monto, fecha) VALUES (?,?,?)",
                          (dict_proyectos[pro_c.get()], float(mon_e.get()), fec_e.get()))
                conn.commit();
                conn.close()
                messagebox.showinfo("Éxito", "Pago registrado");
                v.destroy()
            except Exception as e:
                messagebox.showerror("Error", "Monto inválido")

        tk.Button(f, text="Registrar Pago", bg="#e67e22", fg="white", height=2, command=guardar).pack(fill="x", pady=20)


if __name__ == "__main__":
    root = tk.Tk()
    app = SistemaGestion(root)
    root.mainloop()