# Una clase tokens basica...
class Tokens:
  # Atributos
  tokens = []       # declara una lista de tokens. Se llama tokens y esta vacia
  pos = 0           # decala pos: un indice para el token actual

  # Constructor de la clase...  recibe y asigna tokens. Establece pos en indice 0
  def __init__(self, lista):
    self.tokens = lista
    self.pos = 0

  # Devuelve el token actual
  def current(self):
    return self.tokens[self.pos]  # <------ devuelve el token actual, usando pos como indice

  # Consume un token, avanzando al siguiente
  def avanza(self):
    self.pos += 1
    return self.current()  # <------ devuelve el token actual, usando pos como indice|

# Guarda errores en una lista
def addError(errors, expected, token, index):
  #print(  "ERROR index {index}", "esperaba", expected, "recibio",  token  )
  errors.append( f"ERROR en index {index}: esperaba {expected}, recibio {token}"  )



# F ->  ( E ) | const_int
def factor(tokens, errors):
    # Actualiza el token actual usando la funcion current (de la clase Token) 
    # ??  = ??  # <------ recibe tipo de token, y el valor   ['const_int', 14]
    pass
    # Si es un  '('
  
    # Avanza al siguiente token usando la funcion avanza
    
    # Llama a expr
    
    # Cuando expr termine, actualiza el token actual
    

    # Si el token actual es ahora un ')'....
    
      # Avanza al siguiente
      
    # Si no, guarda el error
    

  # O si es un 'const_int'...
  
    # Avanza al siguiente token
    

  # O si es un 'id'...
  
    # Avanza al siguiente token
    

  # Si no es ninguna de las anteriores...
  
    # guarda el error usando addError
    



# T' -> * F T' | epsilon
def termino_prime(tokens, errors):
    # Obten el token actual
    pass
    # Si el token actual es un '*'
  
    # Avanza al siguiente token
    
    # Llama a factor
    
    # Llama a termino_prime
    
  



# T -> F T'
def termino(tokens, errors):
  # Llama a factor
  pass
  # Luego llama a termino_prime
  


# E' -> + T E' | epsilon
# <expresion_prime> ::= + <termino> <expresion_prime> | <vacio>
def expr_prime(tokens, errors):
  # Obten el token actual
  pass

  # Si token actual es 'op_suma'
  
    # Avanza al siguiente token
    
    # Llama a termino
    
    # Luego llama a expr_prime
    
  # Si no, nada... se asume que es <vacio> xd



# E -> T E'
# <expresion> ::= <termino> <expresion_prime>
def expr(tokens, errors):
  # Llama a termino
  pass

  # Luego, llama a expresion prime...
 



#    Cada linea tiene un EOL al final, para evitar desbordar
#    Inicia haciendo pruebas basicas incrementales, descomentando las lineas 
lineas = [[["const_int", "10"],["const_int", "+"], ["const_int", 12], ["EOL", ""] ],
            [  ["const_int", 14], ["op_suma", "+"],  ["del_par_open","("], ["const_int", 14],  ["op_mul", "*"], ["const_int", 14], ["del_par_close", ")"], ["EOL",""]] ,  # ok
            [  ["const_int", 12] , ["op_suma", "+"], ["EOL", ""] ],
            [  ["const_int", 12] , ["op_suma", "+"], ["const_int", 12], ["EOL", ""] ],
            [  ["const_int", 12] , ["op_mul", "*"], ["const_int", 12], ["EOL", ""] ],
            [  ["op_mul", "*"], ["const_int", 12], ["EOL", ""] ],
            [  ["op_suma", "+"], ["const_int", 12], ["EOL", ""] ],
            [  ["del_par_open", "(" ], ["const_int", 12],  ["op_suma", "+"], ["const_int", 12], ["EOL", ""] ],
            ]
#   Remplaza esta version hardcoded de lineas por: 
# input = """ 14 + (14* 14 ) 
# 12 + 
# 12 +12
# 12* 12
# +12
# ( 12 + 12 
# """
# lineas = tokenizer(input) # tu codigo del tokenizer, para producir una lista en el formato del ejemplo hardcoded



for linea in lineas:
  print("\n",linea)

  tokens = Tokens(linea)
  errors = []

  expr(tokens, errors )   #    Revisa si la linea es una expresion valida


  if tokens.pos < len(tokens.tokens)-1:       #   Si no se consumio toda la linea, hubo algun token inesperado
    addError( errors, "operador", tokens.current() , tokens.pos )

  if len(errors) == 0 :
    print("OKS\n")
  else:
    for e in errors:
      print(e)


