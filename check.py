def contar_repeticiones(crimenes):
    """
    Cuenta cuántas veces se repiten los elementos (víctima, arma, lugar, otros) en los crímenes.
    """
    contador = {
        "Víctima": {},
        "Arma": {},
        "Lugar": {},
        "Otros": {}
    }

    for crimen in crimenes:
        for elemento in ["Víctima", "Arma", "Lugar", "Otros"]:
            valor = crimen.elementos[elemento]
            if valor not in contador[elemento]:
                contador[elemento][valor] = 1
            else:
                contador[elemento][valor] += 1

    # Mostrar los resultados
    print("Conteo de repeticiones de elementos:")
    for elemento, conteo in contador.items():
        print(f"\n{elemento}:")
        for valor, cantidad in conteo.items():
            print(f"{valor}: {cantidad} veces")
    return contador


def analizar_crimenes_asesino(crimenes):
    """
    Analiza los crímenes del asesino para comprobar si el elemento irrelevante varía.
    """
    crímenes_asesino = [crimen for crimen in crimenes if hasattr(crimen, 'marcado_asesino') and crimen.marcado_asesino]

    # Asumimos que el elemento irrelevante es el que cambia en los crímenes del asesino
    print("\nAnálisis de los crímenes del asesino (elementos irrelevantes):")
    for i, crimen in enumerate(crímenes_asesino):
        print(f"Crimen {i + 1}: {crimen.mostrar_detalles()}")


def realizar_chequeo(crimenes):
    """
    Realiza un chequeo completo de los crímenes.
    """
    # Contar las repeticiones de los elementos
    contar_repeticiones(crimenes)

    # Analizar los crímenes del asesino
    analizar_crimenes_asesino(crimenes)
