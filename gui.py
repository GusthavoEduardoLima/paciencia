import tkinter as tk
from PIL import Image, ImageTk
from mesa import Mesa
from movimentos import Movimento

LARGURA = 1300
ALTURA = 650
CARTA_L = 80
CARTA_A = 120
MARGEM = 20


class Game:
    def __init__(self):
        self.mesa = Mesa()
        self.movimento = Movimento(self.mesa)
        self.mesa.estocar()

        self.game = tk.Tk()
        self.game.title("Paciencia")
        self.game.geometry(f"{LARGURA}x{ALTURA}")
        self.game.resizable(False, False)

        self.cache_cartas = {}
        self.id_para_carta = {}

        # variáveis de controle do arraste
        self.item_arrastando = None
        self.pos_original = None
        self.col_origem = None          # coluna do tableau de origem (ou None)
        self.index_origem = None
        self.origem_descarte = False    # flag explícita para origem no descarte
        self.x_mouse = 0
        self.y_mouse = 0
        # lista com todos os itens do bloco sendo arrastado e suas posições originais
        self.itens_arrastando = []
        self.posicoes_originais = []

        self.carregarFundo()
        self.desenharEspaco()
        self.carregarImagens()
        self.desenharMesa()
        self.desenharEstoque()

        self.game.mainloop()

    # ── FUNDO ─────────────────────────────────────────────────────────────────

    def carregarFundo(self):
        self.canvas = tk.Canvas(self.game, width=LARGURA, height=ALTURA, highlightthickness=0)
        self.canvas.pack()
        img = Image.open("assets/background_img.jpeg").resize((LARGURA, ALTURA))
        self.bg_img = ImageTk.PhotoImage(img)
        self.canvas.create_image(0, 0, image=self.bg_img, anchor="nw")

    # ── ESPAÇOS VAZIOS ─────────────────────────────────────────────────────────

    def desenharEspaco(self):
        espaco = (LARGURA - 2 * MARGEM) // 7

        y_topo = MARGEM
        y_tableau = MARGEM + CARTA_A + MARGEM

        x_estoque = MARGEM
        self.canvas.create_rectangle(x_estoque, y_topo,
                                     x_estoque + CARTA_L, y_topo + CARTA_A,
                                     outline="white", fill="#5d12e9", width=2, dash=(5, 3),
                                     tags="rect_estoque")

        x_descarte = MARGEM + espaco
        self.canvas.create_rectangle(x_descarte, y_topo,
                                     x_descarte + CARTA_L, y_topo + CARTA_A,
                                     outline="white", fill="#5d12e9", width=2, dash=(5, 3))

        x_fundacao_inicio = MARGEM + 3 * espaco
        for i in range(4):
            x = x_fundacao_inicio + i * espaco
            self.canvas.create_rectangle(x, y_topo,
                                         x + CARTA_L, y_topo + CARTA_A,
                                         outline="white", fill="#5d12e9", width=2, dash=(5, 3))

        for i in range(7):
            x = MARGEM + i * espaco
            self.canvas.create_rectangle(x, y_tableau,
                                         x + CARTA_L, y_tableau + CARTA_A,
                                         outline="white", fill="#5d12e9", width=2, dash=(5, 3))

    # ── IMAGENS ────────────────────────────────────────────────────────────────

    def carregarImagens(self):
        naipes = ['p', 'o', 'c', 'e']
        for n in naipes:
            for v in range(1, 14):
                img = Image.open(f"assets/Cards/{v}{n}.png").resize((CARTA_L, CARTA_A))
                self.cache_cartas[f"{v}{n}"] = ImageTk.PhotoImage(img)

        img_back = Image.open("assets/Cards/cardBack_blue4.png").resize((CARTA_L, CARTA_A))
        self.cache_cartas["back"] = ImageTk.PhotoImage(img_back)

    # ── MESA INICIAL ──────────────────────────────────────────────────────────

    def desenharMesa(self):
        espaco = (LARGURA - 2 * MARGEM) // 7
        y_base = MARGEM + CARTA_A + MARGEM

        for i, coluna in enumerate(self.mesa.tableau):
            for j, carta in enumerate(coluna):
                x = MARGEM + i * espaco
                y = y_base + j * 25
                chave = f"{carta.valor}{carta.naipe}" if carta.face_up else "back"

                img_id = self.canvas.create_image(x, y,
                                                  image=self.cache_cartas[chave],
                                                  anchor="nw",
                                                  tags="carta")
                self.id_para_carta[img_id] = carta

                if carta.face_up:
                    self._vincularEventos(img_id)

    # ── FUNDAÇÃO ──────────────────────────────────────────────────────────────
    # BUG 2 FIX: método que desenha o topo de cada pilha da fundação

    def desenharFundacao(self):
        self.canvas.delete("img_fundacao")
        espaco = (LARGURA - 2 * MARGEM) // 7
        for i, pilha in enumerate(self.mesa.fundacao):
            if pilha:
                carta = pilha[-1]
                x = MARGEM + (3 + i) * espaco
                img_id = self.canvas.create_image(x, MARGEM,
                                                  image=self.cache_cartas[f"{carta.valor}{carta.naipe}"],
                                                  anchor="nw",
                                                  tags="img_fundacao")
                self.id_para_carta[img_id] = carta

    # ── ESTOQUE ───────────────────────────────────────────────────────────────

    def desenharEstoque(self):
        self.canvas.delete("img_estoque")
        if self.mesa.estoque:
            img_id = self.canvas.create_image(MARGEM, MARGEM,
                                              image=self.cache_cartas["back"],
                                              anchor="nw",
                                              tags="img_estoque")
            self.canvas.tag_bind(img_id, "<Button-1>", self.clicarEstoque)
            self.canvas.tag_bind("rect_estoque", "<Button-1>", self.clicarEstoque)

    def atualizarTela(self):
        # BUG 2 FIX: inclui "img_fundacao" no delete e chama desenharFundacao()
        self.canvas.delete("carta", "img_descarte", "img_fundacao")
        self.id_para_carta.clear()
        self.desenharEstoque()
        self.desenharMesa()
        self.desenharFundacao()
        if self.mesa.descarte:
            self._atualizarDescarte(self.mesa.descarte[-1])

    def clicarEstoque(self, event):
        self.mesa.descartar()
        self.atualizarTela()

    def _atualizarDescarte(self, carta):
        espaco = (LARGURA - 2 * MARGEM) // 7
        self.canvas.delete("img_descarte")
        img_id = self.canvas.create_image(MARGEM + espaco, MARGEM,
                                          image=self.cache_cartas[f"{carta.valor}{carta.naipe}"],
                                          anchor="nw",
                                          tags="img_descarte")
        self.id_para_carta[img_id] = carta
        self._vincularEventos(img_id)

    # ── ARRASTE ───────────────────────────────────────────────────────────────

    def _vincularEventos(self, img_id):
        self.canvas.tag_bind(img_id, "<Button-1>",        self.iniciarArraste)
        self.canvas.tag_bind(img_id, "<B1-Motion>",       self.arrastando)
        self.canvas.tag_bind(img_id, "<ButtonRelease-1>", self.soltarCarta)

    def iniciarArraste(self, event):
        item = self.canvas.find_withtag("current")
        if not item:
            return
        self.item_arrastando = item[0]
        self.pos_original = self.canvas.coords(self.item_arrastando)
        self.x_mouse = event.x
        self.y_mouse = event.y

        carta = self.id_para_carta.get(self.item_arrastando)
        self.carta_arrastando = carta

        self.col_origem = None
        self.index_origem = None
        self.origem_descarte = False
        self.itens_arrastando = [self.item_arrastando]
        self.posicoes_originais = [list(self.pos_original)]

        if self.mesa.descarte and carta == self.mesa.descarte[-1]:
            self.origem_descarte = True
        else:
            col = self._identificarColuna(self.pos_original[0])
            if col is not None and carta in self.mesa.tableau[col]:
                self.col_origem = col
                self.index_origem = self.mesa.tableau[col].index(carta)

                # STACK FIX: encontra os itens canvas de todas as cartas do bloco
                bloco = self.mesa.tableau[col][self.index_origem:]
                if len(bloco) > 1:
                    carta_para_id = {c: iid for iid, c in self.id_para_carta.items()}
                    self.itens_arrastando = []
                    self.posicoes_originais = []
                    for c in bloco:
                        iid = carta_para_id.get(c)
                        if iid is not None:
                            self.itens_arrastando.append(iid)
                            self.posicoes_originais.append(list(self.canvas.coords(iid)))

        # traz todo o bloco para frente, na ordem correta (base primeiro)
        for iid in self.itens_arrastando:
            self.canvas.tag_raise(iid)

    def arrastando(self, event):
        if not self.item_arrastando:
            return
        dx = event.x - self.x_mouse
        dy = event.y - self.y_mouse
        # STACK FIX: move todos os itens do bloco juntos
        for iid in self.itens_arrastando:
            self.canvas.move(iid, dx, dy)
        self.x_mouse = event.x
        self.y_mouse = event.y

    def soltarCarta(self, event):
        if not self.item_arrastando:
            return

        mov_valido = False

        # BUG 1 FIX: verifica primeiro se o drop foi na área da fundação
        fund_dest = self._identificarFundacao(event.x, event.y)
        if fund_dest is not None:
            if self.origem_descarte:
                resultado = self.movimento.descarteParaFundacao(fund_dest)
            elif self.col_origem is not None:
                resultado = self.movimento.tableauParaFundacao(self.col_origem, fund_dest)
            else:
                resultado = "f"
            mov_valido = (resultado == "v")
        else:
            # Tenta mover para o tableau
            col_dest = self._identificarColuna(event.x)
            if col_dest is not None:
                if self.col_origem is not None:
                    n_cartas = len(self.mesa.tableau[self.col_origem]) - self.index_origem
                    resultado = self.movimento.moverBloco(self.col_origem, col_dest, n_cartas)
                    mov_valido = (resultado == "v")
                elif self.origem_descarte:
                    resultado = self.movimento.descarteParaTableau(col_dest)
                    mov_valido = (resultado == "v")

        if mov_valido:
            self.atualizarTela()
        else:
            # STACK FIX: restaura todos os itens do bloco para suas posições originais
            for iid, pos in zip(self.itens_arrastando, self.posicoes_originais):
                self.canvas.coords(iid, pos[0], pos[1])

        self.item_arrastando = None
        self.itens_arrastando = []
        self.posicoes_originais = []

    # ── UTILITÁRIOS ───────────────────────────────────────────────────────────

    def _identificarColuna(self, x_pos):
        """Retorna o índice da coluna do tableau (0-6) pelo x, ou None."""
        espaco = (LARGURA - 2 * MARGEM) // 7
        for i in range(7):
            x_inicio = MARGEM + i * espaco
            if x_inicio <= x_pos <= x_inicio + CARTA_L:
                return i
        return None

    def _identificarFundacao(self, x_pos, y_pos):
        """Retorna o índice da fundação (0-3) se o drop for na área do topo, ou None."""
        # BUG 1 FIX: novo método para detectar drops na fundação
        espaco = (LARGURA - 2 * MARGEM) // 7
        # fundação só existe na linha de cima
        if not (MARGEM <= y_pos <= MARGEM + CARTA_A):
            return None
        for i in range(4):
            x = MARGEM + (3 + i) * espaco
            if x <= x_pos <= x + CARTA_L:
                return i
        return None

if __name__ == "__main__":
    Game()