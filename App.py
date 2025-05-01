from flask import Flask, render_template, request
from alfabeto import validar_expresion_regular
from expresion_regular import a_postfijo
from thompson import construir_afn_postfijo
from afd import convertir_afn_a_afd, dibujar_afd  # Importamos dibujar_afd

app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def index():
    resultado_afn = ""
    resultado_afd = ""
    transiciones_afn = ""
    transiciones_afd = ""
    afd_image_path = ""  # Ruta de la imagen generada
    resultado_palabra = ""  # Inicializamos resultado_palabra

    if request.method == "POST":
        # Limpiar llaves y dividir, creando un conjunto de cadenas (símbolos)
        alfabeto_usuario_str = request.form["alfabeto"].strip("{}")
        # Manejar el caso de un alfabeto vacío o con espacios extra
        if alfabeto_usuario_str:
            alfabeto = set(s.strip() for s in alfabeto_usuario_str.split(","))
        else:
            alfabeto = set()

        expresion = request.form["expresion"]
        palabra = request.form["palabra"]

        # Mensajes de depuración
        print("Alfabeto recibido:", alfabeto)
        print("Expresión regular recibida:", expresion)
        print("Palabra a probar:", palabra)

        # Validar la expresión regular
        if validar_expresion_regular(expresion, alfabeto):
            print("Expresión regular válida. Procediendo con la conversión...")
            try:  # Usamos un try-except para capturar errores durante la conversión
                postfijo = a_postfijo(expresion)
                print(
                    f"Expresión en notación postfija: {''.join(postfijo)}"
                )  # Ver el postfijo

                afn = construir_afn_postfijo(postfijo, alfabeto)
                transiciones_afn = mostrar_transiciones_afn(afn)
                resultado_afn = "AFN creado con éxito."

                # Convertir el AFN a AFD
                afd = convertir_afn_a_afd(afn)
                transiciones_afd = mostrar_transiciones_afd(afd)
                resultado_afd = "AFD creado con éxito."

                # Dibujar el AFD y obtener la ruta de la imagen
                # Asegurarse de que el AFD no esté vacío antes de intentar dibujar
                if afd.estados:
                    afd_image_path = dibujar_afd(afd)
                    print(
                        "Imagen del AFD generada en:", afd_image_path
                    )  # Verificar si la imagen se genera
                else:
                    print("El AFD está vacío, no se generará imagen.")
                    afd_image_path = (
                        ""  # Asegurarse de que la ruta esté vacía si no hay AFD
                    )

                # Procesar la palabra con el AFD
                # Pasar el alfabeto a procesar_palabra para validación
                resultado_palabra = procesar_palabra(afd, palabra, alfabeto)
                print(
                    "Resultado de la palabra:", resultado_palabra
                )  # Ver el resultado de la palabra

            except ValueError as e:
                # Capturar errores específicos de validación del alfabeto o ER
                resultado_afd = f"Error: {e}"
                print(resultado_afd)
            except Exception as e:
                # Capturar cualquier otro error durante el proceso
                resultado_afd = f"Ocurrió un error: {e}"
                print(resultado_afd)

            return render_template(
                "index.html",
                resultado_afn=resultado_afn,
                transiciones_afn=transiciones_afn,
                resultado_afd=resultado_afd,
                transiciones_afd=transiciones_afd,
                resultado_palabra=resultado_palabra,
                afd_image_path=afd_image_path,  # Pasamos la imagen del AFD
                alfabeto=request.form[
                    "alfabeto"
                ],  # Pasar el alfabeto original para mantenerlo en el formulario
                expresion=expresion,
                palabra=palabra,
            )
        else:
            resultado_afd = (
                "La expresión regular no es válida para el alfabeto proporcionado."
            )
            print(resultado_afd)  # Error en la validación

    # Si es un GET request o si la validación de la ER falló
    return render_template(
        "index.html",
        resultado_afn=None,
        resultado_afd=resultado_afd,  # Mostrar el error si hubo
        alfabeto="",
        expresion="",
        palabra="",
    )


# Funciones para mostrar las transiciones
def mostrar_transiciones_afn(afn):
    """Genera un resumen de las transiciones del AFN."""
    visitados = set()
    transiciones = ""
    nombres_estados = {}
    contador = 0

    def obtener_nombre_estado(estado_afn):
        """Asigna un nombre legible a un estado AFN."""
        nonlocal contador
        # Usamos el objeto estado_afn directamente como clave, o su id si es necesario diferenciar instancias
        # Para depuración, id puede ser útil, pero para lógica del autómata, el objeto en sí o un hash único relacionado con él.
        # Dado que el AFN no cambia, id debería ser consistente durante una ejecución.
        # Mantendremos id por ahora para no alterar demasiado, pero es importante notar la diferencia con AFD.
        if id(estado_afn) not in nombres_estados:
            nombres_estados[id(estado_afn)] = f"q{contador}"
            contador += 1
        return nombres_estados[id(estado_afn)]

    def recorrer(estado):
        """Recorre el AFN e imprime las transiciones."""
        nonlocal transiciones
        if id(estado) in visitados:
            return
        visitados.add(id(estado))
        nombre_estado = obtener_nombre_estado(estado)

        # Ordenar transiciones por símbolo para salida consistente
        for simbolo in sorted(estado.transiciones.keys()):
            destinos = estado.transiciones[simbolo]
            for destino in destinos:
                transiciones += (
                    f"{nombre_estado} --{simbolo}--> {obtener_nombre_estado(destino)}\n"
                )
        # Ordenar transiciones epsilon
        for destino in sorted(
            estado.epsilon, key=lambda x: id(x)
        ):  # Ordenar por id para consistencia
            transiciones += f"{nombre_estado} --ε--> {obtener_nombre_estado(destino)}\n"

        # Recorrer destinos
        for simbolo, destinos in estado.transiciones.items():
            for destino in destinos:
                recorrer(destino)
        for destino in estado.epsilon:
            recorrer(destino)

    # Solo recorrer si el AFN tiene un estado inicial válido
    if afn and afn.inicio:
        recorrer(afn.inicio)
    else:
        transiciones = "AFN vacío o inválido."

    return transiciones


def mostrar_transiciones_afd(afd):
    """Genera un resumen de las transiciones del AFD."""
    transiciones = ""
    # Diccionario para asignar nombres legibles a los estados del AFD (que son frozensets)
    nombres_estados_afd = {}
    contador_afd = 0

    def obtener_nombre_estado_afd(estado_afd_frozenset):
        """Asigna un nombre legible a un estado AFD (frozenset)."""
        nonlocal contador_afd
        # Usamos el frozenset directamente como clave
        if estado_afd_frozenset not in nombres_estados_afd:
            nombres_estados_afd[estado_afd_frozenset] = f"q{contador_afd}"
            contador_afd += 1
        return nombres_estados_afd[estado_afd_frozenset]

    # Ordenar las transiciones para una salida consistente
    for (estado, simbolo), siguiente_estado in sorted(afd.transiciones.items()):
        transiciones += f"{obtener_nombre_estado_afd(estado)} --{simbolo}--> {obtener_nombre_estado_afd(siguiente_estado)}\n"

    # Agregar estado inicial y final(es) al resumen
    if afd.estado_inicial:
        transiciones += (
            f"Estado inicial: {obtener_nombre_estado_afd(afd.estado_inicial)}\n"
        )
    if afd.estados_finales:
        transiciones += (
            "Estados finales: "
            + ", ".join(
                sorted(obtener_nombre_estado_afd(s) for s in afd.estados_finales)
            )
            + "\n"
        )

    return transiciones


def procesar_palabra(afd, palabra, alfabeto):
    """Simula el procesamiento de la palabra con el AFD y verifica si contiene caracteres válidos y es aceptada."""
    # Convertir el estado inicial del AFD (que es un frozenset) a la representación que usaremos para el estado actual
    # En este caso, el estado actual *es* el frozenset.
    estado_actual_frozenset = afd.estado_inicial

    # Verificar si el AFD tiene un estado inicial
    if not estado_actual_frozenset:
        return "Error: El AFD no tiene un estado inicial."

    # Verificar si la palabra contiene caracteres fuera del alfabeto
    for simbolo in palabra:
        if simbolo not in alfabeto:
            return f"Palabra no aceptada: El carácter '{simbolo}' no está en el alfabeto {list(alfabeto)}"

    # Procesar cada símbolo de la palabra
    for simbolo in palabra:
        # La clave para buscar la transición es la tupla (estado_actual_frozenset, simbolo)
        key = (estado_actual_frozenset, simbolo)

        # Verificar si existe una transición para esta clave
        if key in afd.transiciones:
            # El siguiente estado es el frozenset almacenado en las transiciones
            estado_actual_frozenset = afd.transiciones[key]
        else:
            # Si no hay transición para el símbolo desde el estado actual, la palabra no es aceptada
            return "Palabra no aceptada"

    # Después de procesar todos los símbolos, verificar si el estado final alcanzado es uno de los estados finales del AFD
    if estado_actual_frozenset in afd.estados_finales:
        return "Palabra aceptada"
    else:
        return "Palabra no aceptada"


if __name__ == "__main__":
    app.run(debug=True)
