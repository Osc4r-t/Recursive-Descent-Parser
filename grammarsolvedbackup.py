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
    'const_float': r"^[0-9]+\.[0-9]+\b",
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

    def current(self):
        # Devuelve el token actualmente bajo analisis.
        return self.tokens[self.pos]

    def next(self):
        # Avanza al siguiente token, pero evitando salir de rango.
        #
        # Implicacion:
        # - El parser siempre puede consultar `current()` con seguridad despues
        #   de llamar `next()`, incluso al final de la secuencia.
        if self.pos < len(self.tokens) - 1:
            self.pos += 1
        return self.current()


def addError(errors, expected, token_actual, index):
    # Constructor uniforme de mensajes de error sintactico.
    #
    # Teoria:
    # - Un parser util no solo dice "fallo", sino tambien que esperaba y que
    #   encontro realmente.
    # - Eso conecta la teoria de prediccion sintactica con retroalimentacion
    #   concreta para depurar entradas invalidas.
    errors.append(
        f"ERROR en index {index}: esperaba {expected}, recibio {token_actual}"
    )


def printErrors(errors):
    # Recorre e imprime todos los errores acumulados.
    #
    # Nota:
    # - Aunque aqui normalmente se reporta uno o pocos errores, mantener una
    #   lista permite extender el sistema a estrategias de recuperacion.
    for error in errors:
        print(error)


# Gramatica libre de contexto utilizada:
#
# E   -> T E'
# E'  -> op_add T E' | op_sub T E' | ε
# T   -> F T'
# T'  -> op_mult F T' | op_div F T' | ε
# F   -> lparen E rparen | N
# N   -> const_int | const_float | const_realn
#
# Teoria importante:
# - E representa expresiones de suma y resta.
# - T representa terminos de multiplicacion y division.
# - F representa factores, es decir, parentesis o numeros.
# - N representa literales numericos.
# - La separacion E/T/F codifica la precedencia:
#   multiplicacion y division tienen prioridad sobre suma y resta.
# - E' y T' aparecen por eliminacion de recursion izquierda, transformacion
#   necesaria para un parser descendente recursivo.
# E   -> T E'
# E'  -> op_add T E' | op_sub T E' | ε
# T   -> F T'
# T'  -> op_mult F T' | op_div F T' | ε
# F   -> lparen E rparen | N
# N   -> const_int | const_float | const_realn



def E(tokens, errors):
    # Implementacion del no terminal E.
    #
    # Teoria:
    # - E inicia reconociendo un termino T.
    # - Despues delega a E' la repeticion opcional de sumas y restas.
    # - Esta division permite modelar expresiones como:
    #   T (+ T) (+ T) (- T) ...
    value = T(tokens, errors)
    if value is None:
        return None
    return Eprime(tokens, errors, value)


def Eprime(tokens, errors, acc):
    # Implementacion del no terminal E' con acumulador.
    #
    # Teoria:
    # - E' representa "lo que sigue" despues de reconocer el primer termino.
    # - En lugar de construir un arbol y evaluarlo al final, se usa `acc` para
    #   ir cargando el resultado parcial.
    # - Esto implementa asociatividad izquierda:
    #   a - b - c se interpreta como (a - b) - c.
    if tokens.current()[0] == 'op_add':
        # Si encontramos '+', consumimos el operador y luego otro termino.
        tokens.next()
        value = T(tokens, errors)
        if value is None:
            return None
        # Se actualiza el acumulador con la suma parcial y se continua.
        return Eprime(tokens, errors, acc + value)

    elif tokens.current()[0] == 'op_sub':
        # Caso analogo para la resta.
        tokens.next()
        value = T(tokens, errors)
        if value is None:
            return None
        return Eprime(tokens, errors, acc - value)

    else:
        # Produccion epsilon.
        #
        # Teoria:
        # - Si no hay '+' ni '-', entonces E' puede derivar a vacio.
        # - En terminos practicos, significa "ya termino la cadena de sumas y
        #   restas", por lo que devolvemos el acumulado.
        return acc


def T(tokens, errors):
    # Implementacion del no terminal T.
    #
    # Teoria:
    # - Igual que E opera sobre sumas/restas, T opera sobre multiplicaciones y
    #   divisiones, que tienen mayor precedencia.
    value = F(tokens, errors)
    if value is None:
        return None
    return Tprime(tokens, errors, value)


def Tprime(tokens, errors, acc):
    # Implementacion del no terminal T' con acumulador.
    #
    # Implicacion semantica:
    # - Aqui se resuelve la precedencia alta de '*' y '/' antes de regresar a
    #   niveles superiores como E y E'.
    if tokens.current()[0] == 'op_mult':
        # Reconoce una multiplicacion y continua encadenando factores.
        tokens.next()
        value = F(tokens, errors)
        if value is None:
            return None
        return Tprime(tokens, errors, acc * value)

    elif tokens.current()[0] == 'op_div':
        # Reconoce una division.
        tokens.next()
        value = F(tokens, errors)
        if value is None:
            return None

        # Verificacion semantica adicional.
        #
        # Teoria:
        # - La gramatica por si sola puede decir que "10 / 0" tiene forma
        #   correcta, pero no puede impedir el error matematico.
        # - Esto muestra la separacion entre sintaxis y semantica.
        if value == 0:
            errors.append("ERROR: division entre cero")
            return None
        return Tprime(tokens, errors, acc / value)

    else:
        # Produccion epsilon: ya no hay mas * o / por consumir.
        return acc


def F(tokens, errors):
    # Implementacion del no terminal F.
    #
    # Teoria:
    # - Un factor puede ser un numero directo o una subexpresion entre
    #   parentesis.
    # - Los parentesis alteran la precedencia natural porque obligan a evaluar
    #   primero la expresion interna.
    if tokens.current()[0] == 'lparen':
        # Se consume '(' para entrar al contexto interno.
        tokens.next()

        # Se evalua recursivamente una expresion completa dentro del parentesis.
        value = E(tokens, errors)
        if value is None:
            return None

        if tokens.current()[0] == 'rparen':
            # Si aparece ')', la subexpresion esta bien delimitada.
            tokens.next()
            return value
        else:
            # Error clasico de balanceo de parentesis.
            addError(errors, "rparen", tokens.current(), tokens.pos)
            return None

    # Si no hay parentesis de apertura, F debe ser un numero.
    return N(tokens, errors)


def N(tokens, errors):
    # Implementacion del no terminal N.
    #
    # Teoria:
    # - Este no terminal concentra las constantes numericas validas.
    # - La separacion entre entero, flotante y notacion cientifica existe a
    #   nivel lexico, pero semanticamente aqui todas representan un numero.
    token_type, lexeme = tokens.current()

    if token_type == 'const_int':
        # Un entero se convierte con `int` para preservar su naturaleza.
        tokens.next()
        return int(lexeme)

    elif token_type == 'const_float' or token_type == 'const_realn':
        # Flotantes y notacion cientifica se convierten con `float`.
        #
        # Implicacion:
        # - A partir de este punto ambos se tratan con la misma semantica
        #   numerica dentro de Python.
        tokens.next()
        return float(lexeme)

    else:
        # Si el token actual no es numerico, la produccion N falla.
        addError(errors, "const_int o const_float o const_realn", tokens.current(), tokens.pos)
        return None


def evaluate_expression(token_list, line_number):
    # Evalua una sola linea de tokens como una expresion independiente.
    #
    # Teoria:
    # - El archivo puede contener varias expresiones, una por linea.
    # - Por eso aqui se encapsula el flujo completo de parsear, validar fin de
    #   entrada y reportar resultado o error.
    errors = []
    stream = Tokens(token_list)

    # El analisis comienza en el simbolo inicial de la gramatica: E.
    result = E(stream, errors)

    if result is None:
        print(f"Linea {line_number}: error")
        printErrors(errors)
        return

    if stream.current()[0] != 'EOF':
        # Si quedaron tokens sin consumir, entonces la expresion tiene basura
        # sintactica al final aunque el prefijo inicial fuera valido.
        addError(errors, "EOF", stream.current(), stream.pos)
        print(f"Linea {line_number}: error")
        printErrors(errors)
        return

    # Caso exitoso: la expresion fue valida y completamente consumida.
    print(f"Linea {line_number}: {result}")


def process_lines(all_tokens):
    # Separa la secuencia global de tokens en expresiones por linea.
    #
    # Teoria:
    # - El token `leap` actua como delimitador externo entre expresiones.
    # - Esta estrategia permite que el lexer procese un archivo completo y que
    #   luego el parser evalue cada linea como una unidad independiente.
    current_line_tokens = []
    line_number = 1

    for tok in all_tokens:
        if tok[0] == 'leap':
            # Al llegar a un salto de linea, se procesa la expresion acumulada.
            if len(current_line_tokens) > 0:
                evaluate_expression(current_line_tokens, line_number)
            else:
                # Se contempla explicitamente el caso de linea vacia.
                print(f"Linea {line_number}: vacia")
            current_line_tokens = []
            line_number += 1
        else:
            current_line_tokens.append(tok)

    if len(current_line_tokens) > 0:
        # Procesa la ultima linea si el archivo no termina en salto de linea.
        evaluate_expression(current_line_tokens, line_number)


if __name__ == "__main__":
    # Punto de entrada del programa cuando se ejecuta directamente.
    #
    # Flujo general:
    # 1. Ya se tokenizo `calc.txt`.
    # 2. Ya se imprimieron los tokens reconocidos.
    # 3. Aqui se recorren las lineas y se evalua cada expresion.
    print("\nResultados:")
    print("--------------------")
    process_lines(parsed_tokens)
