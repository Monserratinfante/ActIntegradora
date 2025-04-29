def obtener_entrada_usuario():
    alfabeto = input("Ingresa el alfabeto, separado por comas (ej. a,b): ").split(",")
    regex = input("Ingresa la expresión regular usando *, |, ., (): ")
    return alfabeto, regex