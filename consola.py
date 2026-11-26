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

    titulo("MATE1133 - Evaluacion Integrada de Desempeño N. 2")
    print(f"RUT seleccionado: {rut_completo} (primeros 8 digitos: {rut})")
    print(f"Digitos: {digitos_lista}")
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

    titulo(f"3. Convergencia y limite empirico (N = {cantidad} terminos, cota de error <= {TOLERANCIA:.0e})")
    encabezado = (
        f"{'Caso':<6}{'Prob.':<11}{'Converge':<10}{'Limite empirico':>17}"
        f"{'Limite analitico':>18}{'|L - S_N|':>13}"
    )
    print(encabezado)
    print("-" * len(encabezado))
    for caso, combinaciones in por_caso.items():
        for etiqueta, datos in combinaciones.items():
            prob_txt = f"{etiqueta}={probabilidades[etiqueta]:.2f}"
            converge = "Si" if datos["converge"] else "No"
            print(
                f"{caso:<6}{prob_txt:<11}{converge:<10}{datos['empirico']:17.8f}"
                f"{datos['analitico']:18.8f}{datos['error']:13.2e}"
            )

    titulo(f"5. Tabla de viabilidad (umbral C_max = {UMBRAL} transmisiones esperadas)")
    encabezado = f"{'Caso':<6}{'Probabilidad':<14}{'Limite empirico':>17}{'<= C_max':>11}   Viabilidad"
    print(encabezado)
    print("-" * len(encabezado))
    for caso, combinaciones in por_caso.items():
        for etiqueta, datos in combinaciones.items():
            prob_txt = f"{etiqueta} = {probabilidades[etiqueta]:.2f}"
            cumple = "Si" if datos["viable"] else "No"
            estado = "Viable (cumple)" if datos["viable"] else "No viable (excede)"
            print(f"{caso:<6}{prob_txt:<14}{datos['empirico']:17.8f}{cumple:>11}   {estado}")

    titulo("Recomendacion y justificacion por analisis de convergencia")
    if mejor is None:
        print(f"Ninguna combinacion cumple el umbral C_max = {UMBRAL}.")
        return

    caso, etiqueta = mejor
    p = probabilidades[etiqueta]
    datos = por_caso[caso][etiqueta]
    limite = datos["empirico"]
    k_est = datos["k_est"]
    total_viables = sum(
        1 for comb in por_caso.values() for info in comb.values() if info["viable"]
    )

    print(f"Combinacion recomendada: Caso {caso} ({CASOS[caso]}) con {etiqueta} = {p:.2f}.")
    print(
        f"1) Convergencia: por el criterio del cociente, lim(a_(i+1)/a_i) = 1 - p = {1 - p:.2f} < 1, "
        f"y empiricamente |S_N - S_(N-1)| < {TOLERANCIA:.0e}; la sucesion converge a "
        f"S_N = {limite:.8f} transmisiones esperadas."
    )
    print(
        f"2) Cumplimiento del umbral y optimalidad: {limite:.8f} <= {UMBRAL}, logrando el menor "
        f"costo esperado entre las {total_viables} combinaciones viables. En el Caso B el peso 1/i "
        f"amortigua los reintentos y mantiene el limite -p*ln(p)/(1-p) < 1, muy por debajo de "
        f"los Casos A (1/p >= {min(por_caso['A'][e]['empirico'] for e in probabilidades):.4f}) y "
        f"C (1/p + 1 >= {min(por_caso['C'][e]['empirico'] for e in probabilidades):.4f})."
    )

    rapida = seleccionar_mas_rapida_caso(por_caso[caso])
    if rapida and rapida != etiqueta:
        p_rap = probabilidades[rapida]
        datos_rap = por_caso[caso][rapida]
        print(
            f"3) Velocidad de estabilizacion: con {etiqueta} = {p:.2f} el salto entre sumas "
            f"consecutivas cae bajo {PASO_ESTABILIZACION:.0e} en k = {k_est} intentos; si se "
            f"prioriza estabilizacion mas rapida dentro del mismo Caso {caso}, {rapida} = {p_rap:.2f} "
            f"(razon 1 - p = {1 - p_rap:.2f}) lo logra en k = {datos_rap['k_est']} intentos con "
            f"limite empirico {datos_rap['empirico']:.8f} <= {UMBRAL}."
        )
