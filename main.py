# main.py
from alfabeto import seleccionar_alfabeto, validar_expresion_regular
from expresion_regular import a_postfijo
from thompson import construir_afn_postfijo
from afd import convertir_afn_a_afd, imprimir_afd


def imprimir_afn(afn):
    """Imprime las transiciones del AFN con nombres legibles para los estados."""
    visitados = set()
    nombres_estados = {}  # Diccionario para asignar nombres legibles a los estados
    contador = 0

    def obtener_nombre_estado(estado):
        """Asigna un nombre legible a un estado."""
        nonlocal contador
        if estado not in nombres_estados:
            nombres_estados[estado] = f"q{contador}"
            contador += 1
        return nombres_estados[estado]

    def recorrer(estado):
        """Recorre el AFN e imprime las transiciones."""
        if estado in visitados:
            return
        visitados.add(estado)
        nombre_estado = obtener_nombre_estado(estado)
        print(f"Estado {nombre_estado}:")
        for simbolo, destinos in estado.transiciones.items():
            for destino in destinos:
                print(
                    f"  {nombre_estado} --{simbolo}--> {obtener_nombre_estado(destino)}"
                )
        for destino in estado.epsilon:
            print(f"  {nombre_estado} --ε--> {obtener_nombre_estado(destino)}")
        for simbolo, destinos in estado.transiciones.items():
            for destino in destinos:
                recorrer(destino)
        for destino in estado.epsilon:
            recorrer(destino)

    print("Transiciones del AFN:")
    recorrer(afn.inicio)
    print(f"Estado inicial: {obtener_nombre_estado(afn.inicio)}")
    print(f"Estado final: {obtener_nombre_estado(afn.fin)}")


# Solicitar al usuario el alfabeto
alfabeto_usuario = input(
    "Introduce el alfabeto (símbolos separados por comas): "
).split(",")
alfabeto = set(alfabeto_usuario)

# Solicitar al usuario la expresión regular
expresion = input("Introduce la expresión regular: ")

# Validar la expresión regular
if validar_expresion_regular(expresion, alfabeto):
    # Convertir la expresión regular a notación postfija
    postfijo = a_postfijo(expresion)
    print(f"Expresión en notación postfija: {''.join(postfijo)}")

    # Construir el AFN (pasando el alfabeto)
    afn = construir_afn_postfijo(postfijo, alfabeto)
    print("AFN creado con éxito.")

    # Imprimir las transiciones del AFN
    imprimir_afn(afn)

    # Convertir el AFN a AFD
    afd = convertir_afn_a_afd(afn)
    print("AFD creado con éxito.")

    # Imprimir el AFD
    imprimir_afd(afd)

else:
    print("La expresión regular contiene símbolos no válidos en el alfabeto.")
