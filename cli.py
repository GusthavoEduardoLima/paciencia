import os
from mesa import Mesa
from movimentos import Movimento
from regras import Regras
from carta import Carta

# ── ANSI ──────────────────────────────────────────────────────────────────────
VERMELHO  = "\033[91m"
VERDE     = "\033[92m"
AMARELO   = "\033[93m"
CIANO     = "\033[96m"
BRANCO    = "\033[97m"
NEGRITO   = "\033[1m"
DIM       = "\033[2m"
RESET     = "\033[0m"

NAIPE_SIM = {'p': '♣', 'o': '♦', 'c': '♥', 'e': '♠'}
VALOR_STR = {1: 'A', 11: 'J', 12: 'Q', 13: 'K'}


class CLI:

    def __init__(self, mesa: Mesa | None = None):
        if mesa is None:
            self.mesa = Mesa()
            self.mesa.estocar()
        else:
            self.mesa = mesa

        self.movimento = Movimento(self.mesa)
        self.regras    = Regras(self.mesa)
        self._loop_principal()

    # ── FORMATAÇÃO ────────────────────────────────────────────────────────────

    def _formatar_carta(self, carta) -> str:
        """Retorna uma string de 6 chars representando a carta (com cor ANSI)."""
        if not carta:
            return f"{DIM}[   ]{RESET}"
        if not carta.face_up:
            return f"{DIM}[ # ]{RESET}"

        val = VALOR_STR.get(carta.valor, str(carta.valor))
        sim = NAIPE_SIM[carta.naipe]

        if len(val) == 1:
            txt = f" {val}{sim}"   # ex: " A♥"
        else:
            txt = f"{val}{sim}"    # ex: "10♦"

        cor = VERMELHO if carta.naipe in ('o', 'c') else BRANCO
        return f"[{cor}{txt}{RESET}]"

    # VERIFICAÇÕES DE FIM DE JOGO

    def _verificar_vitoria(self) -> bool:
       
        return all(len(f) == 13 for f in self.mesa.fundacao)

    def _movimentos_disponiveis(self) -> bool:
        """
        Retorna True se ainda existe QUALQUER ação possível:
          - Tableau → Tableau
          - Tableau → Fundação
          - Descarte → Tableau ou Fundação
          - Estoque com cartas (pode comprar)
        """
        if self.mesa.estoque:
            return True

        if self.regras.movimentosPossiveis():
            return True

        # Verifica topo do tableau → qualquer fundação
        for col in range(7):
            if self.mesa.tableau[col]:
                carta = self.mesa.tableau[col][-1]
                for f in range(4):
                    if self.regras.podeMoverParaFundacao(carta, f):
                        return True

        # Verifica descarte → tableau ou fundação
        if self.mesa.descarte:
            carta = self.mesa.descarte[-1]
            for col in range(7):
                if self.regras.podeMoverTableau(carta, col):
                    return True
            for f in range(4):
                if self.regras.podeMoverParaFundacao(carta, f):
                    return True

        return False

    # ── EXIBIÇÃO 

    def _exibir_mesa(self):
        os.system('cls' if os.name == 'nt' else 'clear')

        linha = "═" * 58
        print(f"{NEGRITO}{CIANO}{linha}{RESET}")
        print(f"{NEGRITO}{CIANO}                          PACIÊNCIA  {RESET}")
        print(f"{NEGRITO}{CIANO}{linha}{RESET}")

        # ── Estoque / Descarte / Fundações ────────────────────────────────────
        est_txt  = f"{NEGRITO}[ # ]{RESET}" if self.mesa.estoque else f"{DIM}[ ✗ ]{RESET}"
        desc_txt = (self._formatar_carta(self.mesa.descarte[-1])
                    if self.mesa.descarte else f"{DIM}[   ]{RESET}")

        fund_txt = "  ".join(
            self._formatar_carta(f[-1]) if f else f"{DIM}[   ]{RESET}"
            for f in self.mesa.fundacao
        )

        print(f"  Estoque:{est_txt}  Descarte:{desc_txt}   "
              f"Fundações: {fund_txt}")
        print(f"  {DIM}(Est)        (Desc)             "
              f"(F0)    (F1)    (F2)    (F3){RESET}")
        print("─" * 58)

        # ── Tableau ───────────────────────────────────────────────────────────
        max_linhas = max((len(col) for col in self.mesa.tableau), default=0)
        print(f"  {NEGRITO}(0)   (1)   (2)   (3)   (4)   (5)   (6){RESET}")

        for linha_idx in range(max_linhas):
            row = ""
            for col in range(7):
                if linha_idx < len(self.mesa.tableau[col]):
                    row += self._formatar_carta(self.mesa.tableau[col][linha_idx]) + " "
                else:
                    row += "       "
            print(row)

        print("─" * 58)

    def _exibir_movimentos(self):
        """Lista todos os movimentos possíveis de forma legível."""
        movs = self.regras.movimentosPossiveis()

        print(f"\n{NEGRITO}{AMARELO}══ MOVIMENTOS POSSÍVEIS ══{RESET}")

        # Tableau → Tableau
        if movs:
            print(f"{CIANO}  Tableau → Tableau:{RESET}")
            for orig, dest, n in movs:
                carta = self.mesa.tableau[orig][-n]
                print(f"    T {orig} {dest} {n}   "
                      f"{self._formatar_carta(carta)} "
                      f"col {NEGRITO}{orig}{RESET} → col {NEGRITO}{dest}{RESET}")
        else:
            print(f"  {DIM}Nenhum movimento tableau disponível.{RESET}")

        # Tableau → Fundação
        print(f"{CIANO}  Tableau → Fundação:{RESET}")
        algum_fund = False
        for col in range(7):
            if self.mesa.tableau[col]:
                carta = self.mesa.tableau[col][-1]
                for f in range(4):
                    if self.regras.podeMoverParaFundacao(carta, f):
                        print(f"    F {col} {f}   "
                              f"{self._formatar_carta(carta)} "
                              f"col {NEGRITO}{col}{RESET} → fundação {NEGRITO}{f}{RESET}")
                        algum_fund = True
        if not algum_fund:
            print(f"  {DIM}Nenhum.{RESET}")

        # Descarte → ...
        if self.mesa.descarte:
            carta = self.mesa.descarte[-1]
            print(f"{CIANO}  Descarte → Tableau/Fundação:{RESET}")
            achou = False
            for col in range(7):
                if self.regras.podeMoverTableau(carta, col):
                    print(f"    D {col}   "
                          f"{self._formatar_carta(carta)} → col {NEGRITO}{col}{RESET}")
                    achou = True
            for f in range(4):
                if self.regras.podeMoverParaFundacao(carta, f):
                    print(f"    (descarte→fundação {f})   "
                          f"{self._formatar_carta(carta)} → fundação {NEGRITO}{f}{RESET}")
                    achou = True
            if not achou:
                print(f"  {DIM}Carta do descarte não tem destino válido.{RESET}")

        if self.mesa.estoque:
            print(f"{CIANO}  Estoque:{RESET} ainda há cartas – use {NEGRITO}E{RESET} para comprar.")

        input(f"\n{DIM}Pressione Enter para continuar...{RESET}")

    # ── LOOP PRINCIPAL ────────────────────────────────────────────────────────

    def _loop_principal(self):
        while True:
            self._exibir_mesa()

            # ── Vitória ───────────────────────────────────────────────────────
            if self._verificar_vitoria():
                print(f"\n{NEGRITO}{VERDE}{'★'*20}{RESET}")
                print(f"{NEGRITO}{VERDE}   PARABÉNS! VOCÊ VENCEU! {RESET}")
                print(f"{NEGRITO}{VERDE}{'★'*20}{RESET}")
                input(f"\n{DIM}Pressione Enter para sair...{RESET}")
                break

            # ── Game Over ────────────────────────────────────────────────────
            if not self._movimentos_disponiveis():
                print(f"\n{NEGRITO}{VERMELHO}{'✖'*20}{RESET}")
                print(f"{NEGRITO}{VERMELHO}   GAME OVER – sem movimentos! {RESET}")
                print(f"{NEGRITO}{VERMELHO}{'✖'*20}{RESET}")
                input(f"\n{DIM}Pressione Enter para sair...{RESET}")
                break

            # ── Status rápido ─────────────────────────────────────────────────
            n_movs = len(self.regras.movimentosPossiveis())
            if n_movs:
                print(f"{AMARELO}  ↪ {n_movs} movimento(s) no tableau disponíveis. "
                      f"Use M para listar.{RESET}")
            else:
                print(f"{VERMELHO}  ↪ Nenhum movimento no tableau. "
                      f"Compre do estoque (E) ou mova para fundação.{RESET}")

            # ── Menu ──────────────────────────────────────────────────────────
            print(f"\n{NEGRITO}COMANDOS:{RESET}")
            print("  E              - Comprar do estoque")
            print("  T [o] [d] [n]  - Mover bloco do tableau   Ex: T 0 1 1")
            print("  D [dest]       - Descarte → tableau        Ex: D 5")
            print("  F [orig] [f]   - Tableau → fundação        Ex: F 0 0")
            print("  DF [f]         - Descarte → fundação       Ex: DF 0")
            print("  M              - Ver movimentos possíveis")
            print("  S              - Sair")

            escolha = input(f"\n{NEGRITO}Comando:{RESET} ").upper().split()
            if not escolha:
                continue

            comando = escolha[0]
            try:
                if comando == 'S':
                    break

                elif comando == 'E':
                    self.mesa.descartar()

                elif comando == 'T':
                    orig, dest, n = int(escolha[1]), int(escolha[2]), int(escolha[3])
                    if self.movimento.moverBloco(orig, dest, n) == 'f':
                        input(f"{VERMELHO}  Movimento inválido! "
                              f"Pressione Enter...{RESET}")

                elif comando == 'D':
                    dest = int(escolha[1])
                    if self.movimento.descarteParaTableau(dest) == 'f':
                        input(f"{VERMELHO}  Movimento inválido! "
                              f"Pressione Enter...{RESET}")

                elif comando == 'F':
                    orig, fund = int(escolha[1]), int(escolha[2])
                    if self.movimento.tableauParaFundacao(orig, fund) == 'f':
                        input(f"{VERMELHO}  Movimento inválido! "
                              f"Pressione Enter...{RESET}")

                elif comando == 'DF':
                    fund = int(escolha[1])
                    if self.movimento.descarteParaFundacao(fund) == 'f':
                        input(f"{VERMELHO}  Movimento inválido! "
                              f"Pressione Enter...{RESET}")

                elif comando == 'M':
                    self._exibir_mesa()
                    self._exibir_movimentos()

                else:
                    input(f"{VERMELHO}  Comando desconhecido! "
                          f"Pressione Enter...{RESET}")

            except (IndexError, ValueError):
                input(f"{VERMELHO}  Argumentos inválidos! "
                      f"Pressione Enter...{RESET}")
            except Exception as e:
                input(f"{VERMELHO}  Erro inesperado: {e} – "
                      f"Pressione Enter...{RESET}")


# ──────────────────────────────────────────────────────────────────────────────
# TESTES RÁPIDOS
# Para ativar um teste, descomente a chamada correspondente em __main__.
# ──────────────────────────────────────────────────────────────────────────────

def _teste_vitoria():
    """
    Mesa quase vencida: fundações com A→Q em todos os naipes,
    e os 4 Reis expostos no tableau (um por coluna).
 
    Solução em 4 comandos:
        F 0 0   →  K♦ vai para fundação 0
        F 1 1   →  K♣ vai para fundação 1
        F 2 2   →  K♥ vai para fundação 2
        F 3 3   →  K♠ vai para fundação 3
    """
    mesa = Mesa.__new__(Mesa)
    mesa.tableau  = [[] for _ in range(7)]
    mesa.estoque  = []
    mesa.descarte = []
    mesa.fundacao = [[], [], [], []]
 
    # Naipes mapeados por índice de fundação: 0=♦ 1=♣ 2=♥ 3=♠
    naipes_ord = ['o', 'p', 'c', 'e']
 
    # Preenche fundações com A até Q (valores 1–12)
    for f_idx, naipe in enumerate(naipes_ord):
        for valor in range(1, 13):          # 1 a 12
            c = Carta(naipe, valor)
            c.face_up = True
            mesa.fundacao[f_idx].append(c)
 
    # Coloca um Rei de cada naipe no tableau (colunas 0–3), face up
    for col, naipe in enumerate(naipes_ord):
        rei = Carta(naipe, 13)
        rei.face_up = True
        mesa.tableau[col] = [rei]
 
    CLI(mesa=mesa)
 
 
def _teste_game_over():
    """
    Mesa que entra em game over rapidamente (em ~6 jogadas).
 
    Estado inicial
    ──────────────
    Tableau:
      Col 0: 8♣ (preto)   Col 1: 6♦ (vermelho)
      Col 2: 5♠ (preto)   Col 3: 4♥ (vermelho)
      Col 4: 3♠ (preto)   Cols 5–6: vazias
 
    Estoque (topo → fundo): 9♥, 2♦
    Descarte: vazio
    Fundação: vazia
 
    Movimentos possíveis
    ────────────────────
      1. T 1 0 1  →  6♦ sobre 8♣? ✗ (precisa de 7)
         T 2 1 1  →  5♠ sobre 6♦ ✓ (preto sobre vermelho, valor-1)
         T 3 2 1  →  4♥ sobre 5♠ ✓ (vermelho sobre preto, valor-1)
         T 4 3 1  →  3♠ sobre 4♥ ✓ (preto sobre vermelho, valor-1)
         E        →  compra 9♥ do estoque (vermelho – não encaixa em 8♣)
         E        →  compra 2♦ do estoque (sem Ás na fundação, sem 3 preto livre)
         → GAME OVER: sem estoque, sem movimentos válidos.
    """
    mesa = Mesa.__new__(Mesa)
    mesa.tableau  = [[] for _ in range(7)]
    mesa.estoque  = []
    mesa.descarte = []
    mesa.fundacao = [[], [], [], []]
 
    # Tableau: pares vermelho/preto sem sequência completa
    setup = [
        ('p', 8),   # col 0 – 8♣ preto
        ('o', 6),   # col 1 – 6♦ vermelho
        ('e', 5),   # col 2 – 5♠ preto
        ('c', 4),   # col 3 – 4♥ vermelho
        ('e', 3),   # col 4 – 3♠ preto
    ]
    for col, (naipe, valor) in enumerate(setup):
        c = Carta(naipe, valor)
        c.face_up = True
        mesa.tableau[col] = [c]
 
    # Estoque: 9♥ e 2♦  (nenhum encaixa após os movimentos acima)
    for naipe, valor in [('c', 9), ('o', 2)]:
        c = Carta(naipe, valor)
        c.face_up = False
        mesa.estoque.append(c)
 
    CLI(mesa=mesa)
# ──────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":

    # ── Jogo normal ───────────────────────────────────────────────────────────
    CLI()

   
    _teste_vitoria()

    # ── Teste: game over imediato ─────────────────────────────────────────────
    # _teste_game_over()