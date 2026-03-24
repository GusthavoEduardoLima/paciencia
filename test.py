from deck import Deck # Ajuste o nome conforme seu arquivo
"""teste 100% gerado por IA"""
def rodar_testes():
    print("--- INICIANDO TESTES DO MOTOR ---")
    
    # 1. Teste de Instanciação
    meu_deck = Deck()
    print(f"Status: {meu_deck}") # Deve imprimir: O baralho tem 52
    
    # 2. Teste de Compra e Pilha
    carta1 = meu_deck.comprar()
    carta2 = meu_deck.comprar()
    
    print(f"Primeira carta tirada: {carta1}")
    print(f"Segunda carta tirada: {carta2}")
    print(f"Restante no deck: {len(meu_deck.cartas)}") # Deve ser 50
    
    # 3. Teste de Lógica (Seus métodos Dunder)
    print("\n--- TESTANDO COMPARAÇÕES ---")
    if carta1 == carta2:
        print("As cartas são iguais (Raro em um baralho de 52!)")
    elif carta1 > carta2:
        print(f"A carta {carta1.valor} é maior que {carta2.valor}")
    else:
        print(f"A carta {carta1.valor} é menor que {carta2.valor}")

    # 4. Teste de Cor (Sua regra de ouro da Paciência)
    print(f"Cor da Carta 1 ({carta1.naipe}): {carta1.cor}")
    print(f"Cor da Carta 2 ({carta2.naipe}): {carta2.cor}")
    
    if carta1.cor != carta2.cor:
        print("Cores diferentes: Movimento POSSÍVEL na mesa (se o valor bater).")
    else:
        print("Cores iguais: Movimento PROIBIDO na mesa.")

if __name__ == "__main__":
    rodar_testes()