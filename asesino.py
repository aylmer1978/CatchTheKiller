import random

class Asesino:
    def __init__(self, victimas, armas, lugares, otros):
        # Seleccionamos 3 rasgos aleatorios y dejamos 1 como irrelevante (None)
        rasgos = {
            "Víctima": random.choice(victimas),
            "Arma": random.choice(armas),
            "Lugar": random.choice(lugares),
            "Otros": random.choice(otros)
        }

        # Hacer que uno de los rasgos sea irrelevante (None)
        irrelevante = random.choice(["Víctima", "Arma", "Lugar", "Otros"])
        rasgos[irrelevante] = None

        # Asignamos los rasgos del asesino
        self.victima = rasgos["Víctima"]
        self.arma = rasgos["Arma"]
        self.lugar = rasgos["Lugar"]
        self.otro = rasgos["Otros"]

    def cometer_crimen(self):
        return {
            "Víctima": self.victima,
            "Arma": self.arma,
            "Lugar": self.lugar,
            "Otros": self.otro
        }
