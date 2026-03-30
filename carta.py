class Carta:
    def __init__(self, naipe, valor):
        self.naipe = naipe
        self.valor = valor
        self.cor = 'v' if naipe in ['o', 'c'] else 'p'
        self.face_up = False

    def __str__(self):
        return f"Carta: VALOR:{self.valor}, NAIPE: {self.naipe}.\n"

    def __repr__(self):
        return self.__str__()

    def __eq__(self, outro):
        if not isinstance(outro, Carta):
            return False
        return self.valor == outro.valor and self.naipe == outro.naipe

    def __hash__(self):
        # BUG FIX: sem __hash__, definir __eq__ torna a classe não-hashable em Python 3,
        # o que quebrava silenciosamente o dict reverso usado no arraste de blocos.
        return hash((self.naipe, self.valor))

    def __lt__(self, outro):
        if not isinstance(outro, Carta):
            return False
        return self.valor < outro.valor

    def __gt__(self, outro):
        if not isinstance(outro, Carta):
            return False
        return self.valor > outro.valor