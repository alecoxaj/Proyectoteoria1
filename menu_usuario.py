import tkinter as tk
from soporte import ventana_soporte
from ajustes import ventana_ajustes
from modo_tema import activar_modo_oscuro, activar_modo_claro

def crear_menu_usuario(self, header, info_user):
    menu_usuario = tk.Menubutton(header, text=info_user, bg="#34495e", fg="#ecf0f1",
                                 font=("Segoe UI", 10), relief="flat", activebackground="#34495e")
    menu_usuario.pack(side="right", padx=30)

    menu = tk.Menu(menu_usuario, tearoff=0)

    menu.add_command(label="⚙️ Ajustes", command=lambda: ventana_ajustes(self))
    menu.add_command(label="📞 Soporte técnico", command=lambda: ventana_soporte(self))
    menu.add_separator()
    menu.add_command(label="🌙 Modo oscuro", command=lambda: activar_modo_oscuro(self))
    menu.add_command(label="☀️ Modo claro", command=lambda: activar_modo_claro(self))
    menu.add_separator()
    menu.add_command(label="Cerrar sesión", command=self.pantalla_login)

    menu_usuario.config(menu=menu)


