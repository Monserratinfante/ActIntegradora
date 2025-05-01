# thompson.py
from afn import Estado, AFN


def crear_afn_simbolo(simbolo, alfabeto):
    """Crea un AFN para un símbolo individual, verificando que esté en el alfabeto."""
    if simbolo not in alfabeto:
        raise ValueError(f"El símbolo '{simbolo}' no está en el alfabeto {alfabeto}")

    inicio = Estado()
    fin = Estado()
    inicio.transiciones[simbolo] = [fin]
    return AFN(inicio, fin, alfabeto)  # Pasamos el alfabeto a la creación del AFN


def concatenacion(afn1, afn2, alfabeto):
    """Concatena dos AFNs, considerando el alfabeto."""
    afn1.fin.epsilon.append(afn2.inicio)
    return AFN(afn1.inicio, afn2.fin, alfabeto)  # Pasamos el alfabeto


def union(afn1, afn2, alfabeto):
    """Realiza la unión de dos AFNs, considerando el alfabeto."""
    inicio = Estado()
    fin = Estado()
    inicio.epsilon.extend([afn1.inicio, afn2.inicio])
    afn1.fin.epsilon.append(fin)
    afn2.fin.epsilon.append(fin)
    return AFN(inicio, fin, alfabeto)  # Pasamos el alfabeto


def estrella(afn, alfabeto):
    """Aplica la estrella de Kleene a un AFN, considerando el alfabeto."""
    inicio = Estado()
    fin = Estado()
    inicio.epsilon.extend([afn.inicio, fin])
    afn.fin.epsilon.extend([afn.inicio, fin])
    return AFN(inicio, fin, alfabeto)  # Pasamos el alfabeto


def construir_afn_postfijo(postfijo, alfabeto):
    """Construye un AFN a partir de una expresión regular en notación postfija, considerando el alfabeto."""
    pila = []

    for c in postfijo:
        if c not in {"*", ".", "|"}:  # Si es un símbolo del alfabeto
            if c in alfabeto:  # Validamos si el símbolo está en el alfabeto
                pila.append(crear_afn_simbolo(c, alfabeto))  # Le pasamos el alfabeto
            else:
                raise ValueError(f"Símbolo {c} no válido en el alfabeto.")
        elif c == "*":  # Estrella de Kleene
            afn = pila.pop()
            pila.append(estrella(afn, alfabeto))
        elif c == ".":  # Concatenación
            afn2 = pila.pop()
            afn1 = pila.pop()
            pila.append(concatenacion(afn1, afn2, alfabeto))
        elif c == "|":  # Unión
            afn2 = pila.pop()
            afn1 = pila.pop()
            pila.append(union(afn1, afn2, alfabeto))

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
