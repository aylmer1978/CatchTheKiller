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
    INVESTIGAR_EXPEDIENTE = auto()
    INVESTIGAR_CASO       = auto()
    ATRIBUTO_LUGAR        = auto()
    ATRIBUTO_FRANJA       = auto()
    ATRIBUTO_ARMA         = auto()
    ATRIBUTO_VICTIMA      = auto()
    ATRIBUTO_OTROS        = auto()


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
}

# Cartas que revelan un atributo específico
TIPOS_ATRIBUTO = {
    TipoCarta.ATRIBUTO_LUGAR,
    TipoCarta.ATRIBUTO_FRANJA,
    TipoCarta.ATRIBUTO_ARMA,
    TipoCarta.ATRIBUTO_VICTIMA,
    TipoCarta.ATRIBUTO_OTROS,
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

    def __repr__(self) -> str:
        return f"Carta({self.icono} {self.nombre})"
