from afn import Estado, AFN

def crear_afn_simbolo(simbolo, alfabeto):
    """Crea un AFN para un símbolo individual."""
    if simbolo not in alfabeto:
        raise ValueError(f"El símbolo '{simbolo}' no está en el alfabeto {alfabeto}")

    inicio = Estado()
    fin = Estado()
    inicio.transiciones[simbolo] = [fin]
    return AFN(inicio, fin, alfabeto)

def concatenacion(afn1, afn2, alfabeto):
    """Concatena dos AFNs."""
    afn1.fin.epsilon.append(afn2.inicio)
    resultado = AFN(afn1.inicio, afn2.fin, alfabeto)
    resultado.estados = afn1.estados.union(afn2.estados)
    return resultado

def union(afn1, afn2, alfabeto):
    """Realiza la unión de dos AFNs."""
    inicio = Estado()
    fin = Estado()
    
    inicio.epsilon.extend([afn1.inicio, afn2.inicio])
    afn1.fin.epsilon.append(fin)
    afn2.fin.epsilon.append(fin)
    
    resultado = AFN(inicio, fin, alfabeto)
    resultado.estados = {inicio, fin}.union(afn1.estados).union(afn2.estados)
    return resultado

def estrella(afn, alfabeto):
    """Aplica la estrella de Kleene a un AFN."""
    inicio = Estado()
    fin = Estado()
    
    inicio.epsilon.extend([afn.inicio, fin])
    afn.fin.epsilon.extend([afn.inicio, fin])
    
    resultado = AFN(inicio, fin, alfabeto)
    resultado.estados = {inicio, fin}.union(afn.estados)
    return resultado

def construir_afn_postfijo(postfijo, alfabeto):
    """Construye un AFN a partir de una expresión regular en notación postfija."""
    pila = []

    def renombrar_estados(afn):
        """Renombra los estados del AFN de manera secuencial."""
        estados = list(afn.obtener_todos_estados())
        # Remover estados inicial y final para numerarlos especialmente
        estados.remove(afn.inicio)
        estados.remove(afn.fin)
        # Ordenar los estados restantes por su id para consistencia
        estados.sort(key=lambda x: id(x))
        
        # Asignar nombres
        afn.inicio.nombre = "q0"
        for i, estado in enumerate(estados, start=1):
            estado.nombre = f"q{i}"
        afn.fin.nombre = "qf"

    for c in postfijo:
        if c not in {"*", ".", "|"}:  # Si es un símbolo del alfabeto
            if c in alfabeto:
                afn = crear_afn_simbolo(c, alfabeto)
                renombrar_estados(afn)
                pila.append(afn)
            else:
                raise ValueError(f"Símbolo {c} no válido en el alfabeto.")
        elif c == "*":
            if not pila:
                raise ValueError("Expresión mal formada: operador * sin operando")
            afn = pila.pop()
            nuevo_afn = estrella(afn, alfabeto)
            renombrar_estados(nuevo_afn)
            pila.append(nuevo_afn)
        elif c == ".":
            if len(pila) < 2:
                raise ValueError("Expresión mal formada: operador . necesita dos operandos")
            afn2 = pila.pop()
            afn1 = pila.pop()
            nuevo_afn = concatenacion(afn1, afn2, alfabeto)
            renombrar_estados(nuevo_afn)
            pila.append(nuevo_afn)
        elif c == "|":
            if len(pila) < 2:
                raise ValueError("Expresión mal formada: operador | necesita dos operandos")
            afn2 = pila.pop()
            afn1 = pila.pop()
            nuevo_afn = union(afn1, afn2, alfabeto)
            renombrar_estados(nuevo_afn)
            pila.append(nuevo_afn)

    if not pila:
        raise ValueError("La expresión está vacía")
    if len(pila) > 1:
        raise ValueError("Expresión mal formada: sobran operandos")

    afn_final = pila[0]
    afn_final.limpiar_estados_no_alcanzables()
    renombrar_estados(afn_final)
    
    return afn_final