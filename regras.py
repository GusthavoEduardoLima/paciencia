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
        