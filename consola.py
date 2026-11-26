from calculos import CASOS, PASO_ESTABILIZACION, TOLERANCIA, UMBRAL, seleccionar_mas_rapida_caso


def titulo(texto):
    print(f"\n{texto}")
    print("-" * len(texto))


def imprimir_analisis(analisis):
    rut_completo = analisis["rut_completo"]
    rut = analisis["rut"]
    probabilidades = analisis["probabilidades"]
    por_caso = analisis["por_caso"]
    cantidad = analisis["cantidad"]
    mejor = analisis["mejor"]
    digitos_lista = ", ".join(f"d{i + 1}={d}" for i, d in enumerate(rut))

    titulo("MATE1133 - Evaluación Integrada de Desempeño N. 2")
    print(f"RUT seleccionado: {rut_completo} (primeros 8 dígitos: {rut})")
    print(f"Dígitos: {digitos_lista}")
    for etiqueta, valor in probabilidades.items():
        print(f"  {etiqueta} = {valor:.2f} ({valor:.0%})")

    titulo("2. Tablas de sumas parciales S1 a S10")
    for caso, nombre in CASOS.items():
        print(f"\nCaso {caso} - {nombre}")
        encabezado = f"{'k':<6}" + "".join(
            f"{f'{etiqueta} ({p:.2f})':>15}" for etiqueta, p in probabilidades.items()
        )
        print(encabezado)
        print("-" * len(encabezado))
        for k in range(1, 11):
            fila = f"{f'S{k}':<6}" + "".join(
                f"{por_caso[caso][etiqueta]['sumas'][k - 1]:15.6f}"
                for etiqueta in probabilidades
            )
            print(fila)

    titulo(f"3. Convergencia y límite empírico (N = {cantidad} términos, cota del resto <= {TOLERANCIA:.0e})")
    encabezado = (
        f"{'Caso':<6}{'Prob.':<11}{'Converge':<10}{'Límite empírico':>17}"
        f"{'Límite analítico':>18}{'|L - S_N|':>13}"
    )
    print(encabezado)
    print("-" * len(encabezado))
    for caso, combinaciones in por_caso.items():
        for etiqueta, datos in combinaciones.items():
            prob_txt = f"{etiqueta}={probabilidades[etiqueta]:.2f}"
            converge = "Sí" if datos["converge"] else "No"
            print(
                f"{caso:<6}{prob_txt:<11}{converge:<10}{datos['empirico']:17.8f}"
                f"{datos['analitico']:18.8f}{datos['error']:13.2e}"
            )

    titulo(f"5. Tabla de viabilidad (umbral C_max = {UMBRAL} transmisiones esperadas)")
    encabezado = f"{'Caso':<6}{'Probabilidad':<14}{'Límite empírico':>17}{'<= C_max':>11}   Viabilidad"
    print(encabezado)
    print("-" * len(encabezado))
    for caso, combinaciones in por_caso.items():
        for etiqueta, datos in combinaciones.items():
            prob_txt = f"{etiqueta} = {probabilidades[etiqueta]:.2f}"
            cumple = "Sí" if datos["viable"] else "No"
            estado = "Viable (cumple)" if datos["viable"] else "No viable (excede)"
            print(f"{caso:<6}{prob_txt:<14}{datos['empirico']:17.8f}{cumple:>11}   {estado}")

    titulo("Recomendación y justificación por análisis de convergencia")
    if mejor is None:
        print(f"Ninguna combinación cumple el umbral C_max = {UMBRAL}.")
        return

    caso, etiqueta = mejor
    p = probabilidades[etiqueta]
    datos = por_caso[caso][etiqueta]
    limite = datos["empirico"]
    k_est = datos["k_est"]
    total_viables = sum(
        1 for comb in por_caso.values() for info in comb.values() if info["viable"]
    )

    print(f"Combinación recomendada: Caso {caso} ({CASOS[caso]}) con {etiqueta} = {p:.2f}.")
    print(f"El cociente entre términos sucesivos tiende a 1 − p = {1-p:.2f} < 1. La serie converge.")
    print(f"Con {cantidad} términos, S_N ≈ {limite:.8f} aproxima el límite L del costo esperado.")
    print(f"El costo cumple L ≤ {UMBRAL} y es mínimo entre las {total_viables} combinaciones viables.")
    if caso == "B":
        print("En fibra, cada intento i se pondera por 1/i. El resultado expresa un costo esperado.")

    rapida = seleccionar_mas_rapida_caso(por_caso[caso])
    if rapida and rapida != etiqueta:
        p_rap = probabilidades[rapida]
        datos_rap = por_caso[caso][rapida]
        print(
            f"Comparación de incrementos: con {etiqueta} = {p:.2f} el salto entre sumas "
            f"consecutivas cae bajo {PASO_ESTABILIZACION:.0e} en k = {k_est} intentos; en el mismo caso "
            f"{caso}, {rapida} = {p_rap:.2f} "
            f"(razón 1 - p = {1 - p_rap:.2f}) lo logra en k = {datos_rap['k_est']} intentos con "
            f"límite empírico {datos_rap['empirico']:.8f} <= {UMBRAL}."
        )
