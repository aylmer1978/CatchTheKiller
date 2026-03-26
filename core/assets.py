"""
core/assets.py — Gestión de imágenes para las fichas de crimen.

Estructura esperada en /assets/:
    assets/
    ├── lugares/
    │   ├── callejon_01.png
    │   ├── callejon_02.png
    │   ├── metro_01.png
    │   └── ...
    └── cuerpos/
        ├── cuerpo_01.png       ← PNG con fondo transparente (alpha)
        ├── cuerpo_02.png
        └── ...

Convención de nombres:
    {valor_normalizado}_{numero:02d}.png

    El valor_normalizado es el valor del JSON en minúsculas, sin tildes,
    con espacios y caracteres especiales reemplazados por guión bajo.

    Ejemplos:
        "Callejón"            → callejon_01.png
        "Hospital abandonado" → hospital_abandonado_01.png
        "Baños públicos"      → banos_publicos_01.png

Comportamiento si faltan assets:
    - Sin imágenes de lugar  → la ficha no muestra imagen de fondo
    - Sin imágenes de cuerpo → la ficha no muestra cuerpo superpuesto
    - El juego nunca lanza excepción por assets faltantes

Añadir nuevas imágenes:
    Simplemente deposita el archivo en la carpeta correcta con el nombre
    normalizado. El sistema las detecta automáticamente en el siguiente arranque.
    Puedes tener tantas variantes (_01, _02, _03...) como quieras.
"""

import random
import unicodedata
import re
from pathlib import Path
from functools import lru_cache


# Directorio raíz de assets, relativo a este fichero
_ASSETS_DIR = Path(__file__).parent.parent / "assets"


def normalizar_nombre(texto: str) -> str:
    """
    Convierte un valor del JSON al prefijo de nombre de archivo.

    Ejemplos:
        "Callejón"            → "callejon"
        "Hospital abandonado" → "hospital_abandonado"
        "Baños públicos"      → "banos_publicos"
    """
    # Descomponer caracteres Unicode y eliminar diacríticos
    nfkd = unicodedata.normalize("NFKD", texto.lower())
    sin_tildes = "".join(c for c in nfkd if not unicodedata.combining(c))
    # Reemplazar cualquier secuencia no alfanumérica por guión bajo
    normalizado = re.sub(r"[^a-z0-9]+", "_", sin_tildes)
    return normalizado.strip("_")


@lru_cache(maxsize=256)
def _listar_imagenes(carpeta: Path, prefijo: str) -> tuple[Path, ...]:
    """
    Lista todas las imágenes que coinciden con el prefijo en la carpeta.
    Resultado cacheado para no releer el disco en cada frame.
    Devuelve tupla vacía si no hay ninguna.
    """
    if not carpeta.exists():
        return ()
    patron = f"{prefijo}_*.png"
    encontradas = sorted(carpeta.glob(patron))
    return tuple(encontradas)


def imagen_lugar(valor_lugar: str) -> Path | None:
    """Imagen aleatoria para el lugar. None si no hay assets."""
    carpeta = _ASSETS_DIR / "lugares"
    opciones = _listar_imagenes(carpeta, normalizar_nombre(valor_lugar))
    return random.choice(opciones) if opciones else None


def imagen_lugar_generica() -> Path | None:
    """Imagen genérica de lugar (gris, sin revelar). Archivo: _generico.png"""
    ruta = _ASSETS_DIR / "lugares" / "_generico.png"
    return ruta if ruta.exists() else None


def imagen_cuerpo() -> Path | None:
    """Imagen aleatoria de cuerpo. None si no hay assets."""
    carpeta = _ASSETS_DIR / "cuerpos"
    opciones = _listar_imagenes(carpeta, "cuerpo")
    return random.choice(opciones) if opciones else None


def imagen_cuerpo_generico() -> Path | None:
    """Imagen genérica de cuerpo (silueta). Archivo: _generico.png"""
    ruta = _ASSETS_DIR / "cuerpos" / "_generico.png"
    return ruta if ruta.exists() else None


def imagen_arma(valor_arma: str) -> Path | None:
    """Imagen aleatoria para el arma. None si no hay assets."""
    carpeta = _ASSETS_DIR / "armas"
    opciones = _listar_imagenes(carpeta, normalizar_nombre(valor_arma))
    return random.choice(opciones) if opciones else None


def imagen_arma_generica() -> Path | None:
    """Imagen genérica de arma (silueta con ?). Archivo: _generico.png"""
    ruta = _ASSETS_DIR / "armas" / "_generico.png"
    return ruta if ruta.exists() else None


def hay_assets_lugar(valor_lugar: str) -> bool:
    """True si existe al menos una imagen para ese lugar."""
    return imagen_lugar(valor_lugar) is not None


def hay_assets_cuerpo() -> bool:
    """True si existe al menos una imagen de cuerpo."""
    return imagen_cuerpo() is not None


def hay_assets_arma(valor_arma: str) -> bool:
    """True si existe al menos una imagen para ese arma."""
    return imagen_arma(valor_arma) is not None


def listar_lugares_con_assets() -> list[str]:
    """
    Devuelve los prefijos normalizados de lugares que tienen al menos una imagen.
    Útil para debug o para saber qué falta ilustrar.
    """
    carpeta = _ASSETS_DIR / "lugares"
    if not carpeta.exists():
        return []
    prefijos = set()
    for f in carpeta.glob("*.png"):
        # El prefijo es todo excepto el sufijo _NN
        partes = f.stem.rsplit("_", 1)
        if len(partes) == 2 and partes[1].isdigit():
            prefijos.add(partes[0])
    return sorted(prefijos)


def invalidar_cache() -> None:
    """Limpia la caché de listado de archivos. Útil si se añaden assets en caliente."""
    _listar_imagenes.cache_clear()


# ── Utilidad de desarrollo ─────────────────────────────────────────────── #

def informe_cobertura(valores_lugar: list[str], valores_arma: list[str] | None = None) -> dict:
    """
    Devuelve un informe de cobertura de assets.

    Uso:
        from core.assets import informe_cobertura
        import json
        with open("data/elementos.json") as f:
            el = json.load(f)
        print(informe_cobertura(el["lugares"], el["armas"]))
    """
    lugares_con = [v for v in valores_lugar if hay_assets_lugar(v)]
    lugares_sin = [v for v in valores_lugar if not hay_assets_lugar(v)]

    resultado = {
        "lugares_con_imagen":    lugares_con,
        "lugares_sin_imagen":    lugares_sin,
        "cobertura_lugares_pct": round(100 * len(lugares_con) / len(valores_lugar), 1)
                                 if valores_lugar else 0,
        "cuerpos":               hay_assets_cuerpo(),
    }

    if valores_arma is not None:
        armas_con = [v for v in valores_arma if hay_assets_arma(v)]
        armas_sin = [v for v in valores_arma if not hay_assets_arma(v)]
        resultado.update({
            "armas_con_imagen":    armas_con,
            "armas_sin_imagen":    armas_sin,
            "cobertura_armas_pct": round(100 * len(armas_con) / len(valores_arma), 1)
                                   if valores_arma else 0,
        })

    return resultado
