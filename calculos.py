"""Series de costos del protocolo ARQ. El índice i comienza en 1."""

from math import log


CASOS = {
    "A": "WiFi estándar",
    "B": "Fibra con reintentos decrecientes",
    "C": "Red móvil con copia extra",
}
UMBRAL = 10
TOLERANCIA = 1e-10


def obtener_probabilidades(rut):
    """Recibe los ocho dígitos como texto para conservar los ceros iniciales."""
    if not isinstance(rut, str) or len(rut) != 8 or not rut.isascii() or not rut.isdigit():
        raise ValueError("Escribe exactamente ocho dígitos (0 a 9) sin puntos ni guion.")

    d1, d2, d3, d4, d5, d6, d7, d8 = map(int, rut)
    p1 = 2 * (d1 + d3 + d5 + 1) / 100
    p2 = 3 * (d2 + d4 + d6 + 1) / 100
    p3 = 4 * (d7 + d8 + 1) / 100
    return {"p1": p1, "p2": p2, "p3": p3}


def termino_serie(caso, i, p):
    """Costo del intento i ponderado por su probabilidad."""
    if caso == "A":
        return i * (1 - p) ** (i - 1) * p
    if caso == "B":
        return (1 / i) * (1 - p) ** (i - 1) * p
    if caso == "C":
        return (i + 1) * (1 - p) ** (i - 1) * p
    raise ValueError("El caso debe ser A, B o C.")


def calcular_sumas_parciales(caso, p, cantidad):
    """Guarda S₁, S₂, …, actualizando la misma suma en cada intento."""
    sumas = []
    acumulado = 0.0
    for i in range(1, cantidad + 1):
        acumulado += termino_serie(caso, i, p)
        sumas.append(acumulado)
    return sumas


def cantidad_de_terminos(probabilidades):
    """Elige un mismo N que garantice un error de truncamiento ≤ TOLERANCIA."""
    # Si q = 1-p, el resto de C es la suma de (N+j+1)·p·q^(N+j-1), j ≥ 1.
    # Al factorizar q^N y usar las sumas geométricas de p·q^(j-1) y
    # j·p·q^(j-1), resulta q^N · (N+1+1/p). A y B cuestan a lo sumo C.
    # Ambos factores crecen al disminuir p. El menor p cubre las nueve series.
    p_menor = min(probabilidades.values())
    cantidad = 10
    while (1 - p_menor) ** cantidad * (cantidad + 1 + 1 / p_menor) > TOLERANCIA:
        cantidad += 1
    return cantidad


def limite_analitico(caso, p):
    """Formas cerradas de las series, con logaritmo natural para B."""
    # Con q = 1-p, A usa la derivada de la serie geométrica:
    # Σ i·q^(i-1) = 1/(1-q)². Para B se usa Σ q^i/i = −ln(1-q).
    # La copia adicional de C suma Σ p·q^(i-1) = 1 al costo de A.
    if caso == "A":
        return 1 / p
    if caso == "B":
        return -p * log(p) / (1 - p)
    if caso == "C":
        return 1 / p + 1
    raise ValueError("El caso debe ser A, B o C.")


def evaluar_combinacion(caso, p, cantidad):
    sumas = calcular_sumas_parciales(caso, p, cantidad)
    empirico = sumas[-1]
    analitico = limite_analitico(caso, p)

    # En aritmética exacta, S_N ≤ L ≤ S_N + TOLERANCIA. Cerca del umbral
    # usamos la forma cerrada para resolver la igualdad y el redondeo numérico.
    if abs(empirico - UMBRAL) <= 2 * TOLERANCIA:
        viable = analitico <= UMBRAL
    else:
        viable = empirico <= UMBRAL

    return {
        "sumas": sumas,
        "empirico": empirico,
        "analitico": analitico,
        "error": abs(analitico - empirico),
        # En los tres casos el cociente de términos tiende a 1-p.
        "converge": 0 < p < 1,
        "viable": viable,
    }


def seleccionar_recomendaciones(resultados):
    """Conserva todos los mínimos viables si dos etiquetas dan el mismo costo."""
    menor_costo = float("inf")
    mejores = []
    for caso, combinaciones in resultados.items():
        for etiqueta, datos in combinaciones.items():
            if datos["viable"]:
                costo = datos["analitico"]
                if costo < menor_costo:
                    menor_costo = costo
                    mejores = [(caso, etiqueta)]
                elif costo == menor_costo:
                    mejores.append((caso, etiqueta))
    return mejores


def analizar_casos(probabilidades):
    """Evalúa los tres protocolos para cada probabilidad del RUT."""
    cantidad = cantidad_de_terminos(probabilidades)
    por_caso = {}
    for caso in CASOS:
        por_caso[caso] = {}
        for etiqueta, p in probabilidades.items():
            por_caso[caso][etiqueta] = evaluar_combinacion(caso, p, cantidad)
    return cantidad, por_caso
