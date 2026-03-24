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
        pass
    def testarTableau(self):
        print("\n=== VERIFICAÇÃO DO TABLEAU (COLUNAS) ===")
        for i, coluna in enumerate(self.tableau):
            print(f"Coluna {i + 1}:")
            if not coluna:
                print("  (Vazia)")
            else:
                for carta in coluna:
                    # Aqui acessamos os atributos individuais de cada objeto Carta
                    status = "ABERTA" if carta.face_up else "FECHADA"
                    print(f"  -> Valor: {carta.valor:2} | Naipe: {carta.naipe} | Face: {status}")
        print("========================================\n")

