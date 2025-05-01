# afn.py


class Estado:
    def __init__(self):
        self.transiciones = {}  # Transiciones por símbolo
        self.epsilon = []  # Transiciones epsilon

    def __repr__(self):
        """Representación en cadena del estado."""
        return f"Estado({id(self)})"  # Representa el estado con su id único para identificarlo


class AFN:
    def __init__(self, inicio, fin, alfabeto):
        self.inicio = inicio
        self.fin = fin
        self.alfabeto = alfabeto  # Guardamos el alfabeto en el AFN

    def __repr__(self):
        """Representación en cadena del AFN"""
        return f"AFN(inicio={id(self.inicio)}, fin={id(self.fin)}, alfabeto={self.alfabeto})"
