from telas_2606 import tela_botoes, tela_mensagem, tela_mudanca_gerentes
import sys
import os
if "src" not in sys.path:
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from globals import Constants

#region GUI

class Screens:

    @classmethod
    def info_gerente(cls) -> dict:
        info = tela_mudanca_gerentes.run()

        if not info:
            raise Exception("Tela de mudança de gerentes encerrada.")
        else:
            return info
    

    @classmethod
    def principal(cls, titulo: str) -> str:
        escolha = tela_botoes.run(["Fazer envios"], titulo) # Botão de enviar

        if not escolha:
            raise Exception("Tela principal encerrada.")
        else:
            return escolha
        

    @classmethod
    def final(cls, mensagem: str = "Envios finalizados!\nLog disponível para verificação."):
        tela_mensagem.run(mensagem)


# Para fins de teste
if __name__ == '__main__':
    print(Screens.principal())
