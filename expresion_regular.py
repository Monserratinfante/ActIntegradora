def insertar_concatenacion(expresion):
    """Inserta el operador de concatenación (.) explícitamente en la expresión regular."""
    resultado = []
    for i in range(len(expresion)):
        resultado.append(expresion[i])
        if i + 1 < len(expresion):
            actual = expresion[i]
            siguiente = expresion[i + 1]
            # Insertar '.' si es necesario
            if (actual.isalnum() or actual == "*" or actual == ")") and \
               (siguiente.isalnum() or siguiente == "("):
                resultado.append(".")
    return "".join(resultado)

def a_postfijo(expresion):
    """Convierte una expresión regular a notación postfija usando el algoritmo Shunting-yard."""
    # Primero insertamos la concatenación explícita
    expresion = insertar_concatenacion(expresion)
    
    precedencia = {"*": 3, ".": 2, "|": 1}
    salida = []
    pila = []

    for c in expresion:
        if c.isalnum():  # Si es un símbolo del alfabeto
            salida.append(c)
        elif c == "(":
            pila.append(c)
        elif c == ")":
            while pila and pila[-1] != "(":
                salida.append(pila.pop())
            if pila:  # Eliminar el paréntesis de apertura
                pila.pop()
            else:
                raise ValueError("Paréntesis no balanceados")
        else:  # Operadores
            while pila and pila[-1] != "(" and \
                  pila[-1] in precedencia and \
                  precedencia[pila[-1]] >= precedencia[c]:
                salida.append(pila.pop())
            pila.append(c)

    # Vaciar la pila
    while pila:
        if pila[-1] == "(":
            raise ValueError("Paréntesis no balanceados")
        salida.append(pila.pop())

    return "".join(salida)