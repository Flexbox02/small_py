import tkinter as tk
from tkinter import ttk
import time
import threading
import winsound

class SoftPomodoroApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Soft Pomodoro")
        self.root.geometry("400x500")
        self.root.configure(bg="#111")

        self.focus_time = tk.IntVar(value=25)
        self.break_time = tk.IntVar(value=5)
        self.remaining = 0
        self.total = 0
        self.running = False
        self.paused = False
        self.is_focus = True

        self.create_widgets()
        self.animate_circle()

    def create_widgets(self):
        # Canvas principal
        self.canvas = tk.Canvas(self.root, bg="#111", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        # Texto centrado con sombra
        self.time_shadow = self.canvas.create_text(0, 0, text="25:00", fill="#333",font=("Segoe UI Light", 42), anchor="c")
        self.time_text = self.canvas.create_text(0, 0, text="25:00", fill="white",font=("Segoe UI Light", 42), anchor="c")

        # Botones
        btn_frame = tk.Frame(self.root, bg="#111")
        btn_frame.pack(pady=10)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TButton",
                        background="#222", foreground="white",
                        font=("Segoe UI", 10), borderwidth=0, padding=6)
        style.map("TButton", background=[("active", "#333")])

        self.start_btn = ttk.Button(btn_frame, text="Start", command=self.start)
        self.start_btn.pack(side="left", padx=5)

        self.pause_btn = ttk.Button(btn_frame, text="Pause", command=self.pause, state="disabled")
        self.pause_btn.pack(side="left", padx=5)

        self.reset_btn = ttk.Button(btn_frame, text="Reset", command=self.reset, state="disabled")
        self.reset_btn.pack(side="left", padx=5)

        # Configuración de tiempos
        config_frame = tk.Frame(self.root, bg="#111")
        config_frame.pack()

        tk.Label(config_frame, text="Focus:", fg="white", bg="#111").grid(row=0, column=0, padx=5)
        tk.Entry(config_frame, textvariable=self.focus_time, width=5).grid(row=0, column=1)

        tk.Label(config_frame, text="Break:", fg="white", bg="#111").grid(row=0, column=2, padx=5)
        tk.Entry(config_frame, textvariable=self.break_time, width=5).grid(row=0, column=3)

    def start(self):
        if self.running:
            return

        self.is_focus = True
        self.total = self.focus_time.get() * 60
        self.remaining = self.total
        self.running = True
        self.paused = False
        self.start_btn.config(state="disabled")
        self.pause_btn.config(state="normal")
        self.reset_btn.config(state="normal")

        threading.Thread(target=self.run_timer).start()

    def pause(self):
        if not self.running:
            return

        self.paused = not self.paused
        self.pause_btn.config(text="Resume" if self.paused else "Pause")

    def reset(self):
        self.running = False
        self.paused = False
        self.remaining = 0
        self.canvas.itemconfig(self.time_text, text="00:00")
        self.canvas.itemconfig(self.time_shadow, text="00:00")
        self.start_btn.config(state="normal")
        self.pause_btn.config(state="disabled", text="Pause")
        self.reset_btn.config(state="disabled")

    def run_timer(self):
        while self.remaining > 0 and self.running:
            if not self.paused:
                time.sleep(1)
                self.remaining -= 1
            else:
                time.sleep(0.1)

        if self.remaining == 0 and self.running:
            winsound.Beep(1000, 700)
            self.running = False
            if self.is_focus:
                self.start_break()
            else:
                self.reset()

    def start_break(self):
        self.is_focus = False
        self.total = self.break_time.get() * 60
        self.remaining = self.total
        self.running = True
        self.paused = False
        self.canvas.itemconfig(self.time_text, text="00:00")
        self.canvas.itemconfig(self.time_shadow, text="00:00")
        threading.Thread(target=self.run_timer).start()

    def animate_circle(self):
        self.canvas.delete("arc")
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()

        cx = w // 2
        cy = h // 2

        radius = min(w, h) // 2 - 60
        x0 = cx - radius
        y0 = cy - radius
        x1 = cx + radius
        y1 = cy + radius

        if self.total > 0:
            percent = (self.total - self.remaining) / self.total
        else:
            percent = 0

        angle = percent * 360

        self.canvas.create_oval(x0, y0, x1, y1, outline="#333", width=10, tags="arc")
        self.canvas.create_arc(x0, y0, x1, y1, start=90, extent=-angle,outline="#FDB207", width=10, style="arc", tags="arc")

        # Actualiza el tiempo y su posición centrada
        mins, secs = divmod(self.remaining, 60)
        tiempo = f"{mins:02d}:{secs:02d}"
        self.canvas.itemconfig(self.time_text, text=tiempo)
        self.canvas.itemconfig(self.time_shadow, text=tiempo)

        self.canvas.coords(self.time_text, cx, cy)
        self.canvas.coords(self.time_shadow, cx + 2, cy + 2)

        self.root.after(33, self.animate_circle)  # ~30 FPS

if __name__ == "__main__":
    root = tk.Tk()
    app = SoftPomodoroApp(root)
    root.mainloop()

