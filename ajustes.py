import tkinter as tk

def ventana_ajustes(self):
    v = tk.Toplevel(self.root)
    v.title("⚙️ Ajustes")
    v.geometry("300x200")
    v.configure(bg="white")

    tk.Label(v, text="Configuraciones", font=("Segoe UI", 14, "bold"), bg="white").pack(pady=20)
    tk.Label(v, text="Aquí puedes agregar más opciones", bg="white").pack()

    