import random
import json
from asesino import Asesino
from generador_crimenes import generar_crimenes_asesino, generar_crimenes_no_asesino
from rutina_juego import mostrar_crimenes, seleccionar_crimen_y_investigar

# Cargar listas de opciones desde JSON
with open('elementos.json', 'r', encoding='utf-8') as f:
    elementos = json.load(f)

victimas = elementos["victimas"]
armas = elementos["armas"]
lugares = elementos["lugares"]
otros = elementos["otros"]

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

    print("="*60)
    print("                CATCH THE KILLER 🔪🔍")
    print("="*60)
    print("¡Bienvenido/a, Inspector/a!")
    print("\nOBJETIVO:")
    print("Se han reportado múltiples crímenes en el área. Tu meta es")
    print("identificar al **Asesino en Serie**, que es responsable de ")
    print("exactamente 3 de estos homicidios.")
    print("\nREGLAS DE IDENTIFICACIÓN:")
    print("1. El Asesino tiene una *\"Firma\"* única:")
    print("   Sus 3 crímenes comparten EXACTAMENTE 2 RASGOS idénticos")
    print("   (ej. misma arma y mismo lugar), pero varían en el resto.")
    print("2. El resto de crímenes son ruido: No hay 2 crímenes iguales.")
    print("   Todos los crímenes en la lista difieren en al menos 2 atributos.")
    print("\nMECÁNICA:")
    print("Cada crimen tiene una pista Oculta ('XXXXXX'). Al investigar,")
    print("debes desencriptar el archivo forense (Minijuego MASTERMIND).")
    print("- Adivina la clave posicional de 4 dígitos (del 1 al 6, sin repe).")
    print("- 'O' (acierto exacto), '-' (número correcto, mal posicionado), 'X' (fallo).")
    print("- Si aciertas, la pista se revela. Si fallas tus 6 intentos, se BLOQUEA.")
    print("="*60)
    input("\nPresiona ENTER para comenzar el análisis forense...")

    # Rutina del juego: 3 fases
    for fase in range(1, 4):
        mostrar_crimenes(todos_los_crimenes, fase)
        seleccionar_crimen_y_investigar(todos_los_crimenes, fase)
        print("\nHas investigado un crimen en esta fase. Pasando a la siguiente fase...\n")

    # Mostrar resultado final al terminar la tercera fase
    mostrar_resultado_final(todos_los_crimenes)

if __name__ == "__main__":
    main()
