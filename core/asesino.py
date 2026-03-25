"""
asesino.py — Define los rasgos persistentes del asesino en serie.

La "firma" son los 3 atributos que se repiten idénticos en TODOS
sus crímenes. Los otros 2 atributos varían libremente entre crímenes.

El asesino también tiene un nombre de prensa que se revela al final.
"""

import random
from core.crimen import ATRIBUTOS

# Apodos inspirados en casos reales y arquetipos del género
APODOS_PRENSA = [
    "El Destripador",
    "El Carnicero de la Ciudad",
    "El Ángel de la Muerte",
    "El Fantasma de las Sombras",
    "El Cosechador",
    "El Cazador Nocturno",
    "El Verdugo Silencioso",
    "El Recolector",
    "El Artista del Crimen",
    "El Mensajero",
    "El Conductor",
    "El Sereno",
    "El Confesor",
    "El Penitente",
    "El Escultor",
    "El Archivero",
    "El Bibliotecario",
    "El Jardinero",
    "El Relojero",
    "El Cartero",
    "El Vecino",
    "El Turista",
    "El Madrugador",
    "El Limpiador",
    "El Sastre",
    "El Organizador",
    "El Médico",
    "El Señor de la Noche",
    "El Caminante",
    "El Coleccionista",
]


class Asesino:
    def __init__(self, elementos: dict, num_firma: int = 3):
        """
        elementos: diccionario cargado desde elementos.json
        num_firma: cuántos atributos forman la firma (defecto: 3)
        """
        self._elementos = elementos
        self.num_firma = num_firma

        # Elegir qué 3 atributos serán la firma
        self.atributos_firma: list[str] = random.sample(list(ATRIBUTOS), num_firma)

        # Asignar un valor fijo a cada atributo de la firma
        self.valores_firma: dict[str, str] = {
            a: random.choice(elementos[self._clave(a)])
            for a in self.atributos_firma
        }

        # Nombre que la prensa le asignará (revelado al final)
        self._apodo: str = random.choice(APODOS_PRENSA)

    # ------------------------------------------------------------------ #
    #  Helpers                                                             #
    # ------------------------------------------------------------------ #

    def _clave(self, atributo: str) -> str:
        """Mapea nombre de atributo a clave del JSON."""
        mapa = {
            "lugar":   "lugares",
            "franja":  "franjas",
            "arma":    "armas",
            "victima": "victimas",
            "otros":   "otros",
        }
        return mapa[atributo]

    def atributos_variables(self) -> list[str]:
        """Los atributos que NO forman la firma."""
        return [a for a in ATRIBUTOS if a not in self.atributos_firma]

    def valor_aleatorio(self, atributo: str) -> str:
        """Devuelve un valor aleatorio para un atributo variable."""
        return random.choice(self._elementos[self._clave(atributo)])

    def nombre_prensa(self) -> str:
        """El apodo que la prensa le ha dado. Se revela al final."""
        return self._apodo

    # ------------------------------------------------------------------ #
    #  Presentación                                                        #
    # ------------------------------------------------------------------ #

    def resumen_firma(self) -> dict:
        """Devuelve la firma completa (solo para debug / pantalla de fin)."""
        return dict(self.valores_firma)

    def __repr__(self) -> str:
        return f"Asesino(firma={self.valores_firma})"
