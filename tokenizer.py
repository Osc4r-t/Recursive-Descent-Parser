import re

def tokenize(input_text, table, print_debug = False):
    # intenta abrir el archivo de entrada
    try:
        with open(input_text, "r") as file:
            # si existe, lee todo su contenido
            text = file.read()

    # si no existe, lo crea con texto por defecto
    except FileNotFoundError:
        default_text = "(2 + 3**2*5)\n"

        with open(input_text, "w") as file:
            file.write(default_text)

        text = default_text

    # Estructura acumuladora de la salida.
    tokens = []

    # Bucle principal del analizador.
    while text != "":
        # Se eliminan espacios y tabulaciones en los extremos.
        text = text.strip(" \t")

        # Lista temporal de todas las categorias que lograron hacer match en la
        # posicion actual.
        matches = []

        # Se revisa cada patron lexico definido en la tabla.
        for label in table:
            # Expresion regular asociada a la categoria actual.
            expre = table[label]

            # Intento de coincidencia al inicio de la cadena restante.
            match_res = re.match(expre,text)

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
            longest = max(matches, key = lambda x : len(x[1]))
            if print_debug:
                print('longest match:',longest)

            # El token resuelto se agrega a la salida final.
            tokens.append(longest)
        else:
            # Caso de error lexico.
            print('lexical error, unrecognized token after this token:', tokens[-1])
            print('tokens found:\n', tokens)
            break

        # Lexema reconocido en esta iteracion.
        substring = longest[1]
        if print_debug:
            print("substring:", substring)

        # Avance del puntero logico del lexer.
        text = text[len(substring):]

    # La lista resultante queda lista para la siguiente etapa:
    # el analisis sintactico.
    return tokens


# Funcion auxiliar para imprimir los tokens de forma legible.
def printTokens(_tokens):
    print("Token printing:")
    linea = 1
    print(f"Linea {linea}:", end="  ")
    i = 0
    while i < len(_tokens):
        token_type, lexeme = _tokens[i]

        # El token "leap" representa un salto de linea.
        if token_type == "leap":
            linea += 1
            print(f"\nLinea {linea}:  ", end="  ")
            i += 1
            continue

        # Se imprime el lexema y su categoria para facilitar la inspeccion.
        print(f"{lexeme} ({token_type})", end="  ")
        i += 1
    print()