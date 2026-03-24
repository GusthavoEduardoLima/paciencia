import random
from carta import Carta
class Deck:
    
    def __init__(self):
        self.cartas = []
        naipes = ['o', 'p', 'c', 'e']

        for n in naipes:
            for v in range(1,14):
                self.cartas.append(Carta(n, v))
        self.embaralhar()
    def embaralhar(self):
        random.shuffle(self.cartas)
    def comprar(self):
        if len(self.cartas)>0:
            return self.cartas.pop()
        return None
    def __str__(self):
        return f"O baralho tem {self.cartas} cartas"        
    def __repr__(self):
        return self.__str__()
nd = Deck()
print(nd)