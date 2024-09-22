from crimen import Crimen
import random

def generar_crimenes_asesino(asesino, victimas, armas, lugares, otros):
    """ Genera los crímenes del asesino, asegurando que solo la combinación del asesino se repita tres veces. """
    crimenes = []
    combinacion_asesino = (
        random.choice(victimas),
        random.choice(armas),
        random.choice(lugares),
        random.choice(otros)
    )

    # Generar los crímenes con la combinación del asesino 3 veces
    for _ in range(3):
        crimen = Crimen(*combinacion_asesino)
        crimen.marcado_asesino = True  # Marcar el crimen como uno del asesino
        crimenes.append(crimen)

    return crimenes


def generar_crimenes_no_asesino(asesino, victimas, armas, lugares, otros, crimenes_existentes, num_crimenes_no_asesino):
    """ Genera crímenes adicionales, asegurando que la combinación del asesino no se repita. """
    crimenes = []
    contador_combinaciones = {}
    combinacion_asesino = (asesino.victima, asesino.arma, asesino.lugar, asesino.otro)

    # Añadir los crímenes ya existentes al contador
    for crimen in crimenes_existentes:
        combinacion = (crimen.victima, crimen.arma, crimen.lugar, crimen.otro)
        contador_combinaciones[combinacion] = contador_combinaciones.get(combinacion, 0) + 1

    # Generar crímenes adicionales que no repitan la combinación del asesino
    for _ in range(num_crimenes_no_asesino):
        while True:
            victima = random.choice(victimas)
            arma = random.choice(armas)
            lugar = random.choice(lugares)
            otro = random.choice(otros)

            combinacion = (victima, arma, lugar, otro)

            # Asegurarse de que la combinación del asesino no se repita
            if combinacion != combinacion_asesino:
                crimen = Crimen(victima, arma, lugar, otro)
                crimen.marcado_asesino = False
                crimenes.append(crimen)
                break

    return crimenes
