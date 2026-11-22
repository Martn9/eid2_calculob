"""Gráficos de S_k en función del número de términos acumulados."""

from matplotlib.figure import Figure
from matplotlib.ticker import LogLocator, StrMethodFormatter


ESTILOS = {
    "p1": ("#17608A", "o"),
    "p2": ("#B34B24", "s"),
    "p3": ("#227862", "^"),
}


def crear_grafico(caso, nombre, probabilidades, combinaciones, figura=None):
    if figura is None:
        figura = Figure(figsize=(6.2, 3.8), constrained_layout=True)
    else:
        figura.clear()
    eje = figura.subplots()
    figura.suptitle(f"Caso {caso} · {nombre}", x=0.06, ha="left",
                    fontsize=13, fontweight="bold", color="#193547")
    subtitulo = "Las líneas horizontales discontinuas indican los límites analíticos."
    etiquetas_por_valor = {}
    for etiqueta, p in probabilidades.items():
        etiquetas_por_valor.setdefault(p, []).append(etiqueta)
    for etiquetas in etiquetas_por_valor.values():
        if len(etiquetas) > 1:
            subtitulo += "\nCurvas coincidentes para " + " = ".join(etiquetas) + "."
    eje.set_title(subtitulo,
                  loc="left", fontsize=10, color="#465D69", pad=7)

    for posicion, (etiqueta, p) in enumerate(probabilidades.items()):
        datos = combinaciones[etiqueta]
        sumas = datos["sumas"]
        limite = datos["analitico"]
        color, marca = ESTILOS[etiqueta]
        eje.axhline(limite, color=color, linestyle="--", linewidth=1.2, alpha=0.75)
        # Con probabilidades iguales las curvas coinciden. Alternar las marcas
        # permite reconocer las tres etiquetas incluso en ese caso.
        eje.plot(range(1, len(sumas) + 1), sumas, color=color, linewidth=2,
                 marker=marca, markersize=5, markerfacecolor="white",
                 markevery=(0.035 * posicion, 0.13), zorder=3,
                 label=f"{etiqueta} = {p:.2f}\nL = {limite:.4f}")

    # La escala logarítmica deja ver los primeros intentos y la estabilización
    # incluso cuando una probabilidad pequeña exige cientos de términos.
    eje.set_xscale("log")
    eje.set_xlim(1, len(sumas))
    eje.xaxis.set_major_locator(LogLocator(base=10, subs=(1, 2, 5), numticks=20))
    eje.xaxis.set_major_formatter(StrMethodFormatter("{x:g}"))
    eje.set_xlabel("Número de términos k (escala logarítmica)", labelpad=9)
    eje.set_ylabel("Costo esperado acumulado $S_k$", labelpad=9)
    eje.set_ylim(bottom=0)
    eje.set_axisbelow(True)
    eje.grid(which="major", color="#DBE3E6", linewidth=0.8)
    for lado in ("top", "right"):
        eje.spines[lado].set_visible(False)
    for lado in ("left", "bottom"):
        eje.spines[lado].set_color("#9DAFB7")
    eje.tick_params(colors="#354D59")
    eje.legend(loc="upper center", bbox_to_anchor=(0.5, -0.22), ncol=3, fontsize=9,
               frameon=False, columnspacing=3, handlelength=2.7)
    return figura


def mostrar_graficos(casos, probabilidades, resultados):
    import matplotlib.pyplot as plt

    for caso, nombre in casos.items():
        figura = plt.figure(figsize=(9.2, 5.9), constrained_layout=True)
        figura.canvas.manager.set_window_title(f"MATE1133 · Caso {caso}")
        crear_grafico(caso, nombre, probabilidades, resultados[caso], figura)
    plt.show()
