import tkinter as tk
from tkinter import messagebox
import time

# 1) CLASE QUEUE (Implementación propia obligatoria)
class Queue:
    def __init__(self):
        self.items = []

    def enqueue(self, item):
        self.items.insert(0, item)

    def dequeue(self):
        return self.items.pop() if not self.is_empty() else None

    def is_empty(self):
        return len(self.items) == 0

    def size(self):
        return len(self.items)

# 2) CLASE PRINTTASK
class PrintTask:
    def __init__(self, id_trabajo, paginas, momento_llegada):
        self.id = id_trabajo
        self.paginas = paginas
        self.llegada = momento_llegada # Segundo en que se creó

# 3) CLASE PRINTER
class Printer:
    def __init__(self, paginas_por_minuto):
        self.tasa_velocidad = paginas_por_minuto
        self.tarea_actual = None
        self.tiempo_restante = 0

    def esta_ocupada(self):
        return self.tarea_actual is not None

    def iniciar_proximo(self, nueva_tarea):
        self.tarea_actual = nueva_tarea
        # Simulación: cada página tarda (60 / tasa) segundos
        self.tiempo_restante = nueva_tarea.paginas * (60 / self.tasa_velocidad)

# 5) INTERFAZ Y LÓGICA DE SIMULACIÓN
class SimuladorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Simulación de Cola de Impresión")
        self.root.geometry("500x600")

        # Inicialización de lógica
        self.cola_impresion = Queue()
        self.impresora = Printer(20) # 20 páginas por minuto
        self.reloj = 0
        self.id_contador = 1
        
        # Métricas
        self.tiempos_espera = []
        self.max_tamano_cola = 0

        # --- UI ---
        tk.Label(root, text="Simulador de Impresora", font=("Arial", 16, "bold")).pack(pady=10)
        
        # Entrada
        frame_input = tk.Frame(root)
        frame_input.pack(pady=5)
        tk.Label(frame_input, text="Páginas:").pack(side=tk.LEFT)
        self.entry_paginas = tk.Entry(frame_input, width=10)
        self.entry_paginas.pack(side=tk.LEFT, padx=5)
        
        tk.Button(root, text="Enviar Trabajo", command=self.agregar_trabajo, bg="lightblue").pack(pady=5)

        # Monitor
        self.lbl_reloj = tk.Label(root, text="Tiempo: 0s", font=("Courier", 12))
        self.lbl_reloj.pack()

        self.lista_visual = tk.Listbox(root, width=50, height=8)
        self.lista_visual.pack(pady=10)

        self.lbl_estado = tk.Label(root, text="Estado: Libre", fg="green", font=("Arial", 10, "bold"))
        self.lbl_estado.pack()

        # Reporte
        self.txt_reporte = tk.Text(root, height=8, width=55, state=tk.DISABLED, bg="#f0f0f0")
        self.txt_reporte.pack(pady=10)

        # Iniciar bucle de tiempo
        self.actualizar_reloj()

    def agregar_trabajo(self):
        try:
            paginas = int(self.entry_paginas.get())
            if paginas <= 0: raise ValueError
            
            nueva_tarea = PrintTask(self.id_contador, paginas, self.reloj)
            self.cola_impresion.enqueue(nueva_tarea)
            
            self.id_contador += 1
            self.entry_paginas.delete(0, tk.END)
            self.actualizar_lista()
        except ValueError:
            messagebox.showerror("Error", "Ingrese un número de páginas válido (mayor a 0).")

    def actualizar_reloj(self):
        self.reloj += 1
        self.lbl_reloj.config(text=f"Tiempo de simulación: {self.reloj}s")

        # Lógica de la impresora
        if self.impresora.esta_ocupada():
            self.impresora.tiempo_restante -= 1
            if self.impresora.tiempo_restante <= 0:
                self.impresora.tarea_actual = None
                self.lbl_estado.config(text="Estado: Libre", fg="green")
        
        # Si está libre, intentar tomar el siguiente
        if not self.impresora.esta_ocupada() and not self.cola_impresion.is_empty():
            tarea = self.cola_impresion.dequeue()
            
            # Cálculo de espera (Métrica)
            espera = self.reloj - tarea.llegada
            self.tiempos_espera.append(espera)
            
            self.impresora.iniciar_proximo(tarea)
            self.lbl_estado.config(text=f"Imprimiendo Trabajo #{tarea.id}...", fg="red")
            self.actualizar_lista()

        # Actualizar máximo tamaño de cola
        if self.cola_impresion.size() > self.max_tamano_cola:
            self.max_tamano_cola = self.cola_impresion.size()

        self.mostrar_metricas()
        self.root.after(1000, self.actualizar_reloj) # Simular 1 segundo real

    def actualizar_lista(self):
        self.lista_visual.delete(0, tk.END)
        # Mostramos los items (copia temporal para visualización)
        for t in reversed(self.cola_impresion.items):
            self.lista_visual.insert(tk.END, f"ID: {t.id} | Páginas: {t.paginas} | Llegó en: {t.llegada}s")

    def mostrar_metricas(self):
        self.txt_reporte.config(state=tk.NORMAL)
        self.txt_reporte.delete(1.0, tk.END)
        
        procesados = len(self.tiempos_espera)
        promedio = sum(self.tiempos_espera) / procesados if procesados > 0 else 0
        max_e = max(self.tiempos_espera) if procesados > 0 else 0
        
        reporte = (
            f"--- MÉTRICAS ---\n"
            f"Trabajos procesados: {procesados}\n"
            f"Tiempo promedio de espera: {promedio:.2f}s\n"
            f"Máximo tiempo de espera: {max_e}s\n"
            f"Tamaño máximo de la cola: {self.max_tamano_cola}"
        )
        self.txt_reporte.insert(tk.END, reporte)
        self.txt_reporte.config(state=tk.DISABLED)

if __name__ == "__main__":
    root = tk.Tk()
    app = SimuladorApp(root)
    root.mainloop()