from crimen import Crimen
import random

def _calcular_diferencias(c1, c2):
    return sum(1 for a, b in zip(c1, c2) if a != b)

def generar_crimenes_asesino(asesino, victimas, armas, lugares, otros):
    """ Genera los crímenes del asesino, asegurando que compartan 2 rasgos (su firma) y difieran en el resto """
    crimenes = []
    
    # Seleccionamos aleatoriamente 2 atributos que formarán la "firma" del asesino
    atributos = ["victima", "arma", "lugar", "otro"]
    firma = random.sample(atributos, 2)
    
    combinaciones_generadas = []
    
    while len(combinaciones_generadas) < 3:
        c_tuple = (
            asesino.victima if "victima" in firma else random.choice(victimas),
            asesino.arma if "arma" in firma else random.choice(armas),
            asesino.lugar if "lugar" in firma else random.choice(lugares),
            asesino.otro if "otro" in firma else random.choice(otros)
        )
        
        # Debe haber al menos 2 diferencias con otros crímenes ya generados para el asesino
        valido = True
        for ya_generado in combinaciones_generadas:
            if _calcular_diferencias(c_tuple, ya_generado) < 2:
                valido = False
                break
                
        if valido:
            combinaciones_generadas.append(c_tuple)
            crimen = Crimen(*c_tuple)
            crimen.marcado_asesino = True
            crimenes.append(crimen)

    return crimenes


def generar_crimenes_no_asesino(asesino, victimas, armas, lugares, otros, crimenes_existentes, num_crimenes_no_asesino):
    """ Genera crímenes adicionales, asegurando que tengan al menos 2 diferencias con cualquier otro crimen """
    crimenes = []
    todas_combinaciones = [(c.victima, c.arma, c.lugar, c.otro) for c in crimenes_existentes]

    while len(crimenes) < num_crimenes_no_asesino:
        c_tuple = (
            random.choice(victimas),
            random.choice(armas),
            random.choice(lugares),
            random.choice(otros)
        )

        # Debe haber al menos 2 diferencias con *CUALQUIER* otro crimen generado
        valido = True
        for ya_generado in todas_combinaciones:
            if _calcular_diferencias(c_tuple, ya_generado) < 2:
                valido = False
                break
                
        if valido:
            todas_combinaciones.append(c_tuple)
            crimen = Crimen(*c_tuple)
            crimen.marcado_asesino = False
            crimenes.append(crimen)

    return crimenes
