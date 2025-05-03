class Estado:
    def __init__(self):
        self.transiciones = {}  # Transiciones por símbolo
        self.epsilon = []  # Transiciones epsilon
        self.es_final = False  # Para marcar estados finales
        self.nombre = None  # Para identificación del estado

    def __repr__(self):
        """Representación en cadena del estado."""
        if self.nombre:
            return f"Estado({self.nombre})"
        return f"Estado({id(self)})"

class AFN:
    def __init__(self, inicio, fin, alfabeto):
        self.inicio = inicio
        self.fin = fin
        self.fin.es_final = True
        self.alfabeto = alfabeto
        self.estados = set()  # Conjunto para mantener todos los estados
        self.agregar_estado(inicio)
        self.agregar_estado(fin)

    def agregar_estado(self, estado):
        """Agrega un estado al AFN"""
        self.estados.add(estado)

    def obtener_todos_estados(self):
        """Retorna todos los estados alcanzables desde el estado inicial"""
        estados_alcanzables = set()
        pila = [self.inicio]
        
        while pila:
            estado_actual = pila.pop()
            if estado_actual not in estados_alcanzables:
                estados_alcanzables.add(estado_actual)
                
                # Agregar estados alcanzables por transiciones normales
                for destinos in estado_actual.transiciones.values():
                    for destino in destinos:
                        pila.append(destino)
                
                # Agregar estados alcanzables por epsilon-transiciones
                for destino in estado_actual.epsilon:
                    pila.append(destino)
        
        return estados_alcanzables

    def limpiar_estados_no_alcanzables(self):
        """Elimina estados que no son alcanzables desde el estado inicial"""
        estados_alcanzables = self.obtener_todos_estados()
        self.estados = estados_alcanzables

    def __repr__(self):
        """Representación en cadena del AFN"""
        return f"AFN(inicio={self.inicio}, fin={self.fin}, alfabeto={self.alfabeto})"