

"""testes gerados por IA para validar as funcionalidades do jogo de paciência"""

import unittest

from carta import Carta
from deck import Deck
from mesa import Mesa
from regras import Regras
from movimentos import Movimento

class TestCarta(unittest.TestCase):
    def test_carta_properties(self):
        c = Carta('o', 7)
        self.assertEqual(c.naipe, 'o')
        self.assertEqual(c.valor, 7)
        self.assertEqual(c.cor, 'v')
        self.assertFalse(c.face_up)

    def test_carta_str_and_repr(self):
        c = Carta('e', 1)
        self.assertIn('VALOR:1', str(c))
        self.assertEqual(str(c), repr(c))

    def test_carta_comparacoes(self):
        a = Carta('o', 5)
        b = Carta('p', 7)
        c = Carta('o', 5)
        self.assertTrue(a == c)
        self.assertFalse(a == b)
        self.assertTrue(a < b)
        self.assertTrue(b > a)

class TestDeck(unittest.TestCase):
    def test_deck_inicializacao(self):
        d = Deck()
        self.assertEqual(len(d), 52)
        self.assertIsNotNone(d.comprar())
        self.assertEqual(len(d), 51)

    def test_deck_comprar_vazio(self):
        d = Deck()
        for _ in range(52):
            d.comprar()
        self.assertIsNone(d.comprar())

class TestMesa(unittest.TestCase):
    def test_distribuir_tableau(self):
        m = Mesa()
        expected = [1, 2, 3, 4, 5, 6, 7]
        sizes = [len(c) for c in m.tableau]
        self.assertEqual(sizes, expected)
        # topo de cada pilha deve estar virada para cima
        self.assertTrue(all(col[-1].face_up for col in m.tableau if col))

    def test_estocar_e_descartar(self):
        m = Mesa()
        m.cartas = Deck()  # baralho novo para controlar
        m.estoque = []
        m.descarte = []
        # popular o estoque manualmente
        carta = Carta('o', 1)
        m.estoque.append(carta)
        c = m.descartar()
        self.assertEqual(c, carta)
        self.assertTrue(c.face_up)
        self.assertIn(c, m.descarte)
        # recolocar ao estoque quando descarte tiver cartas
        retorno = m.descartar()
        self.assertIsNone(retorno)
        self.assertEqual(len(m.descarte), 0)
        self.assertEqual(m.estoque[-1].face_up, False)

class TestRegras(unittest.TestCase):
    def setUp(self):
        self.mesa = Mesa()
        self.regras = Regras(self.mesa)

    def test_pode_mover_tableau_rei_em_pilha_vazia(self):
        self.mesa.tableau[0] = []
        self.assertTrue(self.regras.podeMoverTableau(Carta('o', 13), 0))

    def test_pode_mover_tableau_cor_e_valor(self):
        c11 = Carta('o', 11); c11.face_up = True
        c10 = Carta('p', 10); c10.face_up = True
        self.mesa.tableau[1] = [c11]
        self.assertTrue(self.regras.podeMoverTableau(c10, 1))

    def test_pode_mover_para_fundacao(self):
        as_c = Carta('p', 1); as_c.face_up = True
        self.assertTrue(self.regras.podeMoverParaFundacao(as_c, 0))
        self.mesa.fundacao[0].append(as_c)
        dois_c = Carta('p', 2); dois_c.face_up = True
        self.assertTrue(self.regras.podeMoverParaFundacao(dois_c, 0))

    def test_pode_mover_bloco(self):
        c1 = Carta('o', 2); c1.face_up = True
        c2 = Carta('o', 3); c2.face_up = False
        self.mesa.tableau[0] = [c1, c2]
        self.assertTrue(self.regras.podeMoverBlocoTableau(0, 1))
        self.assertFalse(self.regras.podeMoverBlocoTableau(0, 2))

    def test_movimentos_possiveis(self):
        # coluna 0: K de paus aberto, coluna 1 vazia
        k_p = Carta('p', 13); k_p.face_up = True
        self.mesa.tableau = [[k_p], [], [], [], [], [], []]
        movimentos = self.regras.movimentosPossiveis()
        self.assertIn((0, 1, 1), movimentos)

class TestMovimento(unittest.TestCase):
    def setUp(self):
        self.mesa = Mesa()
        self.mov = Movimento(self.mesa)

    def test_mover_bloco(self):
        k = Carta('o', 13); k.face_up=True
        q = Carta('p', 12); q.face_up=True
        self.mesa.tableau[0] = [q, k]
        self.mesa.tableau[1] = []
        resultado = self.mov.moverBloco(0,1,1)
        self.assertEqual(resultado, 'v')
        self.assertEqual(self.mesa.tableau[1][-1], k)
        self.assertEqual(len(self.mesa.tableau[0]), 1)

    def test_tableau_para_fundacao(self):
        a = Carta('o', 1); a.face_up=True
        self.mesa.tableau[0] = [a]
        resultado = self.mov.tableauParaFundacao(0, 0)
        self.assertEqual(resultado, 'v')
        self.assertEqual(self.mesa.fundacao[0][-1], a)

    def test_descarte_para_fundacao(self):
        a = Carta('o', 1); a.face_up=True
        self.mesa.descarte = [a]
        resultado = self.mov.descarteParaFundacao(0)
        self.assertEqual(resultado, 'v')
        self.assertEqual(self.mesa.fundacao[0][-1], a)

    def test_descarte_para_tableau(self):
        # só pode mover rei para tableau vazio
        rei = Carta('o', 13); rei.face_up = True
        self.mesa.descarte = [rei]
        self.mesa.tableau = [[], [], [], [], [], [], []]

        resultado = self.mov.descarteParaTableau(0)
        self.assertEqual(resultado, 'v')
        self.assertEqual(self.mesa.tableau[0][-1], rei)
        self.assertEqual(len(self.mesa.descarte), 0)

if __name__ == '__main__':
    unittest.main()
