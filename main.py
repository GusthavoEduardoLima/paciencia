import tkinter as tk
from PIL import Image, ImageTk

from mesa import Mesa
#altere as medidas conforme sua tela
LARGURA = 1300
ALTURA = 650
CARTA_L = 80   # largura da carta
CARTA_A = 120  # altura da carta
MARGEM = 20    # espaço entre as bordas e as cartas

class Game:

    def __init__(self):
        self.mesa = Mesa()
        self.game = tk.Tk()
        self.game.title("Paciencia")
        self.game.geometry(f"{LARGURA}x{ALTURA}")
        self.game.resizable(False,False)
        self.cache_cartas = {}
        self.carregarFundo()
        self.desenharEspaco()
        self.carregar_assets()
        self.desenhar_mesa_inicial()
        self.game.mainloop()
    def carregarFundo(self):
        self.canvas = tk.Canvas(self.game, width=LARGURA, height=ALTURA, highlightthickness=0)
        self.canvas.pack()
        img = Image.open("assets/background_img.jpeg").resize((LARGURA, ALTURA))
        self.bg_img = ImageTk.PhotoImage(img)
        self.canvas.create_image(0, 0, image= self.bg_img, anchor="nw")
    def desenharEspaco(self):
        
        # divide o espaço da janela (sem as margens) em 7 colunas iguais
        # ex: (1300 - 40) // 7 = 180px por coluna
        espaco = (LARGURA - 2 * MARGEM) // 7

        # linha de cima começa logo abaixo da margem do topo
        y_topo = MARGEM

        # linha do tableau começa abaixo da linha de cima
        # margem do topo + altura da carta + espaço entre as linhas
        y_tableau = MARGEM + CARTA_A + MARGEM

        # estoque — primeira coluna (índice 0)
        x_estoque = MARGEM
        self.canvas.create_rectangle(x_estoque, y_topo, x_estoque + CARTA_L, y_topo + CARTA_A, outline="white", fill="", width=2, dash=(5,3))

        # descarte — segunda coluna (índice 1)
        x_descarte = MARGEM + espaco
        self.canvas.create_rectangle(x_descarte, y_topo,x_descarte + CARTA_L, y_topo + CARTA_A, outline="white", fill="", width=2, )

        # fundações — começam na quarta coluna (índice 3) pulando a coluna 2 que é vazia
        x_fundacao_inicio = MARGEM + 3 * espaco
        for i in range(4):
            x = x_fundacao_inicio + i * espaco  # cada fundação avança uma coluna
            self.canvas.create_rectangle(x, y_topo,x + CARTA_L, y_topo + CARTA_A, outline="white", fill="", width=2)

        # tableau — 7 colunas igualmente espaçadas na linha de baixo
        for i in range(7):
            x = MARGEM + i * espaco  # cada coluna avança um espaço
            self.canvas.create_rectangle(x, 2*y_tableau,x + CARTA_L, 2* y_tableau + CARTA_A,outline="white", fill="", width=2)
    def carregar_assets(self):
        naipes = ['p', 'o', 'c', 'e']
        for n in naipes:
            for v in range(1, 14):
                nome_arq = f"assets/Cards/{v}{n}.png"
                img_pil = Image.open(nome_arq).resize((80, 110), Image.Resampling.LANCZOS)
                # Guarda no cache com a chave "1p", "13c", etc.
                self.cache_cartas[f"{v}{n}"] = ImageTk.PhotoImage(img_pil)
        
        # Carrega também o verso da carta
        img_back = Image.open("assets/Cards/cardBack_blue4.png").resize((80, 110), Image.Resampling.LANCZOS)
        self.cache_cartas["back"] = ImageTk.PhotoImage(img_back)
    
    def desenhar_mesa_inicial(self):
        # Coordenadas iniciais do Tableau
        x_inicial = 50
        y_inicial = 150
        espacamento_x = 100
        offset_y = 25 # Distância entre uma carta e outra na pilha

        for i, coluna in enumerate(self.mesa.tableau):
            for j, carta in enumerate(coluna):
                x = x_inicial + (i * espacamento_x)
                y = y_inicial + (j * offset_y)
                
                # Se a carta estiver aberta, usa a imagem dela, senão usa o verso
                tag_imagem = f"{carta.valor}{carta.naipe}" if carta.face_up else "back"
                img = self.cache_cartas[tag_imagem]
                
                self.canvas.create_image(x, y, image=img, anchor="nw", tags="carta")

if __name__ == "__main__":
    Game()