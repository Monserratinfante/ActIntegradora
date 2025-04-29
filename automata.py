from graphviz import Digraph

def a_postfijo(regex):
    # Conversión de la expresión regular a notación postfija (Shunting-yard algorithm)
    precedencia = {'*': 3, '.': 2, '|': 1, '(': 0}
    salida = []
    operadores = []

    for token in regex:
        if token.isalnum():  # Si es un símbolo del alfabeto
            salida.append(token)
        elif token == '(':
            operadores.append(token)
        elif token == ')':
            while operadores and operadores[-1] != '(':
                salida.append(operadores.pop())
            operadores.pop()  # Elimina el '('
        else:  # Operadores (*, ., |)
            while operadores and precedencia[operadores[-1]] >= precedencia[token]:
                salida.append(operadores.pop())
            operadores.append(token)

    while operadores:
        salida.append(operadores.pop())

    return ''.join(salida)

class Estado:
    def __init__(self):
        self.transiciones = {}
        self.epsilon = []

class AFN:
    def __init__(self, inicio, fin):
        self.inicio = inicio
        self.fin = fin

def construir_afn(postfijo):
    pila = []

    for token in postfijo:
        if token.isalnum():  # Si es un símbolo del alfabeto
            s1 = Estado()
            s2 = Estado()
            s1.transiciones[token] = [s2]
            pila.append(AFN(s1, s2))
        elif token == '.':  # Concatenación
            afn2 = pila.pop()
            afn1 = pila.pop()
            afn1.fin.epsilon.append(afn2.inicio)
            pila.append(AFN(afn1.inicio, afn2.fin))
        elif token == '|':  # Unión
            afn2 = pila.pop()
            afn1 = pila.pop()
            s_inicio = Estado()
            s_fin = Estado()
            s_inicio.epsilon += [afn1.inicio, afn2.inicio]
            afn1.fin.epsilon.append(s_fin)
            afn2.fin.epsilon.append(s_fin)
            pila.append(AFN(s_inicio, s_fin))
        elif token == '*':  # Estrella de Kleene
            afn = pila.pop()
            s_inicio = Estado()
            s_fin = Estado()
            s_inicio.epsilon += [afn.inicio, s_fin]
            afn.fin.epsilon += [afn.inicio, s_fin]
            pila.append(AFN(s_inicio, s_fin))

    return pila.pop()

def convertir_afn_a_afd(afn):
    def cerradura_epsilon(estados):
        stack = list(estados)
        cerradura = set(estados)

        while stack:
            estado = stack.pop()
            for e in estado.epsilon:
                if e not in cerradura:
                    cerradura.add(e)
                    stack.append(e)

        return cerradura

    def mover(estados, simbolo):
        resultado = set()
        for estado in estados:
            if simbolo in estado.transiciones:
                resultado.update(estado.transiciones[simbolo])
        return resultado

    estados_iniciales = cerradura_epsilon([afn.inicio])
    dfa_estados = {frozenset(estados_iniciales): 0}
    dfa_transiciones = {}
    dfa_finales = set()
    pendientes = [estados_iniciales]

    while pendientes:
        actual = pendientes.pop()
        actual_id = dfa_estados[frozenset(actual)]

        for simbolo in afn.inicio.transiciones.keys():
            nuevos_estados = cerradura_epsilon(mover(actual, simbolo))
            if not nuevos_estados:
                continue

            if frozenset(nuevos_estados) not in dfa_estados:
                dfa_estados[frozenset(nuevos_estados)] = len(dfa_estados)
                pendientes.append(nuevos_estados)

            dfa_transiciones[(actual_id, simbolo)] = dfa_estados[frozenset(nuevos_estados)]

        if afn.fin in actual:
            dfa_finales.add(actual_id)

    return dfa_estados, dfa_transiciones, dfa_finales

def dibujar_afd(estados, transiciones, finales):
    dot = Digraph()
    for estado, id in estados.items():
        if id in finales:
            dot.node(str(id), shape="doublecircle")
        else:
            dot.node(str(id), shape="circle")
    for (origen, simbolo), destino in transiciones.items():
        dot.edge(str(origen), str(destino), label=simbolo)
    dot.render("afd", format="png", cleanup=True)