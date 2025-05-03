import matplotlib.pyplot as plt
import networkx as nx
import os

class AFD:
    def __init__(self):
        self.estados = []
        self.transiciones = {}
        self.estado_inicial = None
        self.estados_finales = set()
        self.estado_trampa = frozenset()
        self._nombres_estados = {}
        self._contador_estados = 0

    def obtener_nombre_estado(self, estado):
        """Obtiene un nombre consistente para un estado."""
        if estado not in self._nombres_estados:
            if estado == self.estado_trampa:
                self._nombres_estados[estado] = "qT"
            elif estado == self.estado_inicial:
                self._nombres_estados[estado] = "q0"
            else:
                self._contador_estados += 1
                self._nombres_estados[estado] = f"q{self._contador_estados}"
        return self._nombres_estados[estado]

    def agregar_estado_trampa(self, alfabeto):
        """Agrega el estado trampa y sus transiciones."""
        if self.estado_trampa not in self.estados:
            self.estados.append(self.estado_trampa)

        # Agregar transiciones faltantes al estado trampa
        for estado in self.estados:
            for simbolo in alfabeto:
                if (estado, simbolo) not in self.transiciones:
                    self.transiciones[(estado, simbolo)] = self.estado_trampa

        # Todas las transiciones desde el estado trampa van a sí mismo
        for simbolo in alfabeto:
            self.transiciones[(self.estado_trampa, simbolo)] = self.estado_trampa

def epsilon_closure(estado_afn):
    """Calcula la cerradura epsilon de un estado AFN."""
    cerradura = {estado_afn}
    pila = [estado_afn]

    while pila:
        actual = pila.pop()
        if hasattr(actual, 'epsilon') and isinstance(actual.epsilon, list):
            for siguiente in actual.epsilon:
                if siguiente not in cerradura:
                    cerradura.add(siguiente)
                    pila.append(siguiente)
    
    return cerradura

def convertir_afn_a_afd(afn):
    """Convierte un AFN en un AFD utilizando el algoritmo de subconjuntos."""
    afd = AFD()

    # Calcular la cerradura epsilon del estado inicial del AFN
    estado_inicial_afn_closure = epsilon_closure(afn.inicio)
    estado_inicial_afd_frozenset = frozenset(estado_inicial_afn_closure)

    afd.estado_inicial = estado_inicial_afd_frozenset
    afd.estados.append(estado_inicial_afd_frozenset)

    pendientes = [estado_inicial_afd_frozenset]
    estados_procesados = {estado_inicial_afd_frozenset}

    while pendientes:
        estado_actual_frozenset = pendientes.pop()

        # Verificar si el estado actual contiene algún estado final del AFN
        if any(estado.es_final for estado in estado_actual_frozenset):
            afd.estados_finales.add(estado_actual_frozenset)

        # Procesar cada símbolo del alfabeto
        for simbolo in sorted(list(afn.alfabeto)):
            siguiente_estados_afn = set()

            # Obtener todos los estados alcanzables con el símbolo actual
            for estado_afn in estado_actual_frozenset:
                if simbolo in estado_afn.transiciones:
                    siguiente_estados_afn.update(estado_afn.transiciones[simbolo])

            if siguiente_estados_afn:
                # Calcular la cerradura epsilon para cada estado alcanzado
                siguiente_estado_closure_afn = set()
                for estado_afn in siguiente_estados_afn:
                    siguiente_estado_closure_afn.update(epsilon_closure(estado_afn))

                siguiente_estado_afd_frozenset = frozenset(siguiente_estado_closure_afn)

                if siguiente_estado_afd_frozenset not in estados_procesados:
                    afd.estados.append(siguiente_estado_afd_frozenset)
                    pendientes.append(siguiente_estado_afd_frozenset)
                    estados_procesados.add(siguiente_estado_afd_frozenset)

                afd.transiciones[(estado_actual_frozenset, simbolo)] = siguiente_estado_afd_frozenset

    # Agregar el estado trampa y sus transiciones
    afd.agregar_estado_trampa(afn.alfabeto)

    return afd

def dibujar_afd(afd):
    """Dibuja el AFD usando matplotlib y networkx."""
    G = nx.DiGraph()

    # Asignar nombres a los estados
    nombres_estados = {}
    for estado in afd.estados:
        nombres_estados[estado] = afd.obtener_nombre_estado(estado)

    # Añadir nodos
    for estado in afd.estados:
        nombre = nombres_estados[estado]
        if estado == afd.estado_inicial:
            G.add_node(nombre, is_initial=True)
        elif estado == afd.estado_trampa:
            G.add_node(nombre, is_trap=True)
        else:
            G.add_node(nombre)
        
        if estado in afd.estados_finales:
            G.nodes[nombre]["is_final"] = True

    # Añadir aristas
    for (estado_origen, simbolo), estado_destino in afd.transiciones.items():
        nombre_origen = nombres_estados[estado_origen]
        nombre_destino = nombres_estados[estado_destino]
        G.add_edge(nombre_origen, nombre_destino, label=simbolo)

    pos = nx.spring_layout(G, k=1, iterations=50)
    plt.figure(figsize=(12, 8))

    # Dibujar nodos
    node_colors = []
    final_node_borders = []
    node_list = []

    for node in G.nodes():
        node_list.append(node)
        if G.nodes[node].get("is_initial"):
            node_colors.append("lightgreen")
        elif G.nodes[node].get("is_trap"):
            node_colors.append("lightgray")
        elif G.nodes[node].get("is_final"):
            node_colors.append("lightblue")
        else:
            node_colors.append("white")
        
        if G.nodes[node].get("is_final"):
            final_node_borders.append(node)

    nx.draw(G, pos, 
            nodelist=node_list,
            node_color=node_colors,
            node_size=3000,
            with_labels=True,
            font_size=12,
            font_weight="bold",
            edgecolors="black",
            linewidths=1)

    # Dibujar estados finales con doble círculo
    nx.draw_networkx_nodes(G, pos,
                          nodelist=final_node_borders,
                          node_size=3500,
                          node_color="none",
                          edgecolors="black",
                          linewidths=2)

    # Dibujar etiquetas de las aristas
    edge_labels = nx.get_edge_attributes(G, "label")
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_color="red")

    # Guardar la imagen
    if not os.path.exists("static"):
        os.makedirs("static")
    plt.savefig("static/afd.png")
    plt.close()

    return "static/afd.png"