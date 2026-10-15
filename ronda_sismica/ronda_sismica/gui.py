"""
Interfaz gráfica (Tkinter) - Ronda sísmica con Lista Circular Doble
"""

import math
import random
import time
import tkinter as tk
from tkinter import ttk, messagebox

from lista_circular_doble import ListaCircularDoble, Estacion

# ----------------------------- Paleta ---------------------------------- #
BG = "#0b1220"
PANEL = "#111a2e"
CARD = "#18233d"
TXT = "#e5edff"
MUTED = "#8aa0c8"
CYAN = "#38bdf8"
ORANGE = "#fb923c"
VIOLET = "#a78bfa"
SEC = "#2a3a63"      # botones secundarios
ESTADOS = {"Normal": "#22c55e", "Alerta": "#f59e0b", "Crítico": "#ef4444"}
MAX_ESTACIONES = 14
FUENTE = "Segoe UI"


def aclarar(hex_color, f=0.18):
    hex_color = hex_color.lstrip("#")
    r, g, b = (int(hex_color[i:i + 2], 16) for i in (0, 2, 4))
    r, g, b = (int(c + (255 - c) * f) for c in (r, g, b))
    return f"#{r:02x}{g:02x}{b:02x}"


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Ronda Sísmica · Lista Circular Doble")
        self.geometry("1220x780")
        self.minsize(1000, 700)
        self.configure(bg=BG)

        self.lista = ListaCircularDoble()
        self.seleccionado = None
        self.auto = False
        self.sentido = 1            # 1 = adelante (next), -1 = atrás (prev)
        self.fase = 0.0
        self.pulso = None
        self.pulso_info = None

        self._estilos()
        self._construir_ui()
        self._datos_demo()
        self.refrescar()
        self._animar()

        self.bind("<Right>", lambda e: self.avanzar())
        self.bind("<Left>", lambda e: self.retroceder())

    # ------------------------------------------------------------------ #
    #  Estilos
    # ------------------------------------------------------------------ #
    def _estilos(self):
        st = ttk.Style(self)
        st.theme_use("clam")
        st.configure("TCombobox", fieldbackground=BG, background=CARD,
                     foreground=TXT, arrowcolor=TXT, bordercolor=CARD,
                     lightcolor=CARD, darkcolor=CARD, padding=4)
        st.map("TCombobox", fieldbackground=[("readonly", BG)],
               foreground=[("readonly", TXT)],
               selectbackground=[("readonly", BG)],
               selectforeground=[("readonly", TXT)])
        self.option_add("*TCombobox*Listbox.background", BG)
        self.option_add("*TCombobox*Listbox.foreground", TXT)
        self.option_add("*TCombobox*Listbox.selectBackground", CYAN)
        self.option_add("*TCombobox*Listbox.selectForeground", BG)

    def _boton(self, parent, texto, cmd, color=CYAN, fg="#04121f"):
        b = tk.Label(parent, text=texto, bg=color, fg=fg, cursor="hand2",
                     font=(FUENTE, 10, "bold"), padx=8, pady=7)
        b.bind("<Button-1>", lambda e: cmd())
        b.bind("<Enter>", lambda e: b.configure(bg=aclarar(color)))
        b.bind("<Leave>", lambda e: b.configure(bg=color))
        return b

    def _tarjeta(self, parent, titulo):
        marco = tk.Frame(parent, bg=CARD, padx=12, pady=10)
        marco.pack(fill="x", pady=(0, 10))
        tk.Label(marco, text=titulo.upper(), bg=CARD, fg=MUTED,
                 font=(FUENTE, 8, "bold")).pack(anchor="w", pady=(0, 6))
        cuerpo = tk.Frame(marco, bg=CARD)
        cuerpo.pack(fill="x")
        return cuerpo

    # ------------------------------------------------------------------ #
    #  Construcción de la interfaz
    # ------------------------------------------------------------------ #
    def _construir_ui(self):
        izq = tk.Frame(self, bg=BG)
        izq.pack(side="left", fill="both", expand=True)

        cab = tk.Frame(izq, bg=BG)
        cab.pack(fill="x", padx=24, pady=(18, 0))
        tk.Label(cab, text="🌋  Ronda de Monitoreo Sísmico", bg=BG, fg=TXT,
                 font=(FUENTE, 20, "bold")).pack(anchor="w")
        tk.Label(cab, text="Lista Circular Doble · cada estación conoce a la "
                           "anterior y a la siguiente",
                 bg=BG, fg=MUTED, font=(FUENTE, 10)).pack(anchor="w")

        self.canvas = tk.Canvas(izq, bg=BG, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True, padx=10, pady=10)
        self.canvas.bind("<Configure>", lambda e: self.dibujar())

        der = tk.Frame(self, bg=PANEL, width=380, padx=14, pady=14)
        der.pack(side="right", fill="y")
        der.pack_propagate(False)

        # ---- Nueva estación ----
        t1 = self._tarjeta(der, "Nueva estación")
        self.v_nombre = tk.StringVar()
        self.v_altitud = tk.StringVar()
        self.v_estado = tk.StringVar(value="Normal")

        for fila, (txt, var) in enumerate((("Nombre", self.v_nombre),
                                           ("Altitud (m)", self.v_altitud))):
            tk.Label(t1, text=txt, bg=CARD, fg=TXT, font=(FUENTE, 10)
                     ).grid(row=fila, column=0, sticky="w", pady=3)
            tk.Entry(t1, textvariable=var, bg=BG, fg=TXT, insertbackground=TXT,
                     relief="flat", font=(FUENTE, 10), highlightthickness=1,
                     highlightbackground=CARD, highlightcolor=CYAN
                     ).grid(row=fila, column=1, sticky="ew", padx=(10, 0),
                            pady=3, ipady=4)
        tk.Label(t1, text="Estado", bg=CARD, fg=TXT, font=(FUENTE, 10)
                 ).grid(row=2, column=0, sticky="w", pady=3)
        ttk.Combobox(t1, textvariable=self.v_estado, values=list(ESTADOS),
                     state="readonly").grid(row=2, column=1, sticky="ew",
                                            padx=(10, 0), pady=3)
        t1.columnconfigure(1, weight=1)

        fb = tk.Frame(t1, bg=CARD)
        fb.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(8, 0))
        fb.columnconfigure((0, 1), weight=1)
        self._boton(fb, "＋ Al inicio", lambda: self.insertar("inicio")
                    ).grid(row=0, column=0, sticky="ew", padx=(0, 4))
        self._boton(fb, "＋ Al final", lambda: self.insertar("final")
                    ).grid(row=0, column=1, sticky="ew", padx=(4, 0))

        # ---- Gestión ----
        t2 = self._tarjeta(der, "Gestión de estaciones")
        t2.columnconfigure((0, 1, 2), weight=1)
        self._boton(t2, "🗑 Eliminar", self.eliminar, "#ef4444", "#ffffff"
                    ).grid(row=0, column=0, sticky="ew", padx=(0, 4))
        self._boton(t2, "✎ Estado", self.actualizar_estado, VIOLET
                    ).grid(row=0, column=1, sticky="ew", padx=4)
        self._boton(t2, "⚡ Evento", self.simular_evento, ORANGE
                    ).grid(row=0, column=2, sticky="ew", padx=(4, 0))
        tk.Label(t2, text="Clic en una estación para seleccionarla · atajos: ← →",
                 bg=CARD, fg=MUTED, font=(FUENTE, 8)
                 ).grid(row=1, column=0, columnspan=3, sticky="w", pady=(6, 0))

        # ---- Ronda ----
        t3 = self._tarjeta(der, "Ronda del guarda")
        t3.columnconfigure((0, 1), weight=1)
        self._boton(t3, "◀ Anterior", self.retroceder, SEC, TXT
                    ).grid(row=0, column=0, sticky="ew", padx=(0, 4))
        self._boton(t3, "Siguiente ▶", self.avanzar, CYAN
                    ).grid(row=0, column=1, sticky="ew", padx=(4, 0))
        self.b_auto = self._boton(t3, "▶ Ronda automática", self.toggle_auto,
                                  "#22c55e")
        self.b_auto.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(6, 0))
        self.b_sentido = self._boton(t3, "→ Sentido: next",
                                     self.cambiar_sentido, SEC, TXT)
        self.b_sentido.grid(row=2, column=0, sticky="ew", pady=(6, 0),
                            padx=(0, 4))
        self._boton(t3, "⇄ Invertir lista", self.invertir, SEC, TXT
                    ).grid(row=2, column=1, sticky="ew", pady=(6, 0), padx=(4, 0))

        # ---- Recorridos ----
        t4 = self._tarjeta(der, "Recorridos de la lista")
        self.l_adelante = tk.Label(t4, bg=CARD, fg=CYAN, justify="left",
                                   anchor="w", wraplength=330,
                                   font=(FUENTE, 9))
        self.l_adelante.pack(fill="x")
        self.l_atras = tk.Label(t4, bg=CARD, fg=ORANGE, justify="left",
                                anchor="w", wraplength=330, font=(FUENTE, 9))
        self.l_atras.pack(fill="x", pady=(6, 0))

        # ---- Bitácora ----
        t5 = self._tarjeta(der, "Bitácora")
        self.log_txt = tk.Text(t5, height=4, bg=BG, fg=MUTED, relief="flat",
                               font=("Consolas", 9), wrap="word", state="disabled",
                               highlightthickness=0)
        self.log_txt.pack(fill="x")

    # ------------------------------------------------------------------ #
    #  Utilidades
    # ------------------------------------------------------------------ #
    def log(self, msg):
        self.log_txt.configure(state="normal")
        self.log_txt.insert("end", f"[{time.strftime('%H:%M:%S')}] {msg}\n")
        self.log_txt.see("end")
        self.log_txt.configure(state="disabled")

    def _datos_demo(self):
        demo = [("Cráter Principal", 4200, "Alerta"),
                ("Cono Norte", 3900, "Normal"),
                ("Mirador", 3600, "Normal"),
                ("Refugio Alto", 3300, "Normal"),
                ("Quebrada Seca", 3000, "Normal"),
                ("Base Sur", 2700, "Normal")]
        for nombre, alt, est in demo:
            self.lista.insertar_final(Estacion(nombre, alt, est))
        self.log("Sistema iniciado con 6 estaciones de ejemplo.")

    # ------------------------------------------------------------------ #
    #  Acciones
    # ------------------------------------------------------------------ #
    def insertar(self, donde):
        nombre = self.v_nombre.get().strip()
        if not nombre:
            messagebox.showwarning("Falta el nombre", "Escribe el nombre de la estación.")
            return
        if self.lista.buscar(nombre):
            messagebox.showwarning("Repetida", f"Ya existe la estación «{nombre}».")
            return
        if self.lista.size >= MAX_ESTACIONES:
            messagebox.showinfo("Límite", f"Máximo {MAX_ESTACIONES} estaciones en pantalla.")
            return
        try:
            altitud = int(self.v_altitud.get() or 0)
        except ValueError:
            messagebox.showwarning("Altitud inválida", "La altitud debe ser un número entero.")
            return
        est = Estacion(nombre, altitud, self.v_estado.get())
        if donde == "inicio":
            self.lista.insertar_inicio(est)
        else:
            self.lista.insertar_final(est)
        self.log(f"Estación «{nombre}» insertada al {donde}.")
        self.v_nombre.set("")
        self.v_altitud.set("")
        self.refrescar()

    def eliminar(self):
        nombre = self.v_nombre.get().strip()
        if not nombre and self.seleccionado:
            nombre = self.seleccionado.data.nombre
        nodo = self.lista.buscar(nombre) if nombre else None
        if nodo is None:
            messagebox.showinfo("Eliminar", "Selecciona una estación o escribe su nombre.")
            return
        if self.lista.eliminar(nombre):
            if self.seleccionado is nodo:
                self.seleccionado = None
            self.v_nombre.set("")
            self.log(f"Estación «{nombre}» eliminada; punteros prev/next reasignados.")
            self.refrescar()

    def actualizar_estado(self):
        nodo = self.seleccionado or self.lista.actual
        if nodo is None:
            return
        nodo.data.estado = self.v_estado.get()
        self.log(f"«{nodo.data.nombre}» ahora está en estado {nodo.data.estado}.")
        self.refrescar()

    def simular_evento(self):
        nodos = self.lista.nodos()
        if not nodos:
            return
        nodo = random.choice(nodos)
        nodo.data.estado = random.choices(list(ESTADOS), weights=[3, 2, 1])[0]
        self.log(f"⚡ Evento sísmico: «{nodo.data.nombre}» → {nodo.data.estado}.")
        self.refrescar()

    def avanzar(self):
        if self.lista.actual is None:
            return
        self.lista.avanzar()
        self.log(f"▶ Guarda avanza a «{self.lista.actual.data.nombre}».")
        self.refrescar()

    def retroceder(self):
        if self.lista.actual is None:
            return
        self.lista.retroceder()
        self.log(f"◀ Guarda regresa a «{self.lista.actual.data.nombre}».")
        self.refrescar()

    def cambiar_sentido(self):
        self.sentido *= -1
        self.b_sentido.configure(
            text="→ Sentido: next" if self.sentido == 1
            else "← Sentido: prev")

    def toggle_auto(self):
        self.auto = not self.auto
        self.b_auto.configure(text="⏸ Pausar ronda" if self.auto else "▶ Ronda automática")
        if self.auto:
            self._tick()

    def _tick(self):
        if not self.auto:
            return
        if self.sentido == 1:
            self.avanzar()
        else:
            self.retroceder()
        self.after(1100, self._tick)

    def invertir(self):
        self.lista.invertir()
        self.log("⇄ Lista invertida (se intercambiaron prev y next en cada nodo).")
        self.refrescar()

    def seleccionar(self, nodo):
        self.seleccionado = nodo
        self.v_nombre.set(nodo.data.nombre)
        self.v_altitud.set(str(nodo.data.altitud))
        self.v_estado.set(nodo.data.estado)
        self.refrescar()

    # ------------------------------------------------------------------ #
    #  Dibujo
    # ------------------------------------------------------------------ #
    def refrescar(self):
        self.dibujar()
        ad = self.lista.recorrer_adelante()
        at = self.lista.recorrer_atras()
        if ad:
            self.l_adelante.configure(
                text="next →  " + " → ".join(e.nombre for e in ad) + " ↺")
            self.l_atras.configure(
                text="prev ←  " + " ← ".join(e.nombre for e in at) + " ↺")
        else:
            self.l_adelante.configure(text="Lista vacía")
            self.l_atras.configure(text="")

    def _arco(self, a, b, ctrl, color, r):
        c = self.canvas
        def punto(p, q, d):
            dx, dy = q[0] - p[0], q[1] - p[1]
            L = math.hypot(dx, dy) or 1
            return p[0] + dx / L * d, p[1] + dy / L * d
        ini = punto(a, ctrl, r + 3)
        fin = punto(b, ctrl, r + 6)
        c.create_line(ini[0], ini[1], ctrl[0], ctrl[1], fin[0], fin[1],
                      smooth=True, fill=color, width=2, arrow="last",
                      arrowshape=(10, 12, 4))

    def dibujar(self):
        c = self.canvas
        c.delete("all")
        self.pulso = None
        w, h = c.winfo_width(), c.winfo_height()
        if w < 100 or h < 100:
            return
        cx, cy = w / 2, h / 2 - 15
        R = max(min(w, h) / 2 - 112, 70)

        # decoración de fondo
        for k, dash in ((1.0, (2, 6)), (0.7, None), (0.4, None)):
            kw = {"dash": dash} if dash else {}
            c.create_oval(cx - R * k, cy - R * k, cx + R * k, cy + R * k,
                          outline="#16223d", **kw)

        nodos = self.lista.nodos()
        n = len(nodos)
        if n == 0:
            c.create_text(cx, cy, fill=MUTED, justify="center",
                          font=(FUENTE, 14),
                          text="La lista está vacía\nInserta una estación para comenzar")
            return

        r = 34 if n <= 6 else max(17, min(34, 2 * math.pi * R / n * 0.32))
        pos = []
        for i in range(n):
            ang = -math.pi / 2 + 2 * math.pi * i / n
            pos.append((cx + R * math.cos(ang), cy + R * math.sin(ang), ang))

        # ---------------- enlaces next (cian) y prev (naranja) ----------- #
        if n == 1:
            x, y, _ = pos[0]
            c.create_line(x - 12, y - r, x - 38, y - r - 58, x + 38, y - r - 58,
                          x + 12, y - r, smooth=True, fill=CYAN, width=2,
                          arrow="last", arrowshape=(10, 12, 4))
            c.create_line(x + 6, y - r - 2, x + 22, y - r - 40, x - 22, y - r - 40,
                          x - 6, y - r - 2, smooth=True, fill=ORANGE, width=2,
                          arrow="last", arrowshape=(10, 12, 4))
        else:
            for i in range(n):
                if n == 2 and i == 1:
                    continue
                j = (i + 1) % n
                ax, ay = pos[i][:2]
                bx, by = pos[j][:2]
                dx, dy = bx - ax, by - ay
                L = math.hypot(dx, dy) or 1
                ux, uy = dx / L, dy / L
                px, py = -uy, ux
                o = 6
                c.create_line(ax + ux * (r + 3) + px * o, ay + uy * (r + 3) + py * o,
                              bx - ux * (r + 6) + px * o, by - uy * (r + 6) + py * o,
                              fill=CYAN, width=2, arrow="last", arrowshape=(10, 12, 4))
                c.create_line(bx - ux * (r + 3) - px * o, by - uy * (r + 3) - py * o,
                              ax + ux * (r + 6) - px * o, ay + uy * (r + 6) - py * o,
                              fill=ORANGE, width=2, arrow="last", arrowshape=(10, 12, 4))
            if n == 2:
                a, b = pos[1][:2], pos[0][:2]
                mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
                dx, dy = b[0] - a[0], b[1] - a[1]
                L = math.hypot(dx, dy) or 1
                px, py = -dy / L, dx / L
                self._arco(a, b, (mx + px * 150, my + py * 150), CYAN, r)       # next de 1 -> 0
                self._arco(b, a, (mx - px * 150, my - py * 150), ORANGE, r)     # prev de 0 -> 1

        # ---------------------------- nodos ------------------------------ #
        for i, (x, y, ang) in enumerate(pos):
            nodo = nodos[i]
            col = ESTADOS.get(nodo.data.estado, "#64748b")
            tag = f"n{i}"

            if nodo is self.seleccionado:
                c.create_oval(x - r - 7, y - r - 7, x + r + 7, y + r + 7,
                              outline=CYAN, dash=(4, 3), width=2, tags=tag)
            c.create_oval(x - r - 3, y - r - 3, x + r + 3, y + r + 3,
                          fill="", outline=col, width=1, tags=tag)
            c.create_oval(x - r, y - r, x + r, y + r, fill=CARD, outline=col,
                          width=4, tags=tag)
            c.create_text(x, y, text=str(i), fill=TXT,
                          font=(FUENTE, max(9, int(r * 0.55)), "bold"), tags=tag)

            # etiqueta exterior
            ca, sa = math.cos(ang), math.sin(ang)
            if n == 1:
                ca, sa = 0, 1
            tx, ty = x + ca * (r + 10), y + sa * (r + 10)
            if ca > 0.35:
                anchor = "w"
            elif ca < -0.35:
                anchor = "e"
            else:
                anchor = "s" if sa < 0 else "n"
            c.create_text(tx, ty, anchor=anchor, fill=TXT, tags=tag,
                          font=(FUENTE, 10, "bold" if nodo is self.lista.actual else "normal"),
                          text=f"{nodo.data.nombre}\n{nodo.data.altitud} m")

            # insignias HEAD / TAIL (hacia el interior del círculo)
            etiquetas = []
            if nodo is self.lista.head:
                etiquetas.append("HEAD")
            if nodo is self.lista.head.prev:
                etiquetas.append("TAIL")
            if etiquetas:
                bx, by = x - math.cos(ang) * (r + 20), y - math.sin(ang) * (r + 20)
                t = c.create_text(bx, by, text="·".join(etiquetas), fill="#04121f",
                                  font=(FUENTE, 8, "bold"))
                bb = c.bbox(t)
                rect = c.create_rectangle(bb[0] - 4, bb[1] - 1, bb[2] + 4, bb[3] + 1,
                                          fill=VIOLET, outline="")
                c.tag_lower(rect, t)

            c.tag_bind(tag, "<Button-1>", lambda e, nd=nodo: self.seleccionar(nd))
            c.tag_bind(tag, "<Enter>", lambda e: c.configure(cursor="hand2"))
            c.tag_bind(tag, "<Leave>", lambda e: c.configure(cursor=""))

        # --------------------- marcador del guarda ----------------------- #
        for i, nodo in enumerate(nodos):
            if nodo is self.lista.actual:
                x, y, _ = pos[i]
                self.pulso = c.create_oval(x - r - 9, y - r - 9, x + r + 9, y + r + 9,
                                           outline="#ffffff", width=2)
                self.pulso_info = (x, y, r)
                break

        # ------------------------ información central -------------------- #
        act = self.lista.actual
        c.create_text(cx, cy - 34, text="GUARDA EN", fill=MUTED, font=(FUENTE, 9, "bold"))
        c.create_text(cx, cy - 8, text=act.data.nombre, fill=TXT,
                      font=(FUENTE, 15, "bold"), width=R * 1.1, justify="center")
        c.create_text(cx, cy + 22, text=f"● {act.data.estado}",
                      fill=ESTADOS.get(act.data.estado, MUTED), font=(FUENTE, 11, "bold"))
        c.create_text(cx, cy + 46,
                      text=f"prev: {act.prev.data.nombre}   |   next: {act.next.data.nombre}",
                      fill=MUTED, font=(FUENTE, 8), width=R * 1.3, justify="center")

        # ----------------------------- leyenda --------------------------- #
        ly = h - 24
        c.create_line(20, ly, 52, ly, fill=CYAN, width=2, arrow="last", arrowshape=(10, 12, 4))
        c.create_text(60, ly, text="next (siguiente)", fill=MUTED, anchor="w", font=(FUENTE, 9))
        c.create_line(190, ly, 222, ly, fill=ORANGE, width=2, arrow="last", arrowshape=(10, 12, 4))
        c.create_text(230, ly, text="prev (anterior)", fill=MUTED, anchor="w", font=(FUENTE, 9))
        x0 = 350
        for nombre, col in ESTADOS.items():
            c.create_oval(x0, ly - 5, x0 + 10, ly + 5, fill=col, outline="")
            c.create_text(x0 + 16, ly, text=nombre, fill=MUTED, anchor="w", font=(FUENTE, 9))
            x0 += 85

    # ------------------------------------------------------------------ #
    #  Animación del pulso del guarda
    # ------------------------------------------------------------------ #
    def _animar(self):
        self.fase += 0.18
        if self.pulso is not None and self.pulso_info:
            x, y, r = self.pulso_info
            rr = r + 9 + 3 * math.sin(self.fase)
            try:
                self.canvas.coords(self.pulso, x - rr, y - rr, x + rr, y + rr)
            except tk.TclError:
                self.pulso = None
        self.after(50, self._animar)
