from deck import Deck

class Mesa:
    def __init__(self):
        self.cartas = Deck()
        self.tableau = [[], [], [], [], [], [], []]
        self.fundacao = [[], [], [], []]
        self.estoque = []
        self.descarte = []
        self.distribuirTableau()
    def distribuirTableau(self):
        for i in  range(7):
                for j in range(i+1):
                    carta = self.cartas.comprar()
                    if carta:
                        if j==i:
                            carta.face_up = True
                        self.tableau[i].append(carta)
    def estocar(self):
        tamanho = len(self.cartas)
        for i in range(tamanho):
            carta = self.cartas.comprar()
            self.estoque.append(carta)
    def descartar(self):
        if len(self.estoque)>0:
            carta = self.estoque.pop()
            carta.face_up= True
            self.descarte.append(carta)
            return carta
        elif len(self.descarte)>0:
            self.estoque = self.descarte[::-1]
            self.descarte = []
            for c in self.estoque:
                c.face_up = False
            return None


