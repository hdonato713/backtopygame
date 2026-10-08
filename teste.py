import pywhatkit
mensagem = "Oi Henrique bom dia, acerte seu numero"

lista = [
    "+5511942339302"
]
for e in range(10):
    for numero in lista:
        pywhatkit.sendwhatmsg_instantly(
            numero,
            mensagem,
            wait_time=10,
            tab_close=True,
            close_time=3
        ) 