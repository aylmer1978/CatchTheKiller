import random

class Crimen:
    def __init__(self, victima, arma, lugar, otro):
        self.victima = victima
        self.arma = arma
        self.lugar = lugar
        self.otro = otro
        self.marcado_asesino = False  # Inicializamos el atributo por defecto como False
        self.elemento_oculto = random.choice(["Víctima", "Arma", "Lugar", "Otros"])  # Ocultamos un elemento aleatorio

    def mostrar_detalles(self):
        # Devolvemos los detalles, ocultando un elemento al azar
        detalles = {
            "Víctima": "XXXXX" if self.elemento_oculto == "Víctima" else self.victima,
            "Arma": "XXXXX" if self.elemento_oculto == "Arma" else self.arma,
            "Lugar": "XXXXX" if self.elemento_oculto == "Lugar" else self.lugar,
            "Otros": "XXXXX" if self.elemento_oculto == "Otros" else self.otro
        }
        return detalles

    # Método para mostrar todos los detalles sin ocultar nada (solo para testeo)
    def mostrar_detalles_completos(self):
        detalles = {
            "Víctima": self.victima,
            "Arma": self.arma,
            "Lugar": self.lugar,
            "Otros": self.otro
        }
        return detalles
