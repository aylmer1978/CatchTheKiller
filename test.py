import random
from crimen import Crimen
from asesino import Asesino

# Listas de opciones compartidas
victimas = ["Mujer 50s", "Hombre 30s", "Hombre 40s", "Homosexual", "Latino"]
armas = ["Cuchillo", "Pistola", "Cuerda", "Bisturí", "Manos", "Martillo"]
lugares = ["Ciudad", "Campo", "Bosque", "Metro", "Casa", "Callejón"]
otros = ["Violación", "Tortura", "Robo", "Amputación", "Marca especial"]

def generar_crimenes_asesino(asesino):
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

# Ejemplo de integración en el juego

def main():
    asesino = Asesino()  # Creamos el asesino con tres rasgos aleatorios y un elemento irrelevante
    crimenes = generar_crimenes_asesino(asesino)  # Generamos los tres crímenes del asesino

    # Mostrar los crímenes del asesino en el juego
    for i, crimen in enumerate(crimenes):
        print(f"Crimen {i + 1}: {crimen.mostrar_detalles()}")

if __name__ == "__main__":
    main()
