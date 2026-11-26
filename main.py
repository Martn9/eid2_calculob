from calculos import RUT, analizar
from consola import imprimir_analisis


def ejecutar_en_consola():
    analisis = analizar(RUT)
    imprimir_analisis(analisis)

    try:
        from graficos import generar_graficos
    except ModuleNotFoundError as error:
        print(f"\nNo se pudieron generar los graficos: falta '{error.name}'.")
        return

    rutas = generar_graficos(analisis, mostrar=False)
    print("\n4. Graficos generados automaticamente:")
    for ruta in rutas:
        print(f"  - {ruta}")


if __name__ == "__main__":
    import sys

    if "--consola" in sys.argv:
        ejecutar_en_consola()
    else:
        from interfaz import iniciar_aplicacion
        iniciar_aplicacion()
