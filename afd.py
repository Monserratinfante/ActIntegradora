# afd.py

import matplotlib.pyplot as plt
import networkx as nx
import os  # Importar os para crear el directorio static


class AFD:
    def __init__(self):
        # Lista de frozensets, donde cada frozenset representa un estado del AFD
        self.estados = []
        # Transiciones del AFD {(frozenset(estado_actual), simbolo) -> frozenset(estado_destino)}
        self.transiciones = {}
        # El estado inicial es un frozenset
        self.estado_inicial = None
        # Conjunto de frozensets, donde cada frozenset representa un estado final del AFD
        self.estados_finales = set()

    def __repr__(self):
        # Representación más amigable para depuración
        return f"AFD(inicial={self.estado_inicial}, finales={self.estados_finales}, num_estados={len(self.estados)})"


def epsilon_closure(estado_afn):
    """Calcula la cerradura epsilon de un estado AFN."""
    cerradura = {estado_afn}
    pila = [estado_afn]  # Usamos una pila para recorrer las transiciones epsilon

    while pila:
        actual = pila.pop()
        # Verificar si 'epsilon' existe y es iterable
        if hasattr(actual, "epsilon") and isinstance(actual.epsilon, list):
            for siguiente_estado in actual.epsilon:
                if siguiente_estado not in cerradura:
                    cerradura.add(siguiente_estado)
                    pila.append(siguiente_estado)
    return cerradura


def convertir_afn_a_afd(afn):
    """Convierte un AFN en un AFD utilizando el algoritmo de subconjuntos."""
    afd = AFD()

    # Calcular la cerradura epsilon del estado inicial del AFN y convertirla a frozenset
    estado_inicial_afn_closure = epsilon_closure(afn.inicio)
    estado_inicial_afd_frozenset = frozenset(estado_inicial_afn_closure)

    afd.estado_inicial = estado_inicial_afd_frozenset
    afd.estados.append(estado_inicial_afd_frozenset)

    # La lista de pendientes ahora contendrá frozensets
    pendientes = [estado_inicial_afd_frozenset]
    # Usamos un set para estados_procesados para búsquedas eficientes
    estados_procesados = {estado_inicial_afd_frozenset}

    while pendientes:
        estado_actual_frozenset = pendientes.pop()  # Extraemos un frozenset

        # *** CORRECCIÓN: Verificar si el estado AFD contiene el estado final del AFN ***
        if afn.fin in estado_actual_frozenset:
            afd.estados_finales.add(estado_actual_frozenset)

        # Iterar sobre los símbolos del alfabeto del AFN
        # Usar un set para el alfabeto para evitar duplicados si se pasa una lista
        for simbolo in sorted(list(afn.alfabeto)):  # Ordenar para consistencia

            siguiente_estados_afn = set()

            # Para cada estado AFN dentro del estado AFD actual (frozenset)
            for estado_afn in estado_actual_frozenset:
                # Si el símbolo es una transición desde este estado AFN
                if simbolo in estado_afn.transiciones:
                    # Agregar los estados AFN destino al conjunto temporal
                    siguiente_estados_afn.update(estado_afn.transiciones[simbolo])

            # Si se encontraron estados AFN alcanzables con este símbolo
            if siguiente_estados_afn:
                # Calcular la cerradura epsilon de los estados AFN alcanzados
                siguiente_estado_closure_afn = set()
                for estado_afn in siguiente_estados_afn:
                    siguiente_estado_closure_afn.update(epsilon_closure(estado_afn))

                # Convertir el conjunto de estados AFN a un frozenset para el estado AFD destino
                siguiente_estado_afd_frozenset = frozenset(siguiente_estado_closure_afn)

                # Si este estado AFD destino no ha sido procesado o añadido a pendientes
                if siguiente_estado_afd_frozenset not in estados_procesados:
                    afd.estados.append(siguiente_estado_afd_frozenset)
                    pendientes.append(siguiente_estado_afd_frozenset)
                    estados_procesados.add(siguiente_estado_afd_frozenset)

                # Guardamos la transición en el AFD
                afd.transiciones[(estado_actual_frozenset, simbolo)] = (
                    siguiente_estado_afd_frozenset
                )

    return afd


def dibujar_afd(afd):
    """Dibuja el AFD usando matplotlib y networkx y guarda la imagen."""

    G = nx.DiGraph()  # Crear un grafo dirigido

    # Diccionario para asignar nombres legibles (q0, q1, ...) a los frozensets de estados AFD
    nombres_estados = {}
    contador = 0

    # Asegurarse de que el estado inicial siempre sea q0 si existe
    if afd.estado_inicial:
        nombres_estados[afd.estado_inicial] = "q0"
        contador = 1  # Empezar el contador para los demás estados

    def obtener_nombre_estado(estado_frozenset):
        """Asigna un nombre legible a un estado AFD (frozenset)."""
        nonlocal contador
        if estado_frozenset not in nombres_estados:
            nombres_estados[estado_frozenset] = f"q{contador}"
            contador += 1
        return nombres_estados[estado_frozenset]

    # Añadir los estados como nodos al grafo
    # Asegurarse de añadir primero el estado inicial si existe
    if afd.estado_inicial:
        G.add_node(obtener_nombre_estado(afd.estado_inicial), is_initial=True)

    for estado_frozenset in afd.estados:
        nombre = obtener_nombre_estado(estado_frozenset)
        # Añadir nodo si no es el estado inicial (ya añadido)
        if estado_frozenset != afd.estado_inicial:
            if estado_frozenset in afd.estados_finales:
                G.add_node(nombre, is_final=True)
            else:
                G.add_node(nombre)
        # Si es el estado inicial y también es final
        elif estado_frozenset in afd.estados_finales:
            G.nodes[nombre]["is_final"] = True

    # Añadir las transiciones como aristas al grafo
    for (
        estado_origen_frozenset,
        simbolo,
    ), estado_destino_frozenset in afd.transiciones.items():
        nombre_origen = obtener_nombre_estado(estado_origen_frozenset)
        nombre_destino = obtener_nombre_estado(estado_destino_frozenset)
        G.add_edge(nombre_origen, nombre_destino, label=simbolo)  # Añadir la transición

    # Generar la visualización
    pos = nx.spring_layout(G, seed=42)  # Layout para la disposición de los nodos
    labels = nx.get_edge_attributes(G, "label")

    plt.figure(figsize=(12, 8))  # Tamaño de la imagen

    # Dibujar los nodos
    node_colors = []
    # Lista para dibujar los bordes de los nodos finales
    final_node_borders = []
    node_list = []  # Para mantener el orden de los nodos dibujados

    for node_name in G.nodes():
        node_list.append(node_name)
        if G.nodes[node_name].get("is_initial"):
            # Si es inicial y final
            if G.nodes[node_name].get("is_final"):
                node_colors.append("lightgreen")  # Color inicial-final
                final_node_borders.append(node_name)  # Añadir para dibujar doble borde
            else:
                node_colors.append("lightgreen")  # Color inicial
        elif G.nodes[node_name].get("is_final"):
            node_colors.append("salmon")  # Color final
            final_node_borders.append(node_name)  # Añadir para dibujar doble borde
        else:
            node_colors.append("lightblue")  # Color normal

    nx.draw(
        G,
        pos,
        nodelist=node_list,  # Usar la lista de nodos para asegurar el orden
        with_labels=True,
        node_size=3000,
        node_color=node_colors,
        font_size=12,
        font_weight="bold",
        edgecolors="black",  # Borde por defecto
        linewidths=1,  # Grosor del borde por defecto
    )

    # Dibujar el borde doble para los estados finales
    nx.draw_networkx_nodes(
        G,
        pos,
        nodelist=final_node_borders,
        node_size=3500,  # Tamaño ligeramente mayor para el borde exterior
        node_color="none",  # Transparente por dentro
        edgecolors="black",
        linewidths=2,  # Borde más grueso
    )

    # Dibujar las etiquetas de las aristas
    nx.draw_networkx_edge_labels(G, pos, edge_labels=labels, font_color="red")

    # Guardar la imagen
    if not os.path.exists("static"):
        os.makedirs("static")

    image_path = "static/afd.png"
    plt.savefig(image_path)
    plt.close()

    return image_path
