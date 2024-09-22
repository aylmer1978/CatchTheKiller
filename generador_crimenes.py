import random
from crimen import Crimen

def generar_crimenes_asesino(asesino, victimas, armas, lugares, otros):
    crimenes = []
    contador_elementos = {
        "Víctima": {},
        "Arma": {},
        "Lugar": {},
        "Otros": {}
    }

    asesino_rasgos = asesino.cometer_crimen()

    # Imprimir los rasgos del asesino
    print(f"Rasgos del asesino: Víctima: {asesino_rasgos['Víctima']}, Arma: {asesino_rasgos['Arma']}, Lugar: {asesino_rasgos['Lugar']}, Otros: {asesino_rasgos['Otros']}")

    # Generar los tres crímenes del asesino
    for _ in range(3):
        # Para el elemento irrelevante (None), seleccionamos aleatoriamente en cada crimen
        victima = elegir_elemento_irrelevante("Víctima", victimas, contador_elementos) if asesino_rasgos["Víctima"] is None else asesino_rasgos["Víctima"]
        arma = elegir_elemento_irrelevante("Arma", armas, contador_elementos) if asesino_rasgos["Arma"] is None else asesino_rasgos["Arma"]
        lugar = elegir_elemento_irrelevante("Lugar", lugares, contador_elementos) if asesino_rasgos["Lugar"] is None else asesino_rasgos["Lugar"]
        otro = elegir_elemento_irrelevante("Otros", otros, contador_elementos) if asesino_rasgos["Otros"] is None else asesino_rasgos["Otros"]

        crimen = Crimen(victima, arma, lugar, otro)
        crimen.marcado_asesino = True
        crimenes.append(crimen)

        # Actualizar contadores de los elementos irrelevantes
        if asesino_rasgos["Víctima"] is None:
            contador_elementos["Víctima"][victima] = contador_elementos["Víctima"].get(victima, 0) + 1
        if asesino_rasgos["Arma"] is None:
            contador_elementos["Arma"][arma] = contador_elementos["Arma"].get(arma, 0) + 1
        if asesino_rasgos["Lugar"] is None:
            contador_elementos["Lugar"][lugar] = contador_elementos["Lugar"].get(lugar, 0) + 1
        if asesino_rasgos["Otros"] is None:
            contador_elementos["Otros"][otro] = contador_elementos["Otros"].get(otro, 0) + 1

    return crimenes

def elegir_elemento_irrelevante(tipo, lista_elementos, contador_elementos):
    """
    Elige un elemento irrelevante aleatorio que no se haya repetido más de 2 veces.
    """
    elementos_validos = [elemento for elemento in lista_elementos if contador_elementos[tipo].get(elemento, 0) < 2]
    if not elementos_validos:
        return random.choice(lista_elementos)  # Si no hay elementos válidos, elegir uno al azar
    return random.choice(elementos_validos)


def generar_crimenes_no_asesino(asesino, victimas, armas, lugares, otros, crímenes_existentes, num_crimenes_no_asesino):
    crimenes = []
    contador_elementos = {
        "Víctima": {},
        "Arma": {},
        "Lugar": {},
        "Otros": {}
    }

    # Contamos los elementos ya utilizados en los crímenes del asesino
    for crimen in crímenes_existentes:
        detalles = crimen.mostrar_detalles()
        contador_elementos["Víctima"][detalles["Víctima"]] = contador_elementos["Víctima"].get(detalles["Víctima"], 0) + 1
        contador_elementos["Arma"][detalles["Arma"]] = contador_elementos["Arma"].get(detalles["Arma"], 0) + 1
        contador_elementos["Lugar"][detalles["Lugar"]] = contador_elementos["Lugar"].get(detalles["Lugar"], 0) + 1
        contador_elementos["Otros"][detalles["Otros"]] = contador_elementos["Otros"].get(detalles["Otros"], 0) + 1

    asesino_rasgos = asesino.cometer_crimen()

    # Generar los crímenes adicionales que no incluyan ningún rasgo del asesino
    for _ in range(num_crimenes_no_asesino):
        while True:
            # Elegir aleatoriamente los elementos para el nuevo crimen
            victima = random.choice(victimas)
            arma = random.choice(armas)
            lugar = random.choice(lugares)
            otro = random.choice(otros)

            # Comprobar que no sea un crimen del asesino
            if (victima, arma, lugar, otro) != (asesino_rasgos["Víctima"], asesino_rasgos["Arma"], asesino_rasgos["Lugar"], asesino_rasgos["Otros"]):
                # Asegurarse de que los elementos no se repiten más de dos veces en total
                if (contador_elementos["Víctima"].get(victima, 0) < 2 and
                    contador_elementos["Arma"].get(arma, 0) < 2 and
                    contador_elementos["Lugar"].get(lugar, 0) < 2 and
                    contador_elementos["Otros"].get(otro, 0) < 2):

                    # Crear el crimen y actualizar los contadores
                    crimen = Crimen(victima, arma, lugar, otro)
                    crimenes.append(crimen)

                    contador_elementos["Víctima"][victima] = contador_elementos["Víctima"].get(victima, 0) + 1
                    contador_elementos["Arma"][arma] = contador_elementos["Arma"].get(arma, 0) + 1
                    contador_elementos["Lugar"][lugar] = contador_elementos["Lugar"].get(lugar, 0) + 1
                    contador_elementos["Otros"][otro] = contador_elementos["Otros"].get(otro, 0) + 1
                    break

    return crimenes