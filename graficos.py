from pathlib import Path

import matplotlib
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure
from matplotlib.ticker import LogLocator, StrMethodFormatter

from calculos import CASOS

ESTILOS = {
    "p1": ("#17608A", "o"),
    "p2": ("#B34B24", "s"),
    "p3": ("#227862", "^"),
}


def dibujar_caso(figura, caso, nombre, probabilidades, combinaciones):
    eje = figura.subplots()
    figura.suptitle(f"Caso {caso} - {nombre}", x=0.06, ha="left", fontsize=13, fontweight="bold")
    eje.set_title(
        "Curvas Sk vs k y lineas horizontales discontinuas de estabilizacion (limite empirico)",
        loc="left",
        fontsize=9.5,
    )

    max_k = 1
    for pos, (etiqueta, p) in enumerate(probabilidades.items()):
        datos = combinaciones[etiqueta]
        sumas = datos["sumas"]
        max_k = max(max_k, len(sumas))
        limite = datos["empirico"]
        color, marca = ESTILOS[etiqueta]

        eje.axhline(limite, color=color, linestyle="--", linewidth=1.2, alpha=0.75)
        eje.plot(
            range(1, len(sumas) + 1),
            sumas,
            color=color,
            linewidth=2,
            marker=marca,
            markersize=5,
            markerfacecolor="white",
            markevery=(0.035 * pos, 0.13),
            label=f"{etiqueta} = {p:.2f} (L = {limite:.4f})",
        )

    eje.set_xscale("log")
    eje.set_xlim(1, max_k)
    eje.xaxis.set_major_locator(LogLocator(base=10, subs=(1, 2, 5), numticks=20))
    eje.xaxis.set_major_formatter(StrMethodFormatter("{x:g}"))
    eje.set_xlabel("Numero de terminos acumulados k (escala logaritmica)")
    eje.set_ylabel("Suma parcial acumulada Sk")
    eje.set_ylim(bottom=0)
    eje.grid(which="major", color="#DBE3E6", linewidth=0.8)
    eje.legend(loc="upper center", bbox_to_anchor=(0.5, -0.18), ncol=3, fontsize=8.5, frameon=False)


def generar_graficos(analisis, carpeta="graficos", mostrar=True):
    destino = Path(carpeta)
    destino.mkdir(parents=True, exist_ok=True)
    probabilidades = analisis["probabilidades"]
    por_caso = analisis["por_caso"]
    interactivo = mostrar and ("agg" not in matplotlib.get_backend().lower())
    rutas = []

    if interactivo:
        import matplotlib.pyplot as plt

        for caso, nombre in CASOS.items():
            figura = plt.figure(figsize=(8.0, 4.8), constrained_layout=True)
            if figura.canvas.manager is not None:
                figura.canvas.manager.set_window_title(f"MATE1133 - Caso {caso}")
            dibujar_caso(figura, caso, nombre, probabilidades, por_caso[caso])
            ruta = destino / f"caso_{caso}.png"
            figura.savefig(ruta, dpi=150, bbox_inches="tight")
            rutas.append(ruta)
        plt.show()
        return rutas

    for caso, nombre in CASOS.items():
        figura = Figure(figsize=(8.0, 4.8), constrained_layout=True)
        dibujar_caso(figura, caso, nombre, probabilidades, por_caso[caso])
        FigureCanvasAgg(figura)
        ruta = destino / f"caso_{caso}.png"
        figura.savefig(ruta, dpi=150, bbox_inches="tight")
        rutas.append(ruta)

    return rutas
