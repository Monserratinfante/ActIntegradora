# afn.py

class Estado:
    def __init__(self):
        self.transiciones = {}  # transiciones por símbolo
        self.epsilon = []       # transiciones epsilon

class AFN:
    def __init__(self, inicio, fin):
        self.inicio = inicio
        self.fin = fin
