"""
core/carta.py — Modelo de carta y tipos del mazo.

Tipos:
  - INVESTIGAR_EXPEDIENTE : revela 3-5 atributos aleatorios
  - INVESTIGAR_CASO       : revela los 5 atributos completos
  - ATRIBUTO_LUGAR        : revela el lugar
  - ATRIBUTO_FRANJA       : revela la franja
  - ATRIBUTO_ARMA         : revela el arma
  - ATRIBUTO_VICTIMA      : revela la víctima
  - ATRIBUTO_OTROS        : revela "otros"
"""

from dataclasses import dataclass
from enum import Enum, auto


class TipoCarta(Enum):
    INVESTIGAR_EXPEDIENTE    = auto()
    INVESTIGAR_CASO          = auto()
    ATRIBUTO_LUGAR           = auto()
    ATRIBUTO_FRANJA          = auto()
    ATRIBUTO_ARMA            = auto()
    ATRIBUTO_VICTIMA         = auto()
    ATRIBUTO_OTROS           = auto()
    INV_PARALELA_LUGAR       = auto()
    INV_PARALELA_FRANJA      = auto()
    INV_PARALELA_ARMA        = auto()
    INV_PARALELA_VICTIMA     = auto()
    INV_PARALELA_OTROS       = auto()


# Metadatos de presentación por tipo
CARTA_META = {
    TipoCarta.INVESTIGAR_EXPEDIENTE: {
        "nombre":      "Investigar Expediente",
        "icono":       "🔍",
        "descripcion": "Revela entre 3 y 5 atributos\naleatorios del expediente.",
        "atributo":    None,
    },
    TipoCarta.INVESTIGAR_CASO: {
        "nombre":      "Investigar Caso",
        "icono":       "📋",
        "descripcion": "Revela los 5 atributos\ncompletos del expediente.",
        "atributo":    None,
    },
    TipoCarta.ATRIBUTO_LUGAR: {
        "nombre":      "Atributo: Lugar",
        "icono":       "📍",
        "descripcion": "Revela el lugar\ndel expediente.",
        "atributo":    "lugar",
    },
    TipoCarta.ATRIBUTO_FRANJA: {
        "nombre":      "Atributo: Franja",
        "icono":       "🕐",
        "descripcion": "Revela la franja horaria\ndel expediente.",
        "atributo":    "franja",
    },
    TipoCarta.ATRIBUTO_ARMA: {
        "nombre":      "Atributo: Arma",
        "icono":       "🔪",
        "descripcion": "Revela el arma\ndel expediente.",
        "atributo":    "arma",
    },
    TipoCarta.ATRIBUTO_VICTIMA: {
        "nombre":      "Atributo: Víctima",
        "icono":       "👤",
        "descripcion": "Revela la víctima\ndel expediente.",
        "atributo":    "victima",
    },
    TipoCarta.ATRIBUTO_OTROS: {
        "nombre":      "Atributo: Otros",
        "icono":       "🩸",
        "descripcion": "Revela los detalles extra\ndel expediente.",
        "atributo":    "otros",
    },
    TipoCarta.INV_PARALELA_LUGAR: {
        "nombre":      "Inv. Paralela: Lugar",
        "icono":       "🔎",
        "descripcion": "Revela un valor de LUGAR\nque NO es parte de la firma.",
        "atributo":    "lugar",
    },
    TipoCarta.INV_PARALELA_FRANJA: {
        "nombre":      "Inv. Paralela: Franja",
        "icono":       "🔎",
        "descripcion": "Revela un valor de FRANJA\nque NO es parte de la firma.",
        "atributo":    "franja",
    },
    TipoCarta.INV_PARALELA_ARMA: {
        "nombre":      "Inv. Paralela: Arma",
        "icono":       "🔎",
        "descripcion": "Revela un valor de ARMA\nque NO es parte de la firma.",
        "atributo":    "arma",
    },
    TipoCarta.INV_PARALELA_VICTIMA: {
        "nombre":      "Inv. Paralela: Victima",
        "icono":       "🔎",
        "descripcion": "Revela un valor de VICTIMA\nque NO es parte de la firma.",
        "atributo":    "victima",
    },
    TipoCarta.INV_PARALELA_OTROS: {
        "nombre":      "Inv. Paralela: Otros",
        "icono":       "🔎",
        "descripcion": "Revela un valor de OTROS\nque NO es parte de la firma.",
        "atributo":    "otros",
    },
}

# Cartas que revelan un atributo específico de un crimen
TIPOS_ATRIBUTO = {
    TipoCarta.ATRIBUTO_LUGAR,
    TipoCarta.ATRIBUTO_FRANJA,
    TipoCarta.ATRIBUTO_ARMA,
    TipoCarta.ATRIBUTO_VICTIMA,
    TipoCarta.ATRIBUTO_OTROS,
}

# Cartas de investigación paralela (revelan qué NO es la firma)
TIPOS_INV_PARALELA = {
    TipoCarta.INV_PARALELA_LUGAR,
    TipoCarta.INV_PARALELA_FRANJA,
    TipoCarta.INV_PARALELA_ARMA,
    TipoCarta.INV_PARALELA_VICTIMA,
    TipoCarta.INV_PARALELA_OTROS,
}

# Mapa de carta paralela → atributo correspondiente
PARALELA_A_ATRIBUTO = {
    TipoCarta.INV_PARALELA_LUGAR:   "lugar",
    TipoCarta.INV_PARALELA_FRANJA:  "franja",
    TipoCarta.INV_PARALELA_ARMA:    "arma",
    TipoCarta.INV_PARALELA_VICTIMA: "victima",
    TipoCarta.INV_PARALELA_OTROS:   "otros",
}


@dataclass(frozen=True)
class Carta:
    tipo: TipoCarta

    @property
    def nombre(self) -> str:
        return CARTA_META[self.tipo]["nombre"]

    @property
    def icono(self) -> str:
        return CARTA_META[self.tipo]["icono"]

    @property
    def descripcion(self) -> str:
        return CARTA_META[self.tipo]["descripcion"]

    @property
    def atributo(self) -> str | None:
        """Atributo específico que revela, o None si es genérica."""
        return CARTA_META[self.tipo]["atributo"]

    def es_atributo_especifico(self) -> bool:
        return self.tipo in TIPOS_ATRIBUTO

    def es_inv_paralela(self) -> bool:
        return self.tipo in TIPOS_INV_PARALELA

    def __repr__(self) -> str:
        return f"Carta({self.icono} {self.nombre})"
