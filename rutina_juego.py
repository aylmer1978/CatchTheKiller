import random

def ocultar_elemento(crimen):
    """ Oculta solo uno de los elementos del crimen aleatoriamente, si no ha sido ocultado ya. """
    if not hasattr(crimen, 'elemento_oculto'):
        elementos = ["Víctima", "Arma", "Lugar", "Otros"]
        crimen.elemento_oculto = random.choice(elementos)  # Asignar solo una vez

    detalles = crimen.mostrar_detalles()

    # Ocultar el elemento seleccionado
    detalles_ocultos = {key: ("XXXXXX" if key == crimen.elemento_oculto else value) for key, value in detalles.items()}
    
    return detalles_ocultos

def investigar_crimen(crimen):
    """ Desvela el elemento oculto de un crimen. """
    detalles = crimen.mostrar_detalles()
    if hasattr(crimen, 'elemento_oculto'):
        # Corregimos el acceso a los atributos en minúsculas
        if crimen.elemento_oculto == "Víctima":
            detalles["Víctima"] = crimen.victima
        elif crimen.elemento_oculto == "Arma":
            detalles["Arma"] = crimen.arma
        elif crimen.elemento_oculto == "Lugar":
            detalles["Lugar"] = crimen.lugar
        elif crimen.elemento_oculto == "Otros":
            detalles["Otros"] = crimen.otro
    return detalles

def mostrar_crimenes(todos_los_crimenes, fase):
    """ Muestra los crímenes con un elemento oculto según la fase actual. """
    if fase == 1:
        print("\nFase 1: Los primeros cinco crímenes")
        crimenes_a_mostrar = todos_los_crimenes[:5]
    elif fase == 2:
        print("\nFase 2: El sexto crimen")
        crimenes_a_mostrar = todos_los_crimenes[:6]
    elif fase == 3:
        print("\nFase 3: El séptimo crimen")
        crimenes_a_mostrar = todos_los_crimenes

    for i, crimen in enumerate(crimenes_a_mostrar):
        # Verificar si el crimen ya ha sido investigado
        if getattr(crimen, 'bloqueado', False):
            # Muestra el crimen pero con la pista como [BLOQUEADO] permanente
            detalles = crimen.mostrar_detalles()
            detalles_ocultos = {key: ("[BLOQUEADO]" if key == crimen.elemento_oculto else value) for key, value in detalles.items()}
        elif hasattr(crimen, 'elemento_oculto') and crimen.elemento_oculto == "revelado":
            detalles_ocultos = crimen.mostrar_detalles()
        else:
            detalles_ocultos = ocultar_elemento(crimen)

        if crimen.marcado_asesino:  # Testeo: agregar * a los crímenes del asesino
            print(f"* Crimen {i + 1}: {detalles_ocultos}")
        else:
            print(f"Crimen {i + 1}: {detalles_ocultos}")

def seleccionar_crimen_y_investigar(todos_los_crimenes, fase):
    """ Permite al jugador seleccionar un crimen para investigar y desvelar su elemento oculto. """
    if fase == 1:
        crimenes_a_mostrar = todos_los_crimenes[:5]
    elif fase == 2:
        crimenes_a_mostrar = todos_los_crimenes[:6]
    elif fase == 3:
        crimenes_a_mostrar = todos_los_crimenes

    while True:
        try:
            eleccion = int(input("Introduce el número del crimen que deseas investigar: ")) - 1
            if 0 <= eleccion < len(crimenes_a_mostrar):
                crimen_investigado = crimenes_a_mostrar[eleccion]
                
                if getattr(crimen_investigado, 'bloqueado', False):
                    print("Esta pista fue corrupta y está bloqueada. Elige otro crimen.")
                    continue
                    
                if getattr(crimen_investigado, 'elemento_oculto', None) == "revelado":
                    print("Ya tienes esta pista al descubierto. Elige otro crimen para aprovechar tu turno.")
                    continue

                print(f"\nIniciando análisis forense del Crimen {eleccion + 1}...")
                from minijuegos import Mastermind
                minijuego = Mastermind()
                exito = minijuego.jugar()
                
                if exito:
                    detalles_revelados = investigar_crimen(crimen_investigado)
                    crimen_investigado.elemento_oculto = "revelado"  # Marcar el crimen como investigado
                    print(f"\nCrimen {eleccion + 1} investigado con éxito: {detalles_revelados}")
                else:
                    crimen_investigado.bloqueado = True
                    print(f"\nHas destruido la evidencia del Crimen {eleccion + 1}. Pista bloqueada para siempre.")

                break
            else:
                print("Por favor, introduce un número válido.")
        except ValueError:
            print("Entrada no válida. Por favor, introduce un número válido.")
