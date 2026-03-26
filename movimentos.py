#regras e logica do jogo
from regras import Regras
class Movimento:
    def __init__(self,mesa):
        self.mesa = mesa
        self.regras = Regras(mesa)
    def moverBloco(self,col_origem,col_destino, n_cartas):

        if not self.regras.podeMoverBlocoTableau(col_origem,n_cartas):
            return "f"
        origem = self.mesa.tableau[col_origem]
        destino = self.mesa.tableau[col_destino]
        
        carta_base = origem[-n_cartas]

        if self.regras.podeMoverTableau(carta_base,col_destino):
            bloco = origem[-n_cartas:]
            self.mesa.tableau[col_origem] = origem[:-n_cartas]
            destino.extend(bloco)
            self._revelar_topo_origem(col_origem)
            return "v"
        return "f"

    def tableauParaFundacao(self,col_origem,destino):
        origem = self.mesa.tableau[col_origem]

        if not origem:
            return "f"
        carta = origem[-1]

        if self.regras.podeMoverParaFundacao(carta,destino):
            self.mesa.fundacao[destino].append(origem.pop())
            self._revelar_topo_origem(col_origem)
            return "v"
        return "f"
    
    def descarteParaFundacao(self,destino):
        if not self.mesa.descarte:
            return "f"
        
        carta_descarte = self.mesa.descarte[-1]

        if self.regras.podeMoverParaFundacao(carta_descarte,destino):
            carta = self.mesa.descarte.pop()
            self.mesa.fundacao[destino].append(carta)
            return "v"
        return "f"
    
    def descarteParaTableau(self,col_destino):
        if not self.mesa.descarte:
            return "f"
        carta_descarte = self.mesa.descarte[-1]

        if self.regras.podeMoverTableau(carta_descarte,col_destino):
            carta = self.mesa.descarte.pop()
            self.mesa.tableau[col_destino].append(carta)
            return "v"  
        return "f"
    

    def _revelar_topo_origem(self, col_indice):
        """Método interno para abrir a carta que ficou exposta na coluna."""
        coluna = self.mesa.tableau[col_indice]
        if coluna and not coluna[-1].face_up:
            coluna[-1].face_up = True
