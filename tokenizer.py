import re

"""
MODULO: tokenizer.py

Este archivo implementa la fase de analisis lexico de una mini-calculadora.

Teoria general:
- En un compilador o interprete, el analisis lexico es la primera gran etapa.
- Su objetivo es tomar una secuencia cruda de caracteres y agruparla en unidades
  con significado llamadas tokens.
- Un token no es solo el texto encontrado, sino tambien su categoria. Por
  ejemplo, '+' pertenece a la categoria de operador de suma, mientras que
  '12.5' pertenece a la categoria de constante flotante.
- En este proyecto el analizador lexico usa expresiones regulares. Cada patron
  describe una forma valida de inicio de cadena, y el algoritmo revisa todos
  los patrones posibles para quedarse con la coincidencia mas larga.

Implicaciones de este diseno:
- El uso de "maximal munch" o "coincidencia mas larga" evita errores comunes
  cuando un lexema puede pertenecer a varias categorias compatibles.
- El orden de la tabla sigue siendo importante cuando dos coincidencias tienen
  exactamente la misma longitud y compiten semanticamente.
- Este tokenizer no construye una estructura compleja con posiciones por
  columna, por lo que su salida es sencilla y adecuada para fines academicos.
- La simplicidad favorece la comprension del pipeline completo: leer,
  reconocer, clasificar y entregar tokens al parser.
"""


# Funcion principal del analizador lexico.
#
# Teoria previa:
# - La entrada real del parser no suele ser texto puro, sino tokens.
# - Tokenizar significa recorrer el texto de izquierda a derecha y, en cada
#   posicion, determinar que categoria valida aparece primero.
# - La tabla "table" actua como especificacion formal del lenguaje en su nivel
#   lexico: define que formas textuales existen y con que nombre se reportan.
#
# Parametros:
# - input_text: ruta del archivo que contiene las expresiones a procesar.
# - table: diccionario {nombre_token: expresion_regular}.
# - print_debug: bandera opcional para mostrar el proceso interno.
#
# Salida:
# - Una lista de pares [tipo_token, lexema].
#
# Observacion importante:
# - Esta funcion no "interpreta" el significado numerico ni evalua
#   expresiones; solamente reconoce piezas validas del lenguaje.
def tokenize(input_text, table, print_debug = False):
    # Se abre el archivo de entrada completo.
    #
    # Implicacion:
    # - Para un archivo pequeno, leer todo de una vez simplifica el algoritmo.
    # - En analizadores industriales podrian usarse buffers o lectura por
    #   bloques, pero aqui se prioriza claridad conceptual.
    with open(input_text, "r") as file:
        # Se guarda el contenido completo en una sola cadena para procesarlo.
        input = file.read()

    # Modo de depuracion:
    # - Permite observar el texto original antes de tokenizar.
    # - Es util para validar que el problema no provenga del archivo.
    if print_debug:
        print(input)

    # Estructura acumuladora de la salida.
    #
    # Cada elemento agregado representa un token reconocido exitosamente.
    tokens = []

    # Bucle principal del analizador.
    #
    # Teoria:
    # - Mientras quede texto por consumir, intentamos identificar un token al
    #   inicio de la cadena restante.
    # - El uso de expresiones con '^' obliga a que la coincidencia ocurra
    #   exactamente al principio, lo cual emula el avance secuencial del lexer.
    while input != "":
        # Se eliminan espacios y tabulaciones en los extremos.
        #
        # Implicacion:
        # - Los espacios y tabs funcionan como separadores ignorables.
        # - No se elimina '\n' porque en este lenguaje el salto de linea tiene
        #   significado: separa expresiones distintas.
        input = input.strip(" \t")

        # Lista temporal de todas las categorias que lograron hacer match en la
        # posicion actual.
        matches = []

        # Se revisa cada patron lexico definido en la tabla.
        #
        # Teoria:
        # - Un mismo prefijo podria coincidir con varias categorias.
        # - Por ejemplo, "123" podria verse como entero, mientras que
        #   "123.45" solo sera flotante si el patron completo aplica.
        for label in table:
            # Expresion regular asociada a la categoria actual.
            expre = table[label]

            # Intento de coincidencia al inicio de la cadena restante.
            #
            # Nota teorica:
            # - re.match revisa desde el principio, lo cual es exactamente lo
            #   que necesitamos en un lexer secuencial.
            match_res = re.match(expre,input)

            # Si hubo coincidencia, se registra como candidata.
            if match_res != None:
                if print_debug:
                    print("match found:","\t", match_res)

                # Se almacena el nombre del token junto con el lexema concreto
                # encontrado en la entrada.
                matches.append([label, match_res.group()])

        # En depuracion mostramos todas las alternativas detectadas.
        if print_debug:
            for m in matches:
                print('matches:', m)

        if (len(matches) > 0):
            # Regla de desambiguacion: elegir la coincidencia mas larga.
            #
            # Teoria:
            # - Esta estrategia es estandar en analizadores lexicos.
            # - Si varios patrones coinciden, normalmente el token correcto es
            #   el que consume mas caracteres.
            # - Esto reduce fragmentaciones erroneas del texto.
            longest = max(matches, key = lambda x : len(x[1]))
            if print_debug:
                print('longest match:',longest)

            # El token resuelto se agrega a la salida final.
            tokens.append(longest)
        else:
            # Caso de error lexico.
            #
            # Teoria:
            # - Si ningun patron puede reconocer el prefijo actual, entonces el
            #   texto restante no pertenece al lenguaje definido.
            # - El proceso se detiene porque el parser no podria continuar con
            #   una secuencia incoherente de entrada.
            print('lexical error, unrecognized token after this token:', tokens[-1])
            print('tokens found:\n', tokens)
            break

        # Lexema reconocido en esta iteracion.
        substring = longest[1]
        if print_debug:
            print("substring:", substring)

        # Avance del puntero logico del lexer.
        #
        # En lugar de manejar un indice explicito, la implementacion reduce la
        # cadena de entrada eliminando el prefijo ya reconocido.
        input = input[len(substring):]

    # La lista resultante queda lista para la siguiente etapa:
    # el analisis sintactico.
    return tokens


# Funcion auxiliar para imprimir los tokens de forma legible.
#
# Teoria previa:
# - Una representacion visual de los tokens ayuda a verificar que el lexer
#   clasifico correctamente la entrada antes de culpar al parser.
# - Este tipo de salida es especialmente util en practicas academicas porque
#   permite ver la frontera exacta entre analisis lexico y sintactico.
def printTokens(_tokens):
    print("Token printing:")
    linea = 1
    print(f"Linea {linea}:", end="  ")
    i = 0
    while i < len(_tokens):
        token_type, lexeme = _tokens[i]

        # El token "leap" representa un salto de linea.
        #
        # Implicacion:
        # - No es solo un separador visual, sino un delimitador de expresiones
        #   que el parser de este proyecto usa para evaluar una linea a la vez.
        if token_type == "leap":
            linea += 1
            print(f"\nLinea {linea}:  ", end="  ")
            i += 1
            continue

        # Se imprime el lexema y su categoria para facilitar la inspeccion.
        print(f"{lexeme} ({token_type})", end="  ")
        i += 1
    print()