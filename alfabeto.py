# alfabeto.py

alfabetos = {
    "Σ1": {"0", "1"},
    "Σ2": {"a", "b", "c"},
    "Σ3": {
        "0",
        "1",
        "2",
        "3",
        "4",
        "5",
        "6",
        "7",
        "8",
        "9",
        "a",
        "b",
        "c",
        "d",
        "e",
        "f",
    },
}


def seleccionar_alfabeto(nombre):
    if nombre in alfabetos:
        return alfabetos[nombre]
    raise ValueError("Alfabeto no válido")


def validar_expresion_regular(expresion, alfabeto):
    operadores = {"*", "|", ".", "(", ")"}

    # Asegurarnos de que solo se usen caracteres del alfabeto y operadores
    for c in expresion:
        if c not in alfabeto and c not in operadores:
            print(f"Carácter no válido en la expresión regular: {c}")
            return False  # Retornar False si hay un carácter no permitido

    return True
