"""Entrada del RUT y consulta del análisis en una ventana de Tkinter."""

import tkinter as tk
from tkinter import font, ttk
from functools import partial

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import calculos
import graficos
import consola
from matplotlib.figure import Figure


TINTA = "#193547"
VERDE = "#126B60"
PAPEL = "#FFFFFF"
FONDO = "#F1F5F4"
GRIS = "#4E666D"


NOMBRES_CORTOS = {"A": "A · WiFi", "B": "B · Fibra", "C": "C · Red móvil"}


def configurar_estilo(ventana):
    fuente = font.nametofont("TkDefaultFont").actual("family")
    estilo = ttk.Style(ventana)
    estilo.theme_use("clam")
    estilo.configure(".", font=(fuente, 11), background=PAPEL, foreground=TINTA)
    estilo.configure("TFrame", background=PAPEL)
    estilo.configure("TSeparator", background="#D2DFDC", bordercolor="#D2DFDC")
    estilo.configure("TNotebook", bordercolor="#D2DFDC", lightcolor=PAPEL, darkcolor=PAPEL)
    estilo.configure("Treeview", bordercolor="#D2DFDC", lightcolor=PAPEL, darkcolor=PAPEL)
    estilo.configure("TButton", padding=(12, 8))
    estilo.configure("Principal.TButton", background=VERDE, foreground=PAPEL,
                     borderwidth=0, font=(fuente, 11, "bold"))
    estilo.map("Principal.TButton", background=[("pressed", "#094C43"), ("active", "#10594F")])
    estilo.configure("TEntry", padding=7, fieldbackground=PAPEL)
    estilo.configure("TNotebook", background=FONDO, borderwidth=0)
    estilo.configure("TNotebook.Tab", padding=(12, 7), background=FONDO, foreground=GRIS)
    estilo.map("TNotebook.Tab", background=[("selected", PAPEL)], foreground=[("selected", VERDE)])
    estilo.configure("Treeview", rowheight=22, borderwidth=0, fieldbackground=PAPEL)
    estilo.configure("Treeview.Heading", font=(fuente, 10, "bold"),
                     background="#E6EFEE", foreground=TINTA, bordercolor=PAPEL,
                     lightcolor="#E6EFEE", darkcolor="#E6EFEE", padding=(4, 6))


def texto(panel, contenido, tamano=11, color=TINTA, negrita=False, **opciones):
    """Etiqueta alineada a la izquierda, con el fondo de su panel."""
    familia = font.nametofont("TkDefaultFont").actual("family")
    return tk.Label(panel, text=contenido, bg=panel.cget("bg"), fg=color,
                    font=(familia, tamano, "bold" if negrita else "normal"),
                    anchor="w", justify="left", **opciones)


def crear_tabla(panel, columnas, filas):
    tabla = ttk.Treeview(panel, columns=columnas, show="headings", height=filas,
                         selectmode="none")
    for nombre in columnas:
        tabla.heading(nombre, text=nombre, anchor="center")
        tabla.column(nombre, width=88, minwidth=62, anchor="center", stretch=True)
    tabla.tag_configure("alterna", background="#F3F7F7")
    tabla.tag_configure("viable", foreground="#125D53")
    tabla.tag_configure("excede", foreground="#923919", background="#FFF0E7")
    tabla.pack(fill="x")
    return tabla


def crear_pestanas_casos(panel):
    selector = ttk.Notebook(panel)
    selector.pack(fill="both", expand=True)
    paginas = {}
    for caso in calculos.CASOS:
        pagina = ttk.Frame(selector, padding=6)
        selector.add(pagina, text=NOMBRES_CORTOS[caso])
        paginas[caso] = pagina
    return paginas


def numero(valor, decimales=4):
    return f"{valor:.{decimales}f}".replace(".", ",")


def subindice(k):
    return str(k).translate(str.maketrans("0123456789", "₀₁₂₃₄₅₆₇₈₉"))


def crear_resumen(panel):
    tarjeta = tk.Frame(panel, bg="#E5F2EE", padx=14, pady=8)
    tarjeta.pack(fill="x")
    tarjeta.columnconfigure(0, weight=1)
    texto(tarjeta, "Menor costo viable", 10, VERDE, True).grid(row=0, column=0, sticky="w")
    texto(tarjeta, "Costo esperado", 10, VERDE).grid(row=0, column=1, sticky="e")
    nombre = texto(tarjeta, "", 14, TINTA, True)
    nombre.grid(row=1, column=0, sticky="w")
    costo = texto(tarjeta, "", 19, VERDE, True)
    costo.grid(row=1, column=1, sticky="e", padx=(8, 0))
    motivo = texto(panel, "", 11, GRIS, wraplength=540)
    motivo.pack(fill="x", pady=(8, 6))
    banda = tk.Frame(panel, bg=PAPEL)
    banda.pack(fill="x", pady=(3, 6))
    conteo = texto(banda, "", 12, negrita=True)
    conteo.pack(side="left")
    boton = ttk.Button(banda, text="¿Cuándo se cumple el umbral?")
    boton.pack(side="right")
    tabla = crear_tabla(panel, ("Caso", "Probabilidad", "Converge", "Límite empírico", "Viabilidad"), 9)
    condiciones = tk.Frame(panel, bg="#F1F6F5", padx=14, pady=8)
    for caso, regla in (
        ("A · WiFi", "1/p ≤ 10   ⇒   p ≥ 1/10 = 10 %."),
        ("B · Fibra", "Todo 0 < p < 1 es viable. Los costos 1/i son como máximo 1 y sus probabilidades suman 1."),
        ("C · Red móvil", "1/p + 1 ≤ 10   ⇒   p ≥ 1/9 ≈ 11,11 %."),
    ):
        texto(condiciones, caso, 11, VERDE, True).pack(fill="x", pady=(4, 0))
        texto(condiciones, regla, 11, wraplength=490).pack(fill="x", pady=(0, 4))

    def alternar():
        if condiciones.winfo_manager():
            condiciones.pack_forget()
            tabla.pack(fill="x")
            boton.configure(text="¿Cuándo se cumple el umbral?")
        else:
            tabla.pack_forget()
            condiciones.pack(fill="x")
            boton.configure(text="Ver las nueve combinaciones")

    boton.configure(command=alternar)

    def actualizar(analisis):
        probabilidades = analisis["probabilidades"]
        por_caso = analisis["por_caso"]
        caso, etiqueta = analisis["mejor"]  # B siempre ofrece al menos una opción viable.
        p = probabilidades[etiqueta]
        nombre.configure(text=f"{NOMBRES_CORTOS[caso]}   ·   {etiqueta} = {numero(p, 2)}")
        costo.configure(text="≈ " + numero(por_caso[caso][etiqueta]["analitico"]))
        mensaje = ("En fibra, un p menor retrasa en promedio el primer éxito. Los intentos "
                   "posteriores reciben menor peso (1/i), por lo que baja el costo ponderado.")
        empatadas = [e for e, valor in probabilidades.items() if valor == p and e != etiqueta]
        if empatadas:
            mensaje += " Comparte el mínimo con " + " y ".join(empatadas) + "."
        motivo.configure(text=mensaje)
        tabla.delete(*tabla.get_children())
        viables = 0
        for caso, combinaciones in por_caso.items():
            for etiqueta, datos in combinaciones.items():
                viable = datos["viable"]
                viables += int(viable)
                fila = (NOMBRES_CORTOS[caso], f"{etiqueta} = {numero(probabilidades[etiqueta], 2)}",
                        "Sí" if datos["converge"] else "No", numero(datos["empirico"], 8),
                        "Viable" if viable else "No viable")
                tabla.insert("", "end", values=fila, tags=("viable" if viable else "excede",))
        conteo.configure(text=f"{viables} de 9 viables   ·   L ≤ {calculos.UMBRAL}")
        if condiciones.winfo_manager():
            alternar()

    return actualizar


def crear_explorador_sumas(panel, caso):
    cuerpo = tk.Frame(panel, bg=PAPEL)
    cuerpo.pack(fill="both", expand=True)
    texto(cuerpo, "Selecciona una suma para ver su cálculo", 13, negrita=True).pack(fill="x")
    rejilla = tk.Frame(cuerpo, bg=PAPEL)
    rejilla.pack(fill="x", pady=(6, 8))
    detalle = tk.Frame(cuerpo, bg=FONDO, padx=12, pady=6)
    detalle.pack(fill="x")
    formula = texto(detalle, "", 11, negrita=True)
    formula.pack(fill="x")
    operacion = texto(detalle, "", 12)
    operacion.pack(fill="x")
    probabilidades = {}
    combinaciones = {}
    celdas = {}
    cabeceras = {}
    seleccion = None


    def seleccionar(k, etiqueta):
        nonlocal seleccion
        if seleccion:
            fila, columna = seleccion
            celdas[seleccion].configure(bg=PAPEL if fila % 2 else FONDO,
                                        fg=graficos.ESTILOS[columna][0])
        seleccion = (k, etiqueta)
        color = graficos.ESTILOS[etiqueta][0]
        celdas[seleccion].configure(bg=color, fg=PAPEL)
        p = probabilidades[etiqueta]
        d = calculos.detalle_suma(caso, p, combinaciones[etiqueta], k)
        factor = {"A": str(k), "B": f"(1/{k})", "C": f"({k} + 1)"}[caso]
        valor_p = numero(p, 2)
        formula.configure(text=f"{etiqueta} · k = {k}     |     a{subindice(k)} = {factor} · (1 − {valor_p})^({k}−1)"
                               f" · {valor_p} ≈ {numero(d['termino'], 6)}", fg=color)
        operacion.configure(text=f"S{subindice(k)} = S{subindice(k-1)} + a{subindice(k)} ≈ {numero(d['anterior'], 6)}"
                                 f" + {numero(d['termino'], 6)} ≈ {numero(d['suma'], 6)}")

    texto(rejilla, "Suma", 10, GRIS, True).grid(row=0, column=0)
    for k in range(1, 11):
        texto(rejilla, f"S{k}", 10, GRIS).grid(row=k, column=0, padx=8)
    for columna, etiqueta in enumerate(graficos.ESTILOS, 1):
        color = graficos.ESTILOS[etiqueta][0]
        rejilla.columnconfigure(columna, weight=1, uniform="probabilidad")
        cabeceras[etiqueta] = texto(rejilla, "", 11, color, True)
        cabeceras[etiqueta].grid(row=0, column=columna, pady=3)
        for k in range(1, 11):
            celda = tk.Label(rejilla, fg=color, bg=PAPEL if k % 2 else FONDO,
                             cursor="hand2", takefocus=True, highlightthickness=1,
                             highlightbackground=PAPEL, highlightcolor=TINTA)
            celda.grid(row=k, column=columna, sticky="nsew")
            celdas[k, etiqueta] = celda
            def elegir(evento, fila=k, serie=etiqueta):
                evento.widget.focus_set()
                seleccionar(fila, serie)
            celda.bind("<Button-1>", elegir)
            celda.bind("<Return>", elegir)
            celda.bind("<space>", elegir)

    def actualizar(analisis):
        nonlocal probabilidades, combinaciones
        probabilidades = analisis["probabilidades"]
        combinaciones = analisis["por_caso"][caso]
        for etiqueta, p in probabilidades.items():
            cabeceras[etiqueta].configure(text=f"{etiqueta} = {numero(p, 2)}")
            for k in range(1, 11):
                celdas[k, etiqueta].configure(text=numero(combinaciones[etiqueta]["sumas"][k-1], 6))
        seleccionar(2, analisis["mejor"][1])

    return actualizar


def crear_explorador_grafico(panel, caso):
    cuerpo = tk.Frame(panel, bg=PAPEL)
    cuerpo.pack(fill="both", expand=True)
    controles = tk.Frame(cuerpo, bg=PAPEL)
    controles.pack(fill="x")
    etiqueta = tk.StringVar(value="p1")
    selector = ttk.Combobox(controles, textvariable=etiqueta, values=tuple(graficos.ESTILOS),
                            width=4, state="readonly")
    selector.pack(side="left", padx=(0, 8))
    indice = tk.IntVar(value=10)
    posicion = texto(controles, "k = 10", 11, negrita=True, width=8)
    posicion.pack(side="left")
    figura = Figure(figsize=(6.2, 3.8), constrained_layout=True)
    lienzo = FigureCanvasTkAgg(figura, master=cuerpo)
    medidas = texto(cuerpo, "", 10, negrita=True)
    medidas.pack(fill="x", pady=(5, 0))
    identidad = texto(cuerpo, "", 10, GRIS)
    if caso == "C":
        identidad.pack(fill="x")
    lienzo.get_tk_widget().pack(fill="both", expand=True)
    probabilidades = {}
    combinaciones = {}
    punto = None

    def mostrar_punto(evento=None):
        if punto is None:
            return
        k = indice.get()
        serie = etiqueta.get()
        p = probabilidades[serie]
        d = calculos.detalle_suma(caso, p, combinaciones[serie], k)
        posicion.configure(text=f"k = {k}")
        medidas.configure(fg=graficos.ESTILOS[serie][0],
                          text=f"Sₖ ≈ {numero(d['suma'], 6)}    ·    L ≈ {numero(d['limite'], 6)}"
                               f"    ·    |L − Sₖ| ≈ {d['error']:.2e}    ·    ≈ {numero(d['porcentaje'], 2)} % de L")
        if caso == "C":
            extra = calculos.costo_extra_acumulado(p, k)
            identidad.configure(text=f"Copia extra: Sₖ(C) − Sₖ(A) = 1 − (1 − p)^k ≈ {numero(extra, 6)}"
                                     "   →   1 cuando k → ∞")
        graficos.mover_marcador(punto, serie, k, d["suma"])
        lienzo.draw_idle()

    def ir_a(k):
        indice.set(k)
        mostrar_punto()

    def ir_al_final():
        ir_a(len(combinaciones[etiqueta.get()]["sumas"]))

    def ir_al_99():
        ir_a(calculos.primer_k_al_99(combinaciones[etiqueta.get()]))

    escala = tk.Scale(controles, from_=1, to=10, variable=indice, orient="horizontal",
                      showvalue=False, resolution=1, bg=PAPEL, troughcolor="#D7E9E4",
                      highlightthickness=0, command=mostrar_punto)
    escala.pack(side="left", fill="x", expand=True)
    for rotulo, accion in (("k = 10", partial(ir_a, 10)), ("99 % de L", ir_al_99), ("k = N", ir_al_final)):
        ttk.Button(controles, text=rotulo, width=8, command=accion).pack(side="left", padx=(3, 0))
    selector.bind("<<ComboboxSelected>>", mostrar_punto)

    def actualizar(analisis):
        nonlocal probabilidades, combinaciones, punto
        probabilidades = analisis["probabilidades"]
        combinaciones = analisis["por_caso"][caso]
        figura.clear()
        graficos.dibujar_caso(figura, caso, calculos.CASOS[caso], probabilidades, combinaciones)
        graficos.guardar_grafico(figura, caso)
        punto = graficos.crear_marcador(figura)
        etiqueta.set(analisis["mejor"][1])
        escala.configure(to=analisis["cantidad"])
        ir_a(10)

    return actualizar


def iniciar_aplicacion():
    ventana = tk.Tk()
    ventana.title("Análisis de convergencia")
    ventana.geometry(f"{min(1080, ventana.winfo_screenwidth()-40)}x{min(730, ventana.winfo_screenheight()-90)}")
    ventana.minsize(840, 605)
    ventana.configure(bg=FONDO)
    configurar_estilo(ventana)

    cabecera = tk.Frame(ventana, bg=TINTA, padx=24, pady=14)
    cabecera.pack(fill="x")
    texto(cabecera, "Análisis de convergencia", 22, PAPEL, True).pack(fill="x")
    texto(cabecera, "MATE1133 — Evaluación Integrada de Desempeño N.º 2",
          11, "#CCE1E2").pack(fill="x")

    cuerpo = tk.Frame(ventana, bg=FONDO, padx=16, pady=14)
    cuerpo.pack(fill="both", expand=True)
    formulario = tk.Frame(cuerpo, bg=PAPEL, padx=16, pady=16)
    formulario.pack(side="left", fill="y", padx=(0, 12))
    texto(formulario, "RUT", 14, negrita=True).pack(fill="x")
    texto(formulario, "Primeros ocho dígitos,\nsin puntos ni guion.", 10, GRIS).pack(fill="x", pady=(3, 8))
    entrada = ttk.Entry(formulario, width=17)
    entrada.pack(fill="x")
    boton = ttk.Button(formulario, text="Calcular resultados", style="Principal.TButton")
    boton.pack(fill="x", pady=(8, 0))
    error = texto(formulario, "", 10, "#963A23", wraplength=165)
    error.pack(fill="x", pady=4)
    ttk.Separator(formulario).pack(fill="x", pady=8)
    texto(formulario, "Probabilidades", 13, negrita=True).pack(fill="x")
    valores = {}
    for etiqueta in ("p1", "p2", "p3"):
        valores[etiqueta] = texto(formulario, f"{etiqueta}     —", 12)
        valores[etiqueta].pack(fill="x", pady=(8, 0))

    espacio = tk.Frame(cuerpo, bg=FONDO)
    espacio.pack(fill="both", expand=True)
    secciones = ttk.Notebook(espacio)
    resumen = tk.Frame(secciones, bg=PAPEL, padx=12, pady=10)
    sumas = ttk.Frame(secciones, padding=8)
    graficas = ttk.Frame(secciones, padding=4)
    secciones.add(resumen, text="Resumen")
    secciones.add(sumas, text="Sumas parciales")
    secciones.add(graficas, text="Gráficos")

    actualizar_resumen = crear_resumen(resumen)
    paginas_sumas = crear_pestanas_casos(sumas)
    paginas_graficos = crear_pestanas_casos(graficas)
    exploradores = []
    for caso in calculos.CASOS:
        exploradores.append(crear_explorador_sumas(paginas_sumas[caso], caso))
        exploradores.append(crear_explorador_grafico(paginas_graficos[caso], caso))

    referencia = texto(formulario, "", 10, GRIS)
    referencia.pack(fill="x", pady=(15, 0))

    def calcular(evento=None):
        rut = entrada.get()
        if len(rut) != 8 or not rut.isascii() or not rut.isdigit():
            error.configure(text="Ingresa exactamente ocho dígitos del 0 al 9.")
            entrada.focus_set()
            return

        analisis = calculos.analizar(rut)
        probabilidades = analisis["probabilidades"]
        consola.imprimir_analisis(analisis)
        error.configure(text="")
        referencia.configure(text=f"RUT analizado · {rut}\nN = {analisis['cantidad']} términos")
        for etiqueta, p in probabilidades.items():
            valores[etiqueta].configure(text=f"{etiqueta}     {numero(p, 2)}  ({p:.0%})",
                                         fg=graficos.ESTILOS[etiqueta][0])
        actualizar_resumen(analisis)
        for actualizar in exploradores:
            actualizar(analisis)
        secciones.pack(fill="both", expand=True)
        secciones.select(resumen)

    boton.configure(command=calcular)
    entrada.bind("<Return>", calcular)
    entrada.focus_set()
    entrada.insert(0, calculos.RUT)
    entrada.selection_range(0, "end")
    calcular()
    ventana.mainloop()
