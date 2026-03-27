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
        # cria a mesa (lógica do jogo) e as regras
        self.mesa = Mesa()
        self.movimento = Movimento(self.mesa)
        self.mesa.estocar()

        # cria a janela
        self.game = tk.Tk()
        self.game.title("Paciencia")
        self.game.geometry(f"{LARGURA}x{ALTURA}")
        self.game.resizable(False, False)

        # dicionário que guarda todas as imagens carregadas
        # chave: "1p", "13e", "back" → valor: ImageTk.PhotoImage
        self.cache_cartas = {}

        # dicionário que liga o id do item no canvas ao objeto Carta
        # chave: id do canvas → valor: objeto Carta
        self.id_para_carta = {}

        # variáveis de controle do arraste
        self.item_arrastando = None   # id do item sendo arrastado
        self.pos_original = None      # posição antes de arrastar (para voltar se movimento inválido)
        self.col_origem = None        # coluna de onde a carta saiu
        self.x_mouse = 0             # posição do mouse durante arraste
        self.y_mouse = 0

        # monta a tela na ordem correta
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
        # divide o espaço da janela (sem as margens) em 7 colunas iguais
        espaco = (LARGURA - 2 * MARGEM) // 7

        y_topo = MARGEM
        y_tableau = MARGEM + CARTA_A + MARGEM

        # estoque — primeira coluna
        x_estoque = MARGEM
        self.canvas.create_rectangle(x_estoque, y_topo,
                                     x_estoque + CARTA_L, y_topo + CARTA_A,
                                     outline="white", fill="", width=2, dash=(5, 3),
                                     tags="rect_estoque")

        # descarte — segunda coluna
        x_descarte = MARGEM + espaco
        self.canvas.create_rectangle(x_descarte, y_topo,
                                     x_descarte + CARTA_L, y_topo + CARTA_A,
                                     outline="white", fill="", width=2, dash=(5, 3))

        # fundações — começam na quarta coluna pulando a coluna 2 que é vazia
        x_fundacao_inicio = MARGEM + 3 * espaco
        for i in range(4):
            x = x_fundacao_inicio + i * espaco
            self.canvas.create_rectangle(x, y_topo,
                                         x + CARTA_L, y_topo + CARTA_A,
                                         outline="white", fill="", width=2, dash=(5, 3))

        # tableau — 7 colunas igualmente espaçadas na linha de baixo
        for i in range(7):
            x = MARGEM + i * espaco
            self.canvas.create_rectangle(x, y_tableau,
                                         x + CARTA_L, y_tableau + CARTA_A,
                                         outline="white", fill="", width=2, dash=(5, 3))

    # ── IMAGENS ────────────────────────────────────────────────────────────────

    def carregarImagens(self):
        # carrega todas as 52 cartas redimensionadas para o tamanho definido
        naipes = ['p', 'o', 'c', 'e']
        for n in naipes:
            for v in range(1, 14):
                img = Image.open(f"assets/Cards/{v}{n}.png").resize((CARTA_L, CARTA_A))
                self.cache_cartas[f"{v}{n}"] = ImageTk.PhotoImage(img)

        # carrega o verso da carta
        img_back = Image.open("assets/Cards/cardBack_blue4.png").resize((CARTA_L, CARTA_A))
        self.cache_cartas["back"] = ImageTk.PhotoImage(img_back)

    # ── MESA INICIAL ──────────────────────────────────────────────────────────

    def desenharMesa(self):
        espaco = (LARGURA - 2 * MARGEM) // 7

        # y onde o tableau começa
        y_base = MARGEM + CARTA_A + MARGEM

        for i, coluna in enumerate(self.mesa.tableau):
            for j, carta in enumerate(coluna):
                x = MARGEM + i * espaco
                # cada carta fica 25px abaixo da anterior — mostrando a pilha
                y = y_base + j * 25

                # se a carta está virada para cima mostra a frente, senão o verso
                chave = f"{carta.valor}{carta.naipe}" if carta.face_up else "back"

                img_id = self.canvas.create_image(x, y,
                                                  image=self.cache_cartas[chave],
                                                  anchor="nw",
                                                  tags="carta")

                # liga o id do canvas ao objeto carta para saber qual carta é quando clicar
                self.id_para_carta[img_id] = carta

                # só vincula eventos de arraste em cartas viradas para cima
                if carta.face_up:
                    self._vincularEventos(img_id)

    # ── ESTOQUE ───────────────────────────────────────────────────────────────

    def desenharEstoque(self):
        self.canvas.delete("img_estoque")
        if self.mesa.estoque:
            img_id = self.canvas.create_image(MARGEM, MARGEM,
                                              image=self.cache_cartas["back"],
                                              anchor="nw",
                                              tags="img_estoque")
            # clique no estoque vira a próxima carta
            self.canvas.tag_bind(img_id, "<Button-1>", self.clicarEstoque)
            self.canvas.tag_bind("rect_estoque", "<Button-1>", self.clicarEstoque)

    def atualizarTela(self):
        self.canvas.delete("carta", "img_descarte")
        self.id_para_carta.clear()
        self.desenharEstoque()
        self.desenharMesa()
        if self.mesa.descarte:
            self._atualizarDescarte(self.mesa.descarte[-1])

    def clicarEstoque(self, event):
        carta = self.mesa.descartar()
        if carta:
            self.atualizarTela()
        else:
            # estoque vazio — recoloca as cartas do descarte
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
        # vincula os três eventos necessários para arrastar uma carta
        self.canvas.tag_bind(img_id, "<Button-1>",       self.iniciarArraste)
        self.canvas.tag_bind(img_id, "<B1-Motion>",      self.arrastando)
        self.canvas.tag_bind(img_id, "<ButtonRelease-1>", self.soltarCarta)

    def iniciarArraste(self, event):
        # pega o item que está sob o mouse no momento do clique
        item = self.canvas.find_withtag("current")
        if not item:
            return
        self.item_arrastando = item[0]
        self.pos_original = self.canvas.coords(self.item_arrastando)
        self.x_mouse = event.x
        self.y_mouse = event.y
        self.col_origem = self._identificarColuna(self.pos_original[0])
        self.carta_arrastando = self.id_para_carta.get(self.item_arrastando)

        if self.col_origem is not None and self.carta_arrastando in self.mesa.tableau[self.col_origem]:
            self.index_origem = self.mesa.tableau[self.col_origem].index(self.carta_arrastando)
        else:
            self.index_origem = None

        # traz a carta para frente de tudo
        self.canvas.tag_raise(self.item_arrastando)

    def arrastando(self, event):
        if not self.item_arrastando:
            return
        # calcula quanto o mouse se moveu e move a carta junto
        dx = event.x - self.x_mouse
        dy = event.y - self.y_mouse
        self.canvas.move(self.item_arrastando, dx, dy)
        self.x_mouse = event.x
        self.y_mouse = event.y

    def soltarCarta(self, event):
        if not self.item_arrastando:
            return

        col_dest = self._identificarColuna(event.x)
        movimento_valido = False

        if col_dest is not None and self.col_origem is not None and self.index_origem is not None:
            n_cartas = len(self.mesa.tableau[self.col_origem]) - self.index_origem
            resultado = self.movimento.moverBloco(self.col_origem, col_dest, n_cartas)
            movimento_valido = resultado == "v"

        elif col_dest is not None and self.col_origem is None:
            resultado = self.movimento.descarteParaTableau(col_dest)
            movimento_valido = resultado == "v"

        if movimento_valido:
            self.atualizarTela()
        else:
            # movimento inválido — volta a carta para a posição original
            self.canvas.coords(self.item_arrastando,
                               self.pos_original[0], self.pos_original[1])

        self.item_arrastando = None
        self.carta_arrastando = None
        self.index_origem = None

    # ── UTILITÁRIOS ───────────────────────────────────────────────────────────

    def _identificarColuna(self, x_pos):
        espaco = (LARGURA - 2 * MARGEM) // 7
        for i in range(7):
            x_inicio = MARGEM + i * espaco
            if x_inicio <= x_pos <= x_inicio + CARTA_L:
                return i
        return None

    def _revelarTopo(self, col_idx):
        coluna = self.mesa.tableau[col_idx]
        if not coluna:
            return
        carta_topo = coluna[-1]
        if not carta_topo.face_up:
            carta_topo.face_up = True
            # atualiza a imagem da carta no canvas
            for img_id, obj in self.id_para_carta.items():
                if obj == carta_topo:
                    self.canvas.itemconfig(img_id, image=self.cache_cartas[f"{carta_topo.valor}{carta_topo.naipe}"])
                    self._vincularEventos(img_id)

if __name__ == "__main__":
    Game()