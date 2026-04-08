import tokenizer as token

# Tabla de expresiones regulares usada por el analizador lexico.
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
parsed_tokens = token.tokenize("calc.txt", re_table, False)
token.printTokens(parsed_tokens)
class Tokens:

    def __init__(self, lista):
        # Se copia la lista recibida para evitar modificar accidentalmente la
        # referencia externa que llega desde otras partes del programa.
        # Ademas, se agrega el token EOF artificial.
        self.tokens = lista[:] + [['EOF', '$']]
        self.pos = 0

    def current(self,value):
        # Devuelve el token actualmente bajo analisis.
        if (value == "token"):
            p = 0
        elif (value == "lexeme"):
            p = 1
        else:
            print("wrong value received")
            exit(1)
        return self.tokens[self.pos][p]


    def next(self):
        # Avanza al siguiente token, pero evitando salir de rango.
        print(f"Avanzando a token: {self.current('token')}")  # Depuracion: muestra el token al avanzar
        if self.pos < len(self.tokens) - 1:
            self.pos += 1
        return self.current("token")


def printError(expected, token_actual, index):
    # Constructor uniforme de mensajes de error sintactico.
    print(
        f"ERROR en index {index}: esperaba {expected}, recibio {token_actual}"
    )
    exit(1)


# Gramatica libre de contexto utilizada:
# implementacion de gramatica con saltos de linea para evaluar expresiones una por linea.
# S  -> E leap S | E EOF | ε

# E  -> T E'
# E' -> op_add T E' | op_sub T E' | ε

# T  -> P T'
# T' -> op_mult P T' | op_div P T' | op_mod P T' | ε

# P  -> F P'
# P' -> op_expo P | ε

# F  -> op_sub F | op_sqrt lparen E rparen | lparen E rparen | N

# N  -> const_int | const_float | const_realn | const_hex


def S(tokens):
    # mientras no se llegue al final del archivo sigue evaluando lineas
    while tokens.current("token") != "EOF":
        # evalua una expresion completa y guarda su valor
        value = E(tokens)

        # si termina en salto de linea, imprime resultado y sigue con la siguiente
        if tokens.current("token") == "leap":
            print(value)
            tokens.next()

        # si termina en EOF, imprime resultado y termina
        elif tokens.current("token") == "EOF":
            print(value)
            return True

        # cualquier otro token sobrante es error
        else:
            printError("leap o EOF", tokens.current("token"), tokens.pos)

    return True

def E(tokens):
    # recibe el valor de T()
    value = T(tokens)
    # revisa si hay mas sumas o restas
    return Eprime(tokens,value)

def Eprime(tokens,acc):
    # revisa si el token es de una suma
    if tokens.current("token") == "op_add":
        # si lo es lo consume
        tokens.next()
        # suma el acumulador por el valor
        value = acc + T(tokens)
        # revisa si hay otra operacion del mismo nivel
        return Eprime(tokens, value)
    
    # revisa si el token es de una resta
    elif tokens.current("token") == "op_sub":
        # si lo es lo consume
        tokens.next()
        # resta el acumulador por el valor
        value = acc - T(tokens)
        # revisa si hay otra operacion del mismo nivel
        return Eprime(tokens, value)
    else:
        #si ya no hay devuelve el acumulador
        return acc

def T(tokens):
    # recibe valor de P()
    value = P(tokens)
    # devuelve si hay mult, div o mod con Tprime()
    return Tprime(tokens, value)


def Tprime(tokens,acc):
    # revisa si el token es de una multiplicacion
    if tokens.current("token") == "op_mult":
        # si lo es lo consume
        tokens.next()
        # multiplica el acumulador por el valor
        value = acc * P(tokens)
        # revisa si hay otra operacion del mismo nivel
        return Tprime(tokens, value)
    
    # revisa si el token es de una division
    elif tokens.current("token") == "op_div":
        # si lo es lo consume
        tokens.next()
        # multiplica el acumulador por el valor
        value = acc / P(tokens)
        # revisa si hay otra operacion del mismo nivel
        return Tprime(tokens, value)

    # revisa si el token es de un modulo
    elif tokens.current("token") == "op_mod":
        # si lo es lo consume
        tokens.next()
        # multiplica el acumulador por el valor
        value = acc % P(tokens)
        # revisa si hay otra operacion del mismo nivel
        return Tprime(tokens, value)
    else:
        #si ya no hay devuelve el acumulador
        return acc



def P(tokens):
    # recibe valor de F()
    value = F(tokens)
    # revisa si hay exponente con Pprime()
    return Pprime(tokens, value)

def Pprime(tokens, acc):
    # revisa si hay un op_expo
    if tokens.current("token") == "op_expo":
        # si lo hay consume token
        tokens.next()
        # calcula el exponente de manera que quede asociativo a la derecha
        expo =  P(tokens)
        # devuelve el acumulador expuesto al exponente
        return acc ** expo
    # sino toma el caso que no haya exponente y solo devuelve el acumulador
    else:
        return acc

def F (tokens):
    # revisa si el token es un op_sub
    if tokens.current("token") == "op_sub":
        # si lo es consume token
        tokens.next()
        # devuelve como negativo otra vez un F
        return -F(tokens)
    # si no lo es, revisa si es un sqrt
    elif tokens.current("token") == "op_sqrt":
        # si lo es consume token
        tokens.next()
        # revisa si sigue un lparen
        if tokens.current("token") == "lparen":
            # si lo es consume token
            tokens.next()
            # toma el valor de una expresion y lo guarda
            value = E(tokens)**(1/2)
            # revisa si sigue despues de la expresion un rparen
            if tokens.current("token") == "rparen":
                # si lo es consume token
                tokens.next()
                # si todo es correcto devuelve el sqrt 
                return value
            # caso de rparen incorrecto
            else:
                printError( 'rparen', tokens.current("token"), tokens.pos)
        # caso de lparen incorrecto
        else:
            printError( 'lparen', tokens.current("token"), tokens.pos)
    # revisa si el token es un lparen
    elif tokens.current("token") == "lparen":
        # si lo es consume token
        tokens.next()
        # guarda el valor de la expresion
        value = E(tokens)
        # revisa si el token que sigue es un rparen
        if tokens.current("token") == "rparen":
            # si lo es consume token
            tokens.next()
            # devuelve el valor ya que todo esta bien escrito
            return value
        # caso donde rparen esta mal
        else:
            printError( 'rparen', tokens.current("token"), tokens.pos)
    # revisa si el token es un numero
    return N(tokens)


def N(tokens):
    # revisa si el token es una constante entera
    if tokens.current("token") == "const_int":
        # si lo es convierte el lexema a int y lo guarda
        value = int(tokens.current("lexeme"))
        # consume token
        tokens.next()
        # devuelve el valor entero
        return value
    # revisa si el token es una constante flotante o real con notacion cientifica
    elif tokens.current("token") in ["const_float", "const_realn"]:
        # si lo es convierte el lexema a float y lo guarda
        value = float(tokens.current("lexeme"))
        # consume token
        tokens.next()
        # devuelve el valor flotante
        return value
    # revisa si el token es una constante hexadecimal
    elif tokens.current("token") == "const_hex":
        # si lo es convierte el lexema a entero base 16 y lo guarda
        value = int(tokens.current("lexeme"),16)
        # consume token
        tokens.next()
        # devuelve el valor hexadecimal ya convertido
        return value
    # caso donde no se encontro ninguna constante numerica valida
    else:
        printError('numeric_const', tokens.current("token"), tokens.pos)

if __name__ == "__main__":
    # inicializacion de la lista de errores y el flujo de tokens para el parser.
    tokens = Tokens(parsed_tokens)
    S(tokens)
        