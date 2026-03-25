"""
crimen.py — Modelo de datos de un crimen individual.

Cada crimen tiene 5 atributos:
    lugar, franja, arma, victima, otros

Estado interno:
    - marcado_asesino:      True si pertenece al asesino en serie
    - campos_revelados:     set con los nombres de atributos ya investigados
    - atributos_iniciales:  atributos visibles al investigar por primera vez (3-5)
    - visible_en_mapa:      True si ya ha aparecido en el mapa del jugador
    - archivado:            True si el jugador lo descartó a la reserva
    - sospechoso:           True si el jugador lo marcó para acusar
"""

from dataclasses import dataclass, field
from typing import Set

# Orden canónico de los 5 atributos
ATRIBUTOS = ("lugar", "franja", "arma", "victima", "otros")

# Etiquetas de presentación
ETIQUETAS = {
    "lugar":   "📍 Lugar",
    "franja":  "🕐 Franja",
    "arma":    "🔪 Arma",
    "victima": "👤 Víctima",
    "otros":   "🩸 Otros",
}


@dataclass
class Crimen:
    lugar:   str
    franja:  str
    arma:    str
    victima: str
    otros:   str

    # Estado de juego — no forman parte de la identidad del crimen
    marcado_asesino:    bool      = field(default=False, compare=False)
    campos_revelados:   Set[str]  = field(default_factory=set, compare=False)
    atributos_iniciales: list     = field(default_factory=list, compare=False)
    visible_en_mapa:    bool      = field(default=False, compare=False)
    archivado:          bool      = field(default=False, compare=False)
    sospechoso:         bool      = field(default=False, compare=False)

    # ------------------------------------------------------------------ #
    #  Acceso a datos                                                      #
    # ------------------------------------------------------------------ #

    def valor(self, atributo: str) -> str:
        """Devuelve el valor real de un atributo."""
        return getattr(self, atributo)

    def como_dict(self) -> dict:
        """Todos los atributos como diccionario {nombre: valor}."""
        return {a: self.valor(a) for a in ATRIBUTOS}

    def como_tuple(self) -> tuple:
        """Todos los atributos como tupla, en orden canónico."""
        return tuple(self.valor(a) for a in ATRIBUTOS)

    # ------------------------------------------------------------------ #
    #  Estado de investigación                                             #
    # ------------------------------------------------------------------ #

    def esta_revelado(self, atributo: str) -> bool:
        return atributo in self.campos_revelados

    def revelar(self, atributo: str) -> None:
        """Marca un atributo como investigado."""
        self.campos_revelados.add(atributo)

    def todos_revelados(self) -> bool:
        return self.campos_revelados >= set(ATRIBUTOS)

    def atributos_ocultos(self) -> list[str]:
        """Atributos aún no revelados."""
        return [a for a in ATRIBUTOS if a not in self.campos_revelados]

    # ------------------------------------------------------------------ #
    #  Presentación                                                        #
    # ------------------------------------------------------------------ #

    def num_revelados(self) -> int:
        return len(self.campos_revelados)

    def esta_completamente_revelado(self) -> bool:
        return self.campos_revelados >= set(ATRIBUTOS)

    def vista(self) -> dict:
        """
        Devuelve un dict {atributo: valor_o_???} para mostrar en UI.
        Los atributos en campos_revelados muestran su valor real.
        El resto aparece como '???'.
        Si el crimen nunca fue investigado, todo es '???'.
        """
        if not self.visible_en_mapa:
            return {a: "???" for a in ATRIBUTOS}
        return {
            a: self.valor(a) if a in self.campos_revelados else "???"
            for a in ATRIBUTOS
        }

    def __repr__(self) -> str:
        marca = "★" if self.marcado_asesino else " "
        arch  = "A" if self.archivado else " "
        sosp  = "⚑" if self.sospechoso else " "
        return f"[{marca}{arch}{sosp}] {self.como_dict()}"
