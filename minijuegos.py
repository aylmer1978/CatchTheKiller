import random

class Mastermind:
    def __init__(self, longitud_codigo=4, max_intentos=6, num_opciones=6):
        self.longitud_codigo = longitud_codigo
        self.max_intentos = max_intentos
        self.num_opciones = num_opciones
        self.codigo = self._generar_codigo()
        
    def _generar_codigo(self):
        # Usamos random.sample para que los números del 1 al num_opciones no se repitan
        return [str(n) for n in random.sample(range(1, self.num_opciones + 1), self.longitud_codigo)]
        
    def jugar(self):
        print("\n" + "="*40)
        print("   MINIJUEGO: DESENCRIPTAR ARCHIVO")
        print("="*40)
        print(f"La pista está protegida. Descifra el código de {self.longitud_codigo} dígitos (del 1 al {self.num_opciones}).")
        print("Feedback después de cada intento:")
        print("  'O' = Número correcto y en la posición correcta (Verde).")
        print("  '-' = Número correcto, pero en la posición incorrecta (Amarillo).")
        print("  'X' = Número incorrecto.")
        print(f"Tienes {self.max_intentos} intentos para evitar que el archivo se corrompa.")
        print("-" * 40)
        
        intentos = 0
        while intentos < self.max_intentos:
            intento = input(f"\nIntento {intentos + 1}/{self.max_intentos}. Introduce {self.longitud_codigo} números juntos: ").strip()
            
            if len(intento) != self.longitud_codigo or not intento.isdigit():
                print(f"Error: Debes introducir exactamente {self.longitud_codigo} dígitos numéricos juntos (sin espacios, ej: 1234).")
                continue
                
            lista_intento = list(intento)
            if lista_intento == self.codigo:
                print("\n[!] ¡Acceso concedido! Archivo desencriptado con éxito.")
                return True
                
            feedback = self._evaluar_intento(lista_intento)
            print(f"Resultado: {' '.join(feedback)}")
            intentos += 1
            
        print(f"\n[X] ¡Acceso denegado! Te has quedado sin intentos.")
        print(f"El código de anulación era: {''.join(self.codigo)}")
        return False
        
    def _evaluar_intento(self, intento):
        codigo_temp = self.codigo.copy()
        intento_temp = intento.copy()
        feedback = ['X'] * self.longitud_codigo
        
        # Primero buscar aciertos exactos (Verde u 'O')
        for i in range(self.longitud_codigo):
            if intento_temp[i] == codigo_temp[i]:
                feedback[i] = 'O'
                codigo_temp[i] = None
                intento_temp[i] = None
                
        # Luego buscar aciertos de número pero no posición (Amarillo o '-')
        for i in range(self.longitud_codigo):
            if feedback[i] == 'X' and intento_temp[i] is not None and intento_temp[i] in codigo_temp:
                feedback[i] = '-'
                # Eliminamos uno de los números correctos encontrados para no contarlo doble
                codigo_temp[codigo_temp.index(intento_temp[i])] = None
                
        return feedback
