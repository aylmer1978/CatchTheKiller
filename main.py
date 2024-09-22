import random
from asesino import Asesino
from generador_crimenes import generar_crimenes_asesino, generar_crimenes_no_asesino

# Listas de opciones compartidas
victimas = ["Mujer 50s", "Hombre 30s", "Hombre 40s", "Homosexual", "Latino"]
armas = ["Cuchillo", "Pistola", "Cuerda", "Bisturí", "Manos", "Martillo"]
lugares = ["Ciudad", "Campo", "Bosque", "Metro", "Casa", "Callejón"]
otros = ["Violación", "Tortura", "Robo", "Amputación", "Marca especial"]

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

    # Mostrar los crímenes con un elemento oculto
    print("\nTodos los crímenes (con un elemento oculto):")
    for i, crimen in enumerate(todos_los_crimenes):
        if crimen.marcado_asesino:
            print(f"* Crimen {i + 1}: {crimen.mostrar_detalles()}")
        else:
            print(f"Crimen {i + 1}: {crimen.mostrar_detalles()}")

    # Mostrar los crímenes con todos los elementos visibles (test)
    print("\nTodos los crímenes (con todos los elementos visibles - TEST):")
    for i, crimen in enumerate(todos_los_crimenes):
        if crimen.marcado_asesino:
            print(f"* Crimen {i + 1}: {crimen.mostrar_detalles_completos()}")
        else:
            print(f"Crimen {i + 1}: {crimen.mostrar_detalles_completos()}")

if __name__ == "__main__":
    main()
