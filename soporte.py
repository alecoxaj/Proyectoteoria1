import tkinter as tk

def ventana_soporte(self):
    v = tk.Toplevel(self.root)
    v.title("📞 Soporte Técnico")
    v.geometry("350x250")
    v.configure(bg="white")

    tk.Label(v, text="SOPORTE TÉCNICO", font=("Segoe UI", 14, "bold"), bg="white").pack(pady=20)

    tk.Label(v, text="📱 +502 4560-7604", bg="white").pack(pady=5)
    tk.Label(v, text="📱 +502 4135-7899", bg="white").pack(pady=5)
    tk.Label(v, text="📱 +502 3067-8267", bg="white").pack(pady=5)