def a_postfijo(expresion):
    """Convierte una expresión regular a notación postfija usando el algoritmo Shunting-yard."""
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
            pila.pop()  # Elimina el paréntesis de apertura
        else:  # Operadores (*, ., |)
            while pila and pila[-1] != "(" and precedencia[pila[-1]] >= precedencia[c]:
                salida.append(pila.pop())
            pila.append(c)

    while pila:
        salida.append(pila.pop())

    return "".join(salida)