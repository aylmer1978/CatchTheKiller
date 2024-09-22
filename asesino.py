import random

class Asesino:
    def __init__(self, victimas, armas, lugares, otros):
        # Asignar valores aleatorios de los arrays para los rasgos del asesino
        self.victima = random.choice(victimas)
        self.arma = random.choice(armas)
        self.lugar = random.choice(lugares)
        self.otro = random.choice(otros)

    def mostrar_rasgos(self):
        """ Muestra los rasgos distintivos del asesino """
        return {
            "Víctima": self.victima,
            "Arma": self.arma,
            "Lugar": self.lugar,
            "Otros": self.otro
        }

