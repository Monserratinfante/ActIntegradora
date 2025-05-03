def validar_expresion_regular(expresion, alfabeto):
    """Valida que una expresión regular use solo símbolos válidos del alfabeto y operadores permitidos."""
    operadores = {"*", "|", ".", "(", ")"}
    
    for c in expresion:
        if c not in alfabeto and c not in operadores:
            print(f"Carácter no válido en la expresión regular: {c}")
            return False
    
    # Validación básica de paréntesis
    parentesis = 0
    for c in expresion:
        if c == "(":
            parentesis += 1
        elif c == ")":
            parentesis -= 1
        if parentesis < 0:
            print("Error: Paréntesis mal balanceados")
            return False
    
    if parentesis != 0:
        print("Error: Paréntesis mal balanceados")
        return False
    
    return True

def procesar_alfabeto(alfabeto_str):
    """Procesa una cadena de alfabeto y retorna un conjunto de símbolos válidos."""
    # Eliminar espacios y caracteres de llaves
    alfabeto_str = alfabeto_str.strip("{}").replace(" ", "")
    
    # Dividir por comas y crear conjunto
    if alfabeto_str:
        return set(simbolo.strip() for simbolo in alfabeto_str.split(","))
    return set()