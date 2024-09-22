import random
from asesino import Asesino
from generador_crimenes import generar_crimenes_asesino, generar_crimenes_no_asesino
from rutina_juego import mostrar_crimenes, seleccionar_crimen_y_investigar

# Listas de opciones compartidas
victimas = ["Mujer 50s", "Hombre 30s", "Hombre 40s", "Homosexual", "Latino"]
armas = ["Cuchillo", "Pistola", "Cuerda", "Bisturí", "Manos", "Martillo"]
lugares = ["Ciudad", "Campo", "Bosque", "Metro", "Casa", "Callejón"]
otros = ["Violación", "Tortura", "Robo", "Amputación", "Marca especial"]

def mostrar_resultado_final(todos_los_crimenes):
    """ Muestra el resultado final al terminar las tres fases. """
    print("\nResumen final de los crímenes:")
    for i, crimen in enumerate(todos_los_crimenes):
        detalles = crimen.mostrar_detalles()
        if crimen.marcado_asesino:
            print(f"* Crimen {i + 1}: {detalles}")
        else:
            print(f"Crimen {i + 1}: {detalles}")


def main():
    # Variable para ajustar el número de crímenes que no son del asesino
    num_crimenes_no_asesino = 4  # Puedes cambiar este valor según lo necesites
    
    # Creamos el asesino
    asesino = Asesino(victimas, armas, lugares, otros)
    
    # Generamos los crímenes del asesino
    crimenes_asesino = generar_crimenes_asesino(asesino, victimas, armas, lugares, otros)

    # Generamos los crímenes adicionales que no son del asesino
    crimenes_no_asesino = generar_crimenes_no_asesino(asesino, victimas, armas, lugares, otros, crimenes_asesino, num_crimenes_no_asesino)

    # Mezclamos los crímenes del asesino y los que no lo son en un orden aleatorio
    todos_los_crimenes = crimenes_asesino + crimenes_no_asesino
    random.shuffle(todos_los_crimenes)  # Orden aleatorio

    # Rutina del juego: 3 fases
    for fase in range(1, 4):
        mostrar_crimenes(todos_los_crimenes, fase)
        seleccionar_crimen_y_investigar(todos_los_crimenes, fase)
        print("\nHas investigado un crimen en esta fase. Pasando a la siguiente fase...\n")

    # Mostrar resultado final al terminar la tercera fase
    mostrar_resultado_final(todos_los_crimenes)

if __name__ == "__main__":
    main()
