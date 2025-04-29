from automata import a_postfijo, construir_afn, convertir_afn_a_afd, dibujar_afd

if __name__ == "__main__":
    # Captura de entrada
    alfabeto = input("Introduce el alfabeto (separado por comas): ")
    regex = input("Introduce la expresión regular: ")

    # Conversión a notación postfija
    postfijo = a_postfijo(regex)

    # Construcción del AFN
    afn = construir_afn(postfijo)

    # Conversión del AFN a AFD
    estados, transiciones, finales = convertir_afn_a_afd(afn)

    # Dibujar el AFD
    dibujar_afd(estados, transiciones, finales)
    print("El AFD se ha generado y guardado como 'afd.png'.")