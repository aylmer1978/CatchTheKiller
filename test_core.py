"""test_core.py — Tests del core v3 (sistema de cartas)."""

import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from core.crimen import ATRIBUTOS
from core.asesino import Asesino, APODOS_PRENSA
from core.carta import Carta, TipoCarta, TIPOS_ATRIBUTO
from core.mazo import Mazo, TAMANYO_MANO, DISTRIBUCION
from core.partida import Partida, Dificultad, ResultadoAcusacion, ResultadoCarta

def cargar():
    with open("data/elementos.json", encoding="utf-8") as f:
        return json.load(f)

def ok(msg):      print(f"  ✓ {msg}")
def seccion(msg): print(f"\n── {msg} ──")


def test_carta_meta(elementos):
    seccion("TEST 1: Metadatos de cartas")
    for tipo in TipoCarta:
        c = Carta(tipo)
        assert c.nombre and c.icono and c.descripcion
        if tipo in TIPOS_ATRIBUTO:
            assert c.atributo in ATRIBUTOS
            assert c.es_atributo_especifico()
        else:
            assert c.atributo is None
            assert not c.es_atributo_especifico()
    ok(f"{len(TipoCarta)} tipos de carta con metadatos correctos")


def test_mazo_distribucion(elementos):
    seccion("TEST 2: Distribución del mazo")
    mazo = Mazo()
    total_esperado = sum(n for _, n in DISTRIBUCION)
    total_real = mazo.cartas_en_mazo() + mazo.cartas_en_descarte() + len(mazo.mano)
    assert total_real == total_esperado, f"Esperado {total_esperado}, hay {total_real}"
    assert len(mazo.mano) == TAMANYO_MANO
    ok(f"Mazo de {total_esperado} cartas, mano inicial de {TAMANYO_MANO}")


def test_mazo_jugar_y_robar(elementos):
    seccion("TEST 3: Jugar carta y robar")
    mazo = Mazo()
    cartas_antes = mazo.cartas_totales()
    carta_jugada, regenero = mazo.jugar(0)
    assert isinstance(carta_jugada, Carta)
    assert len(mazo.mano) == TAMANYO_MANO   # mano se mantiene en 3
    assert mazo.cartas_en_descarte() == 1
    assert mazo.cartas_totales() == cartas_antes
    ok(f"Jugada {carta_jugada}, mano sigue en {TAMANYO_MANO}, total conservado")


def test_mazo_descarte_gratuito(elementos):
    seccion("TEST 4: Descarte gratuito")
    mazo = Mazo()
    assert mazo.puede_descartar()
    carta = mazo.descartar(0)
    assert isinstance(carta, Carta)
    assert len(mazo.mano) == TAMANYO_MANO
    assert not mazo.puede_descartar()  # ya descartó este turno

    # Segundo descarte debe fallar
    try:
        mazo.descartar(0)
        assert False, "Debería haber lanzado ValueError"
    except ValueError:
        pass

    # Después de jugar una carta, el flag se resetea
    mazo.jugar(0)
    assert mazo.puede_descartar()
    ok("Descarte gratuito funciona, bloquea segundo descarte, reset tras jugar")


def test_mazo_regeneracion(elementos):
    seccion("TEST 5: Regeneración del mazo con penalización")
    mazo = Mazo()
    total = mazo.cartas_totales()

    # Vaciar el mazo jugando todas las cartas excepto la mano
    while mazo.cartas_en_mazo() > 0:
        mazo.jugar(0)

    assert mazo.regeneraciones == 0
    # La próxima jugada debería regenerar
    _, regenero = mazo.jugar(0)
    assert regenero
    assert mazo.regeneraciones == 1
    assert mazo.cartas_totales() == total
    ok("Regeneración detectada, contador incrementado, total conservado")


def test_jugar_carta_expediente(elementos):
    seccion("TEST 6: Jugar carta INVESTIGAR_EXPEDIENTE")
    asesino = Asesino(elementos)
    partida = Partida(asesino, elementos)
    idx_crimen = partida.crimenes_en_mapa()[0][0]

    # Buscar una carta de tipo INVESTIGAR_EXPEDIENTE en mano
    idx_carta = next(
        (i for i, c in enumerate(partida.mazo.mano)
         if c.tipo == TipoCarta.INVESTIGAR_EXPEDIENTE),
        None
    )
    if idx_carta is None:
        ok("No había carta INVESTIGAR_EXPEDIENTE en mano (aleatorio), test omitido")
        return

    res = partida.jugar_carta(idx_carta, idx_crimen)
    assert res.exito
    assert 3 <= len(res.atributos) <= 5
    assert len(partida.mazo.mano) == TAMANYO_MANO
    ok(f"INVESTIGAR_EXPEDIENTE reveló {len(res.atributos)} atributos, mano conservada")


def test_jugar_carta_caso(elementos):
    seccion("TEST 7: Jugar carta INVESTIGAR_CASO")
    asesino = Asesino(elementos)
    partida = Partida(asesino, elementos)
    idx_crimen = partida.crimenes_en_mapa()[0][0]

    # Forzar carta INVESTIGAR_CASO en posición 0 de la mano
    partida.mazo.mano[0] = Carta(TipoCarta.INVESTIGAR_CASO)
    res = partida.jugar_carta(0, idx_crimen)
    assert res.exito
    assert len(res.atributos) == 5
    assert partida.crimen(idx_crimen).todos_revelados()
    ok("INVESTIGAR_CASO revela los 5 atributos")


def test_jugar_carta_atributo(elementos):
    seccion("TEST 8: Jugar carta de atributo concreto")
    asesino = Asesino(elementos)
    partida = Partida(asesino, elementos)
    idx_crimen = partida.crimenes_en_mapa()[0][0]

    partida.mazo.mano[0] = Carta(TipoCarta.ATRIBUTO_ARMA)
    res = partida.jugar_carta(0, idx_crimen)
    assert res.exito
    assert res.atributos == ["arma"]
    assert "arma" in partida.crimen(idx_crimen).campos_revelados

    # Jugar la misma carta sobre el mismo crimen debe fallar
    partida.mazo.mano[0] = Carta(TipoCarta.ATRIBUTO_ARMA)
    res2 = partida.jugar_carta(0, idx_crimen)
    assert not res2.exito
    ok("ATRIBUTO_ARMA revela arma, segundo intento bloqueado correctamente")


def test_carta_en_crimen_completo(elementos):
    seccion("TEST 9: Carta inutilizable en crimen completo")
    asesino = Asesino(elementos)
    partida = Partida(asesino, elementos)
    idx_crimen = partida.crimenes_en_mapa()[0][0]

    # Revelar todo el crimen
    partida.mazo.mano[0] = Carta(TipoCarta.INVESTIGAR_CASO)
    partida.jugar_carta(0, idx_crimen)

    # Intentar jugar otra carta sobre el mismo crimen
    partida.mazo.mano[0] = Carta(TipoCarta.INVESTIGAR_EXPEDIENTE)
    usable, motivo = partida.carta_usable_en(0, idx_crimen)
    assert not usable
    ok(f"Carta bloqueada en crimen completo: '{motivo}'")


def test_descartar_carta_partida(elementos):
    seccion("TEST 10: Descartar carta desde partida")
    asesino = Asesino(elementos)
    partida = Partida(asesino, elementos)

    exito, carta, _ = partida.descartar_carta(0)
    assert exito and carta is not None
    assert len(partida.mazo.mano) == TAMANYO_MANO

    exito2, _, motivo = partida.descartar_carta(0)
    assert not exito2
    ok(f"Descarte OK, segundo descarte bloqueado: '{motivo}'")


def test_pasar_turno(elementos):
    seccion("TEST 11: Pasar turno")
    asesino = Asesino(elementos)
    partida = Partida(asesino, elementos)
    acc_antes = partida.acciones
    partida.pasar_turno()
    assert partida.acciones == acc_antes + 1
    ok("Pasar turno incrementa acciones")


def test_nuevo_crimen_cada_3_acciones(elementos):
    seccion("TEST 12: Nuevo crimen cada 3 cartas jugadas")
    asesino = Asesino(elementos)
    partida = Partida(asesino, elementos)
    iniciales = len(partida.crimenes_en_mapa())

    ids = [i for i, _ in partida.crimenes_en_mapa()][:3]
    for idx_crimen in ids:
        partida.mazo.mano[0] = Carta(TipoCarta.INVESTIGAR_CASO)
        partida.jugar_carta(0, idx_crimen)

    assert partida.acciones == 3
    assert len(partida.crimenes_en_mapa()) == iniciales + 1
    ok(f"Tras 3 acciones: {iniciales} → {iniciales+1} crímenes")


def test_dossier_con_cartas(elementos):
    seccion("TEST 13: Dossier incluye estadísticas de cartas")
    asesino = Asesino(elementos)
    partida = Partida(asesino, elementos, Dificultad.NORMAL)

    for idx in partida.indices_asesino_visibles():
        partida.toggle_sospechoso(idx)
    partida.acusar()

    d = partida.dossier()
    assert "cartas_jugadas" in d
    assert "regeneraciones_mazo" in d
    ok(f"Dossier OK: {d['cartas_jugadas']} cartas jugadas, "
       f"{d['regeneraciones_mazo']} regeneraciones")


if __name__ == "__main__":
    print("=" * 55)
    print("  CATCH THE KILLER — Test del Core v3")
    print("=" * 55)

    elementos = cargar()
    test_carta_meta(elementos)
    test_mazo_distribucion(elementos)
    test_mazo_jugar_y_robar(elementos)
    test_mazo_descarte_gratuito(elementos)
    test_mazo_regeneracion(elementos)
    test_jugar_carta_expediente(elementos)
    test_jugar_carta_caso(elementos)
    test_jugar_carta_atributo(elementos)
    test_carta_en_crimen_completo(elementos)
    test_descartar_carta_partida(elementos)
    test_pasar_turno(elementos)
    test_nuevo_crimen_cada_3_acciones(elementos)
    test_dossier_con_cartas(elementos)

    print("\n" + "=" * 55)
    print("  Todos los tests pasaron ✓")
    print("=" * 55)

    print("\n--- Partida de ejemplo ---")
    asesino = Asesino(elementos)
    partida = Partida(asesino, elementos)
    partida.imprimir_estado(revelar_todo=False)
