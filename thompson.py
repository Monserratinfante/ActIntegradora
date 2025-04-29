from afn import Estado, AFN

def crear_afn_simbolo(simbolo):
    """Crea un AFN para un símbolo individual."""
    inicio = Estado()
    fin = Estado()
    inicio.transiciones[simbolo] = [fin]
    return AFN(inicio, fin)

def concatenacion(afn1, afn2):
    """Concatena dos AFNs."""
    afn1.fin.epsilon.append(afn2.inicio)
    return AFN(afn1.inicio, afn2.fin)

def union(afn1, afn2):
    """Realiza la unión de dos AFNs."""
    inicio = Estado()
    fin = Estado()
    inicio.epsilon.extend([afn1.inicio, afn2.inicio])
    afn1.fin.epsilon.append(fin)
    afn2.fin.epsilon.append(fin)
    return AFN(inicio, fin)

def estrella(afn):
    """Aplica la estrella de Kleene a un AFN."""
    inicio = Estado()
    fin = Estado()
    inicio.epsilon.extend([afn.inicio, fin])
    afn.fin.epsilon.extend([afn.inicio, fin])
    return AFN(inicio, fin)

def construir_afn_postfijo(postfijo):
    """Construye un AFN a partir de una expresión regular en notación postfija."""
    pila = []

    for c in postfijo:
        if c not in {"*", ".", "|"}:  # Si es un símbolo del alfabeto
            pila.append(crear_afn_simbolo(c))
        elif c == "*":  # Estrella de Kleene
            afn = pila.pop()
            pila.append(estrella(afn))
        elif c == ".":  # Concatenación
            afn2 = pila.pop()
            afn1 = pila.pop()
            pila.append(concatenacion(afn1, afn2))
        elif c == "|":  # Unión
            afn2 = pila.pop()
            afn1 = pila.pop()
            pila.append(union(afn1, afn2))

    return pila[0]

def eliminar_estados_vacios(afn):
    """Elimina los estados vacíos del AFN."""
    visitados = set()
    transiciones_utiles = set()

    def recorrer(estado):
        """Recorre el AFN y marca los estados útiles."""
        if estado in visitados:
            return
        visitados.add(estado)
        for simbolo, destinos in estado.transiciones.items():
            for destino in destinos:
                transiciones_utiles.add(destino)
                recorrer(destino)
        for destino in estado.epsilon:
            transiciones_utiles.add(destino)
            recorrer(destino)

    # Recorre el AFN desde el estado inicial
    recorrer(afn.inicio)

    # Elimina los estados que no están en las transiciones útiles
    def limpiar(estado):
        if estado not in transiciones_utiles:
            estado.transiciones.clear()
            estado.epsilon.clear()

    for estado in visitados:
        limpiar(estado)