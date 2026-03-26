from mesa import Mesa

class Regras:
    def __init__(self,mesa):
        self.mesa = mesa

    def podeMoverTableau(self,carta, col_destino):
        """se coluna vazia e carta for um rei"""
        destino = self.mesa.tableau[col_destino]
        if not destino:
            return carta.valor == 13
        
        topo= destino[-1]
        return topo.face_up and topo.cor != carta.cor and topo.valor == carta.valor+1
    def podeMoverParaFundacao(self,carta,pilha_dest):
        pilha = self.mesa.fundacao[pilha_dest]

        if not pilha:
            return carta.valor==1
        topo = pilha[-1]
        return topo.naipe==carta.naipe  and topo.valor == carta.valor-1
    def podeMoverBlocoTableau(self,col_origen,n_cartas):
        origem = self.mesa.tableau[col_origen]
        cartas_abertas = []
        for i in origem:
            if i.face_up:
                cartas_abertas.append(i)
        return n_cartas<=len(cartas_abertas)
    def movimentosPossiveis(self):
        movimentos=[]
        for col_origem in range(7):
            origem = self.mesa.tableau[col_origem]
            cartas_abertas = []
            for i in origem:
                if i.face_up:
                    cartas_abertas.append(i)
            for n in range(1, len(cartas_abertas)+1):
                carta_base = cartas_abertas[-n]
                for col_destino in range(7):
                    if col_destino!=col_origem:
                        if self.podeMoverTableau(carta_base,col_destino):
                            movimentos.append((col_origem,col_destino,n))
        return movimentos