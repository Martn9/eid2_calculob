"""Entrada del RUT y consulta del análisis en una ventana de Tkinter."""

import tkinter as tk
from tkinter import font, ttk

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import calculos
import graficos
import resultados


TINTA = "#193547"
VERDE = "#126B60"
PAPEL = "#FFFFFF"
FONDO = "#F1F5F4"
GRIS = "#4E666D"


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
    estilo.configure("Treeview", rowheight=25, borderwidth=0, fieldbackground=PAPEL)
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
        selector.add(pagina, text=f"Caso {caso}")
        paginas[caso] = pagina
    return paginas


def crear_resumen(panel):
    texto(panel, "Convergencia y viabilidad", 16, negrita=True).pack(fill="x")
    detalle = texto(panel, "", 10, GRIS)
    detalle.pack(fill="x", pady=(2, 10))
    tabla = crear_tabla(panel, ("Caso", "Probabilidad", "Converge", "Límite empírico", "Viabilidad"), 9)
    tarjeta = tk.Frame(panel, bg="#E6F3EF", padx=14, pady=8)
    tarjeta.pack(fill="x", pady=(12, 0))
    texto(tarjeta, "Recomendación", 11, VERDE, True).pack(fill="x")
    recomendacion = texto(tarjeta, "", 11, wraplength=500)
    recomendacion.pack(fill="x")
    return detalle, tabla, recomendacion


def actualizar_resumen(tabla, recomendacion, probabilidades, por_caso, mejores):
    tabla.delete(*tabla.get_children())
    for caso, combinaciones in por_caso.items():
        for etiqueta, datos in combinaciones.items():
            estado = "Viable" if datos["viable"] else "No viable"
            color = "viable" if datos["viable"] else "excede"
            fila = (caso, f"{etiqueta} = {probabilidades[etiqueta]:.2f}",
                    "Sí" if datos["converge"] else "No", f"{datos['empirico']:.8f}", estado)
            tabla.insert("", "end", values=fila, tags=(color,))

    if mejores:
        caso, etiqueta = mejores[0]
        costo = por_caso[caso][etiqueta]["analitico"]
        nombres = " / ".join(nombre for _, nombre in mejores)
        mensaje = (f"Caso {caso} · {calculos.CASOS[caso]} · {nombres}\n"
                   f"Costo esperado {costo:.8f} ≤ {calculos.UMBRAL}, el menor entre las opciones viables.")
    else:
        mensaje = "Ninguna combinación cumple el umbral de costo."
    recomendacion.configure(text=mensaje)


def actualizar_sumas(tabla, probabilidades, combinaciones):
    tabla.delete(*tabla.get_children())
    for etiqueta, p in probabilidades.items():
        tabla.heading(etiqueta, text=f"{etiqueta} = {p:.2f}")
    for k in range(1, 11):
        fila = [f"S{k}"]
        for etiqueta in probabilidades:
            fila.append(f"{combinaciones[etiqueta]['sumas'][k - 1]:.6f}")
        tabla.insert("", "end", values=fila, tags=("alterna",) if k % 2 == 0 else ())


def actualizar_grafico(panel, lienzo, caso, probabilidades, combinaciones):
    figura = lienzo.figure if lienzo is not None else None
    figura = graficos.crear_grafico(caso, calculos.CASOS[caso], probabilidades, combinaciones, figura)
    if lienzo is None:
        lienzo = FigureCanvasTkAgg(figura, master=panel)
        lienzo.get_tk_widget().pack(fill="both", expand=True)
    lienzo.draw_idle()
    return lienzo


def crear_bienvenida(panel):
    portada = tk.Frame(panel, bg=PAPEL, padx=24, pady=22)
    texto(portada, "Casos que se analizarán", 17, negrita=True).pack(fill="x", pady=(0, 12))
    descripciones = {
        "A": "Cada intento tiene el mismo costo de transmisión.",
        "B": "El costo del intento i se pondera por 1/i.",
        "C": "La copia adicional aumenta en una unidad el costo.",
    }
    for caso, nombre in calculos.CASOS.items():
        ttk.Separator(portada).pack(fill="x", pady=8)
        texto(portada, f"{caso}   {nombre}", 13, VERDE, True).pack(fill="x")
        texto(portada, descripciones[caso], 11, GRIS).pack(fill="x", pady=(2, 6))
    return portada


def iniciar_aplicacion():
    ventana = tk.Tk()
    ventana.title("Análisis de convergencia")
    ventana.geometry(f"{min(1040, ventana.winfo_screenwidth()-40)}x{min(710, ventana.winfo_screenheight()-90)}")
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
    portada = crear_bienvenida(espacio)
    portada.pack(fill="both", expand=True)
    secciones = ttk.Notebook(espacio)
    resumen = tk.Frame(secciones, bg=PAPEL, padx=12, pady=10)
    sumas = ttk.Frame(secciones, padding=8)
    graficas = ttk.Frame(secciones, padding=4)
    secciones.add(resumen, text="Resumen")
    secciones.add(sumas, text="Sumas parciales")
    secciones.add(graficas, text="Gráficos")

    detalle, tabla, recomendacion = crear_resumen(resumen)
    paginas_sumas = crear_pestanas_casos(sumas)
    paginas_graficos = crear_pestanas_casos(graficas)
    tablas = {}
    lienzos = {}
    for caso, nombre in calculos.CASOS.items():
        pagina = paginas_sumas[caso]
        ttk.Label(pagina, text=nombre).pack(anchor="w", pady=(2, 8))
        tablas[caso] = crear_tabla(pagina, ("Suma", "p1", "p2", "p3"), 10)

    def calcular(evento=None):
        rut = entrada.get()
        try:
            probabilidades = calculos.obtener_probabilidades(rut)
        except ValueError as problema:
            error.configure(text=str(problema))
            entrada.focus_set()
            return

        cantidad, por_caso = calculos.analizar_casos(probabilidades)
        mejores = calculos.seleccionar_recomendaciones(por_caso)
        resultados.imprimir_analisis(rut, calculos.CASOS, probabilidades, por_caso,
                                     cantidad, mejores, calculos.UMBRAL, calculos.TOLERANCIA)
        error.configure(text="")
        detalle.configure(text=f"RUT {rut}   ·   {cantidad} términos   ·   Umbral de costo ≤ {calculos.UMBRAL}")
        for etiqueta, p in probabilidades.items():
            valores[etiqueta].configure(text=f"{etiqueta}     {p:.2f}  ({p:.0%})")
        actualizar_resumen(tabla, recomendacion, probabilidades, por_caso, mejores)
        for caso in calculos.CASOS:
            actualizar_sumas(tablas[caso], probabilidades, por_caso[caso])
            lienzos[caso] = actualizar_grafico(paginas_graficos[caso], lienzos.get(caso),
                                               caso, probabilidades, por_caso[caso])
        portada.pack_forget()
        secciones.pack(fill="both", expand=True)
        secciones.select(resumen)

    boton.configure(command=calcular)
    entrada.bind("<Return>", calcular)
    entrada.focus_set()
    ventana.mainloop()
