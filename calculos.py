from math import log

RUT_COMPLETO = "21.947.172-6"
RUT = "21947172"
CASOS = {
    "A": "WiFi estandar",
    "B": "Fibra con reintentos decrecientes",
    "C": "Red movil con copia extra",
}
UMBRAL = 10
TOLERANCIA = 1e-10
PASO_ESTABILIZACION = 1e-4


def obtener_probabilidades(rut=RUT):
    digitos = "".join(c for c in rut if c.isdigit())[:8]
    if len(digitos) != 8:
        raise ValueError("El RUT debe contener al menos ocho digitos.")

    d1, d2, d3, d4, d5, d6, d7, d8 = map(int, digitos)
    return {
        "p1": 2 * (d1 + d3 + d5 + 1) / 100,
        "p2": 3 * (d2 + d4 + d6 + 1) / 100,
        "p3": 4 * (d7 + d8 + 1) / 100,
    }


def termino_serie(caso, i, p):
    if caso == "A":
        return i * (1 - p) ** (i - 1) * p
    if caso == "B":
        return (1 / i) * (1 - p) ** (i - 1) * p
    if caso == "C":
        return (i + 1) * (1 - p) ** (i - 1) * p
    raise ValueError("El caso debe ser A, B o C.")


def calcular_sumas_parciales(caso, p, cantidad):
    sumas = []
    acumulado = 0.0
    for i in range(1, cantidad + 1):
        acumulado += termino_serie(caso, i, p)
        sumas.append(acumulado)
    return sumas


def cantidad_de_terminos(probabilidades):
    p_menor = min(probabilidades.values())
    cantidad = 10
    while (1 - p_menor) ** cantidad * (cantidad + 1 + 1 / p_menor) > TOLERANCIA:
        cantidad += 1
    return cantidad


def limite_analitico(caso, p):
    if caso == "A":
        return 1 / p
    if caso == "B":
        return -p * log(p) / (1 - p)
    if caso == "C":
        return 1 / p + 1
    raise ValueError("El caso debe ser A, B o C.")


def k_estabilizacion(sumas, paso=PASO_ESTABILIZACION):
    for k in range(2, len(sumas) + 1):
        if abs(sumas[k - 1] - sumas[k - 2]) < paso:
            return k
    return len(sumas)


def evaluar_combinacion(caso, p, cantidad):
    sumas = calcular_sumas_parciales(caso, p, cantidad)
    empirico = sumas[-1]
    analitico = limite_analitico(caso, p)
    ultimo_incremento = abs(sumas[-1] - sumas[-2])
    converge = (0 < p < 1) and (ultimo_incremento < TOLERANCIA)
    viable = (analitico <= UMBRAL) if abs(empirico - UMBRAL) <= 2 * TOLERANCIA else (empirico <= UMBRAL)
    return {
        "sumas": sumas,
        "empirico": empirico,
        "analitico": analitico,
        "error": abs(analitico - empirico),
        "k_est": k_estabilizacion(sumas),
        "converge": converge,
        "viable": viable,
    }


def seleccionar_recomendacion(resultados):
    mejor = None
    menor_costo = float("inf")
    for caso, combinaciones in resultados.items():
        for etiqueta, datos in combinaciones.items():
            if datos["viable"] and datos["empirico"] < menor_costo:
                menor_costo = datos["empirico"]
                mejor = (caso, etiqueta)
    return mejor


def seleccionar_mas_rapida_caso(combinaciones):
    etiqueta_rapida = None
    menor_k = None
    menor_costo = float("inf")
    for etiqueta, datos in combinaciones.items():
        if not datos["viable"]:
            continue
        par = (datos["k_est"], datos["empirico"])
        if menor_k is None or par < (menor_k, menor_costo):
            menor_k, menor_costo = par
            etiqueta_rapida = etiqueta
    return etiqueta_rapida


def analizar(rut=RUT):
    digitos = "".join(c for c in rut if c.isdigit())[:8]
    probabilidades = obtener_probabilidades(digitos)
    cantidad = cantidad_de_terminos(probabilidades)
    por_caso = {
        caso: {
            etiqueta: evaluar_combinacion(caso, p, cantidad)
            for etiqueta, p in probabilidades.items()
        }
        for caso in CASOS
    }
    mejor = seleccionar_recomendacion(por_caso)
    return {
        "rut_completo": RUT_COMPLETO if digitos == RUT else rut,
        "rut": digitos,
        "probabilidades": probabilidades,
        "cantidad": cantidad,
        "por_caso": por_caso,
        "mejor": mejor,
    }
