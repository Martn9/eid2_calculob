"""Presentación en consola de los resultados calculados."""


def titulo(texto):
    print(f"\n{texto}")
    print("─" * len(texto))


def mostrar_probabilidades(rut, probabilidades):
    titulo("MATE1133 · Evaluación Integrada de Desempeño N.º 2")
    print("Límites, sucesiones y series del protocolo ARQ")
    print(f"\nRUT utilizado (ocho dígitos)  {rut}")
    for etiqueta, valor in probabilidades.items():
        print(f"  {etiqueta} = {valor:.2f}   ({valor:.0%})")


def mostrar_sumas_parciales(casos, probabilidades, resultados):
    titulo("Sumas parciales · Primeros diez intentos")
    for caso, nombre in casos.items():
        print(f"\nCaso {caso} · {nombre}")
        encabezado = f"{'Suma':<8}"
        for etiqueta, p in probabilidades.items():
            encabezado += f"{f'{etiqueta} = {p:.2f}':>15}"
        print(encabezado)
        print("─" * len(encabezado))
        for k in range(1, 11):
            fila = f"{'S' + str(k):<8}"
            for etiqueta in probabilidades:
                suma = resultados[caso][etiqueta]["sumas"][k - 1]
                fila += f"{suma:15.6f}"
            print(fila)


def mostrar_convergencia(resultados, cantidad, tolerancia):
    titulo("Convergencia · Suma numérica y comprobación analítica")
    print("El cociente entre términos consecutivos tiende a 1 − p < 1.")
    print("Por el criterio del cociente, las tres series convergen para cada p.")
    print(f"Se acumularon N = {cantidad} términos. Cota del resto ≤ {tolerancia:.0e}.")
    print("Formas cerradas de L    A = 1/p    B = −p·ln(p)/(1−p)    C = 1/p + 1\n")
    encabezado = f"{'Caso':<6}{'Prob.':<7}{'Converge':<11}{'S_N':>15}{'L analítico':>16}{'|L − S_N|':>14}"
    print(encabezado)
    print("─" * len(encabezado))
    for caso, combinaciones in resultados.items():
        for etiqueta, datos in combinaciones.items():
            converge = "Sí" if datos["converge"] else "No"
            print(f"{caso:<6}{etiqueta:<7}{converge:<11}{datos['empirico']:15.8f}"
                  f"{datos['analitico']:16.8f}{datos['error']:14.2e}")


def mostrar_viabilidad(resultados, probabilidades, umbral):
    titulo(f"Viabilidad · Costo esperado ≤ {umbral} transmisiones equivalentes")
    print("En fibra, el costo de cada reintento se pondera por 1/i.\n")
    encabezado = f"{'Caso':<7}{'Probabilidad':<16}{'Límite empírico':>18}   Clasificación"
    print(encabezado)
    print("─" * len(encabezado))
    for caso, combinaciones in resultados.items():
        for etiqueta, datos in combinaciones.items():
            probabilidad = f"{etiqueta} = {probabilidades[etiqueta]:.2f}"
            estado = "Viable" if datos["viable"] else "No viable"
            print(f"{caso:<7}{probabilidad:<16}{datos['empirico']:18.8f}   {estado}")


def mostrar_recomendacion(mejores, casos, probabilidades, resultados, umbral):
    titulo("Recomendación final")
    if not mejores:
        print("Ninguna combinación cumple el umbral.")
        return

    caso, etiqueta = mejores[0]
    costo = resultados[caso][etiqueta]["analitico"]
    print(f"Caso {caso} · {casos[caso]}, con {etiqueta} = {probabilidades[etiqueta]:.2f}.")
    print(f"La serie converge a un costo esperado de {costo:.8f} transmisiones equivalentes.")
    print(f"Cumple el umbral ({costo:.8f} ≤ {umbral}) y alcanza el menor costo entre las opciones viables.")
    for otro_caso, otra_etiqueta in mejores[1:]:
        print(f"Comparte ese mínimo con el caso {otro_caso}, {otra_etiqueta} = {probabilidades[otra_etiqueta]:.2f}.")


def imprimir_analisis(rut, casos, probabilidades, por_caso, cantidad, mejores, umbral, tolerancia):
    mostrar_probabilidades(rut, probabilidades)
    mostrar_sumas_parciales(casos, probabilidades, por_caso)
    mostrar_convergencia(por_caso, cantidad, tolerancia)
    mostrar_viabilidad(por_caso, probabilidades, umbral)
    mostrar_recomendacion(mejores, casos, probabilidades, por_caso, umbral)
