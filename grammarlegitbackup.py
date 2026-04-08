import tokenizer as token

"""
MODULO: grammar.py

Este archivo implementa dos ideas al mismo tiempo:

1. Analisis sintactico recursivo descendente.
2. Evaluacion semantica inmediata de expresiones aritmeticas.

Teoria general:
- Una vez que el analizador lexico produce tokens, el parser verifica si esa
  secuencia respeta la gramatica del lenguaje.
- En este caso se usa un parser descendente recursivo. Cada no terminal de la
  gramatica se modela como una funcion de Python.
- El parser no solo valida la forma; tambien calcula el resultado numerico en
  el mismo recorrido. Esto convierte al parser en una especie de interprete.

Implicaciones de este enfoque:
- Es muy didactico porque conecta directamente la teoria de gramaticas con la
  implementacion.
- La precedencia de operadores no se programa con "if" arbitrarios; se obtiene
  de la propia estructura de la gramatica.
- La asociatividad izquierda de +, -, * y / se implementa mediante las
  funciones Eprime y Tprime con acumuladores.
- El diseno es ideal para expresiones aritmeticas simples, aunque para
  lenguajes mas grandes convendrian estructuras mas robustas como ASTs.
"""


# Tabla de expresiones regulares usada por el analizador lexico.
#
# Teoria:
# - Esta tabla define el vocabulario terminal del lenguaje.
# - Cada clave sera el tipo de token, y cada valor describe con una expresion
#   regular la forma textual aceptada para esa categoria.
# - Todos los patrones estan anclados con '^' para forzar coincidencia al
#   inicio de la cadena restante, propiedad esencial en un lexer secuencial.
re_table = {
    'op_add': r"^\+",
    'op_sub': r"^-",
    'op_mult': r"^\*",
    'op_div': r"^/",
    'op_mod': r"^%",
    'op_expo': r"^\*\*",
    'op_sqrt': r"^sqrt",
    'const_float': r"^[0-9]+\.[0-9]+\b",

    'const_realn': r'^([0-9]+(\.[0-9]+)?|\.[0-9]+)([eE][+-]?[0-9]+)\b',
    'const_hex': r"^0x[0-9a-fA-F]+\b",
    'const_int': r"^[0-9]+\b",
    'lparen': r"^\(",
    'rparen': r"^\)",
    'leap': r"^\n"
}

# Tokenizacion inicial del archivo de entrada.
#
# Implicacion:
# - El archivo `calc.txt` se analiza antes de ejecutar el parser principal.
# - Esta decision simplifica el flujo del programa y permite inspeccionar los
#   tokens antes de pasar al analisis sintactico.
parsed_tokens = token.tokenize("calc.txt", re_table, False)
token.printTokens(parsed_tokens)
class Tokens:
    """
    Abstraccion minima de un flujo de tokens.

    Teoria:
    - Un parser necesita avanzar de token en token sin manipular indices en
      cada funcion.
    - Esta clase encapsula ese comportamiento con una posicion actual y dos
      operaciones fundamentales: consultar el token presente y avanzar.

    Implicaciones:
    - Hace que las funciones del parser sean mas legibles.
    - Permite agregar explicitamente un token EOF al final para detectar si la
      expresion se consumio por completo.
    """

    def __init__(self, lista):
        # Se copia la lista recibida para evitar modificar accidentalmente la
        # referencia externa que llega desde otras partes del programa.
        #
        # Ademas, se agrega el token EOF artificial.
        # Teoria:
        # - EOF ("end of file" o fin de entrada) es una convencion clasica en
        #   parsers para indicar que no quedan simbolos por leer.
        # - Su presencia ayuda a detectar entradas parcialmente consumidas.
        self.tokens = lista[:] + [['EOF', '$']]
        self.pos = 0

    def current(self,value = "token"):
        # Devuelve el token actualmente bajo analisis.
        return self.tokens[self.pos][0 if value == "token" else 1]


    def next(self):
        # Avanza al siguiente token, pero evitando salir de rango.
        #
        # Implicacion:
        # - El parser siempre puede consultar `current()` con seguridad despues
        #   de llamar `next()`, incluso al final de la secuencia.
        print(f"Avanzando a token: {self.current()}")  # Depuracion: muestra el token al avanzar
        if self.pos < len(self.tokens) - 1:
            self.pos += 1
        return self.current()


def printError(expected, token_actual, index):
    # Constructor uniforme de mensajes de error sintactico.
    #
    # Teoria:
    # - Un parser util no solo dice "fallo", sino tambien que esperaba y que
    #   encontro realmente.
    # - Eso conecta la teoria de prediccion sintactica con retroalimentacion
    #   concreta para depurar entradas invalidas.
    print(
        f"ERROR en index {index}: esperaba {expected}, recibio {token_actual}"
    )
    exit(1)


# Gramatica libre de contexto utilizada:
# implementacion de gramatica con saltos de linea para evaluar expresiones una por linea.
# S  -> E leap S | E | ε

# E  -> T E'
# E' -> op_add T E' | op_sub T E' | ε

# T  -> P T'
# T' -> op_mult P T' | op_div P T' | op_mod P T' | ε

# P  -> F P'
# P' -> op_expo P | ε

# F  -> op_sub F | op_sqrt lparen E rparen | lparen E rparen | N

# N  -> const_int | const_float | const_realn | const_hex


# no implementation, just parsing
def S(tokens):
    # El no terminal S es el punto de entrada del parser. Maneja la estructura general de la entrada, que puede consistir en varias expresiones separadas por saltos de linea.
    if E(tokens):
        # Si E se resuelve correctamente, se verifica si el siguiente token es un salto de linea (leap). Si es asi, se consume ese token y se llama recursivamente a S para procesar la siguiente expresion. Esto permite manejar multiples lineas de entrada.
        if tokens.current("token") == "leap":
            print("linea completa")
            tokens.next()
            if tokens.current("token") == "EOF":
                return True
            return S(tokens)
        # Si no hay un salto de linea, se devuelve True para indicar que la produccion se cumplio. Esto cubre el caso de una sola expresion sin saltos de linea.
        elif (tokens.current("token") == "EOF"):
            return True
        else:
            return False
    # Si E no se resuelve, se reporta un error sintactico indicando que se esperaba una expresion.
    else:
        printError( 'E', tokens.current("token"), tokens.pos)


def E(tokens):
    # El no terminal E se encarga de manejar la precedencia de los operadores de suma y resta. Se implementa con una produccion que llama a T para resolver el primer termino, y luego a E' para manejar los operadores adicionales.
    if T(tokens):
        # Si T se resuelve correctamente, se llama a E' para verificar si hay operadores de suma o resta adicionales. E' se encarga de manejar la asociatividad izquierda de estos operadores.
        return Eprime(tokens)
    # Si T no se resuelve, se reporta un error sintactico indicando que se esperaba un termino.
    else:
        printError( 'T', tokens.current("token"), tokens.pos)

def Eprime(tokens):
    # El no terminal E' maneja la asociatividad izquierda de los operadores de suma y resta.
    if tokens.current("token") == 'op_add':
        tokens.next()
        # Si el token actual es un operador de suma, se consume ese token y se llama a T para resolver el siguiente termino.
        if T(tokens):
            # Si T se resuelve correctamente, se llama recursivamente a E' para verificar si hay mas operadores de suma o resta.
            if Eprime(tokens):
                return True
            # Si E' no se resuelve, se reporta un error sintactico indicando que se esperaba un operador de suma o resta.
            else:
                printError( 'E', tokens.current("token"), tokens.pos)
        # Si T no se resuelve, se reporta un error sintactico indicando que se esperaba un termino.
        else:
            printError( 'T', tokens.current("token"), tokens.pos)
    # El caso de resta se maneja de forma similar al de suma, pero con el token 'op_sub'.
    elif tokens.current("token") == 'op_sub':
        tokens.next()
        if T(tokens):
            if Eprime(tokens):
                return True
            else:
                printError( 'E', tokens.current("token"), tokens.pos)
        else:
            printError( 'T', tokens.current("token"), tokens.pos)
    # Si no se cumple ninguna de las producciones anteriores, se devuelve True para indicar que la produccion se cumplio.
    else:
        return True

def T(tokens):
    # El no terminal T se encarga de manejar la precedencia de los operadores de multiplicacion, division y modulo.
    if P(tokens):
        # Si P se resuelve correctamente, se llama a T' para verificar si hay operadores de multiplicacion, division o modulo.
        return Tprime(tokens)
    # Si P no se resuelve, se reporta un error sintactico indicando que se esperaba un factor.
    else:
        printError( 'P', tokens.current("token"), tokens.pos)

def Tprime(tokens):
    # El no terminal T' maneja la asociatividad izquierda de los operadores de multiplicacion, division y modulo.
    if tokens.current("token") == 'op_mult':
        # Si el token actual es un operador de multiplicacion, se consume ese token y se llama a P para resolver el siguiente factor.
        tokens.next()
        # Si P se resuelve correctamente, se llama recursivamente a T' para verificar si hay mas operadores de multiplicacion o division.
        if P(tokens):
            # Si T' se resuelve correctamente, se devuelve True para indicar que la produccion se cumplio.
            if Tprime(tokens):

                return True
            # Si T' no se resuelve, se reporta un error sintactico indicando que se esperaba un operador de multiplicacion, division o modulo.
            else:
                printError( 'T', tokens.current("token"), tokens.pos)
        # Si P no se resuelve, se reporta un error sintactico indicando que se esperaba un factor.
        else:
            printError( 'P', tokens.current("token"), tokens.pos)
    # El caso de division se maneja de forma similar al de multiplicacion, pero con el token 'op_div'. 
    elif tokens.current("token") == 'op_div':
        tokens.next()
        if P(tokens):
            if Tprime(tokens):

                return True
            else:
                printError( 'T', tokens.current("token"), tokens.pos)
        else:
            printError( 'P', tokens.current("token"), tokens.pos)
    # El caso de modulo se maneja de forma similar al de multiplicacion, pero con el token 'op_mod'.
    elif tokens.current("token") == 'op_mod':
        tokens.next()
        if P(tokens):
            if Tprime(tokens):

                return True
            else:
                printError( 'T', tokens.current("token"), tokens.pos)
        else:
            printError( 'P', tokens.current("token"), tokens.pos)
    # Si no se cumple ninguna de las producciones anteriores, se devuelve True para indicar que la produccion se cumplio.
    else:
        return True

def P(tokens):
    # El no terminal P se encarga de manejar la precedencia del operador de potencia.
    if F(tokens):
        # Si F se resuelve correctamente, se llama a P' para verificar si hay una potencia.
        return Pprime(tokens)
    # Si F no se resuelve, se reporta un error sintactico indicando que se esperaba una expresion o un numero.
    else:
        printError( 'F', tokens.current("token"), tokens.pos)

def Pprime(tokens):
    # El no terminal P' tiene una produccion recursiva a la derecha para manejar la asociatividad del operador de potencia.
    if tokens.current("token") == 'op_expo':
        tokens.next()
        if P(tokens):

            return True
        else:
            printError( 'P', tokens.current("token"), tokens.pos)
    else:

        return True
def F(tokens):
    # El no terminal F tiene varias producciones, por lo que se implementa con "if" para decidir cual aplicar.
    if tokens.current("token") == 'op_sub':
        tokens.next()
        if F(tokens):

            return True
        else:
            printError( 'F', tokens.current("token"), tokens.pos)
    # El caso de raiz cuadrada se maneja con una produccion mas compleja que incluye parentesis y una expresion interna.
    elif tokens.current("token") == 'op_sqrt':
        tokens.next()
        if tokens.current("token") == 'lparen':
            tokens.next()
            if E(tokens):
                if tokens.current("token") == 'rparen':
                    tokens.next()
                    return True
                else:
                    printError( 'rparen', tokens.current("token"), tokens.pos)
            else:
                printError( 'E', tokens.current("token"), tokens.pos)
        else:
            printError( 'lparen', tokens.current("token"), tokens.pos)
    # El caso de expresion entre parentesis se maneja con una produccion que espera un E entre lparen y rparen.
    elif tokens.current("token") == 'lparen':
        tokens.next()
        if E(tokens):
            if tokens.current("token") == 'rparen':
                tokens.next()
                
                return True
            else:
                printError( 'rparen', tokens.current("token"), tokens.pos)
        else:
            printError( 'E', tokens.current("token"), tokens.pos)
    # Si no se cumple ninguna de las producciones anteriores, se intenta reconocer un numero con el no terminal N.
    else:
        return N(tokens)


def N(tokens):
    if (tokens.current("token") in ["const_int", "const_float", "const_realn", "const_hex"]):
        tokens.next()
        
        return True
    else:
        printError( 'numeric_const', tokens.current("token"), tokens.pos)

if __name__ == "__main__":
    # inicializacion de la lista de errores y el flujo de tokens para el parser.

    tokens = Tokens(parsed_tokens)
    # Aqui se llamaria a la funcion principal del parser, que no se muestra en este fragmento.
    if (S(tokens)):
        print("Parsing successful!")
    