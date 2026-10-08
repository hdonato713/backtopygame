def verifica_igual_porum(resposta, antiga, chute):
    if chute == resposta:
        return "Acertou!"
    else:
        i = 0
        for a in range(len(chute)):
            if chute[a] != antiga[a]:
                i += 1
        if i != 1:
            return "Tentativa inválida"
        else:
            antiga = chute
            return "boa!"


respota = "merda"
antiga = "perdo"
while verifica_igual_porum != "Acertou!":
    print(antiga)
    chute = input("\n") 





# print(verifica_igual_porum("olá", "quem sabe", "olá"))