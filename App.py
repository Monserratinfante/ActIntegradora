from flask import Flask, render_template, request
from alfabeto import validar_expresion_regular, procesar_alfabeto
from expresion_regular import a_postfijo
from thompson import construir_afn_postfijo
from afd import convertir_afn_a_afd, dibujar_afd

app = Flask(__name__)

def mostrar_transiciones_afn(afn):
    """Genera un resumen de las transiciones del AFN."""
    transiciones = []
    visitados = set()

    def recorrer(estado):
        if estado in visitados:
            return
        visitados.add(estado)

        # Transiciones normales
        for simbolo, destinos in sorted(estado.transiciones.items()):
            for destino in destinos:
                transiciones.append(f"{estado} --{simbolo}--> {destino}")

        # Transiciones epsilon
        for destino in sorted(estado.epsilon, key=lambda x: x.nombre if x.nombre else str(id(x))):
            transiciones.append(f"{estado} --ε--> {destino}")

        # Recorrer destinos
        for destinos in estado.transiciones.values():
            for destino in destinos:
                recorrer(destino)
        for destino in estado.epsilon:
            recorrer(destino)

    recorrer(afn.inicio)
    return "\n".join(sorted(transiciones))

def mostrar_transiciones_afd(afd):
    """Genera un resumen de las transiciones del AFD."""
    transiciones = []
    
    # Agregar transiciones ordenadas
    for (estado, simbolo), siguiente_estado in sorted(afd.transiciones.items(), 
                                                    key=lambda x: (afd.obtener_nombre_estado(x[0][0]), x[0][1])):
        transiciones.append(f"{afd.obtener_nombre_estado(estado)} --{simbolo}--> {afd.obtener_nombre_estado(siguiente_estado)}")

    # Agregar información de estados especiales
    transiciones.append(f"\nEstado inicial: {afd.obtener_nombre_estado(afd.estado_inicial)}")
    estados_finales = sorted(afd.obtener_nombre_estado(estado) for estado in afd.estados_finales)
    transiciones.append(f"Estados finales: {', '.join(estados_finales)}")
    if afd.estado_trampa in afd.estados:
        transiciones.append(f"Estado trampa: {afd.obtener_nombre_estado(afd.estado_trampa)}")

    return "\n".join(transiciones)

def procesar_palabra(afd, palabra, alfabeto):
    """Simula el procesamiento de una palabra en el AFD."""
    estado_actual = afd.estado_inicial

    if not estado_actual:
        return "Error: El AFD no tiene un estado inicial."

    # Verificar si la palabra contiene caracteres fuera del alfabeto
    for simbolo in palabra:
        if simbolo not in alfabeto:
            return f"Palabra no aceptada: El carácter '{simbolo}' no está en el alfabeto {list(alfabeto)}"

    # Procesar cada símbolo de la palabra
    recorrido = [f"Estado inicial: {afd.obtener_nombre_estado(estado_actual)}"]
    
    for i, simbolo in enumerate(palabra):
        key = (estado_actual, simbolo)
        
        if key not in afd.transiciones:
            recorrido.append(f"No hay transición válida para el símbolo '{simbolo}' desde el estado {afd.obtener_nombre_estado(estado_actual)}")
            return "Palabra no aceptada\n" + "\n".join(recorrido)
            
        estado_actual = afd.transiciones[key]
        recorrido.append(f"Símbolo '{simbolo}' -> {afd.obtener_nombre_estado(estado_actual)}")
        
        if estado_actual == afd.estado_trampa:
            recorrido.append("¡Llegó al estado trampa!")
            return "Palabra no aceptada\n" + "\n".join(recorrido)

    # Verificar si el estado final es de aceptación
    if estado_actual in afd.estados_finales:
        recorrido.append(f"Estado final {afd.obtener_nombre_estado(estado_actual)} es de aceptación")
        return "Palabra aceptada\n" + "\n".join(recorrido)
    else:
        recorrido.append(f"Estado final {afd.obtener_nombre_estado(estado_actual)} no es de aceptación")
        return "Palabra no aceptada\n" + "\n".join(recorrido)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        try:
            # Procesar el alfabeto
            alfabeto = procesar_alfabeto(request.form["alfabeto"])
            if not alfabeto:
                return render_template("index.html", 
                                    error="El alfabeto no puede estar vacío")

            expresion = request.form["expresion"]
            palabra = request.form["palabra"]

            # Validar la expresión regular
            if not validar_expresion_regular(expresion, alfabeto):
                return render_template("index.html", 
                                    error="La expresión regular contiene símbolos no válidos")

            # Convertir a postfijo y construir AFN
            postfijo = a_postfijo(expresion)
            afn = construir_afn_postfijo(postfijo, alfabeto)
            
            # Convertir a AFD
            afd = convertir_afn_a_afd(afn)
            
            # Generar imagen del AFD
            dibujar_afd(afd)
            
            # Procesar la palabra
            resultado_palabra = procesar_palabra(afd, palabra, alfabeto)

            return render_template("index.html",
                                resultado_afn="AFN creado exitosamente",
                                transiciones_afn=mostrar_transiciones_afn(afn),
                                resultado_afd="AFD creado exitosamente",
                                transiciones_afd=mostrar_transiciones_afd(afd),
                                resultado_palabra=resultado_palabra,
                                alfabeto=request.form["alfabeto"],
                                expresion=expresion,
                                palabra=palabra)

        except Exception as e:
            return render_template("index.html", 
                                error=f"Error: {str(e)}")

    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)