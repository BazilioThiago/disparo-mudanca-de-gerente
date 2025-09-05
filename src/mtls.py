import requests
import sys
import os
if "src" not in sys.path:
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from globals import Constants
from src.navigations import USER, Logs

# region MTLS
logger = Logs.load_log(__name__)


class Disparo:

    def __init__(self): # Get Token
        token = requests.post( 
            url = Constants.EP_MTLS_TOKEN, 
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
                'Cache-control': 'no-cache'
            }, 
            data = {
                "client_id": Constants.CLIENT_ID,
                "client_secret": Constants.CLIENT_SECRET,
                "grant_type": Constants.GRANT_TYPE,
                "password": Constants.PASSWORD,
                "scope": Constants.SCOPE,
                "username": Constants.USERNAME
            }
            )

        if(token.status_code == 200): # Sucesso no envio
            self.token = token.json()['access_token']
        else: # Falha no envio
            logger.error(f"Falha no Get Token - código {token.status_code}")


    def disparo_whats(self, celular: str, agencia: str, conta: str, associado: str, gerente: str, template: str) -> int:
        retorno = requests.post( 
            url = Constants.EP_DISPARO_WHATS,
            headers = {
                'authorization' : 'Bearer ' + self.token,
                'x-api-coop-user' : USER,
                'x-api-coop-numero': '2606',
                'x-api-coop-aplicacao': 'python 0203080_Disparo Mudanca de Gerente'
            }, 
            json = {
                "customerBranchNum": agencia,
                "customerAccountNum": conta,
                "customerCoopCode": '2606',
                "customerPhoneNum": "55"+celular,
                "originCompany": "coop_2606",
                "originSystem": "WhatsApp Sicredi",
                "originUsername": "rpa_api_2606",
                "templateName": template,
                "templateParameters": {
                    "nome_associado": associado,
                    "nome_cooperativa": "Vale Litoral SC",
                    "nome_gestor": gerente
                }
            }, 
            cert = (
                Constants.PATH_CERTIFICADO,
                Constants.PATH_COOP_KEY
                )
            )

        if(retorno.status_code == 200): # Sucesso no envio
            return 1
        else: # Falha no envio
            logger.error(f"Falha no disparo - código {retorno.status_code}: {retorno.text}")
            return 0


# Para fins de teste
if __name__ == '__main__':
    teste = Disparo()
    celular = '47996277671'
    agencia = '33'
    conta = '999999'
    associado = 'thiago bazilio'
    gerente = 'Matheus Teste da Silva'
    template = 'generico_novo_gerente_contapf'
    #template = 'generico_novo_gerente_contapj'
    print( teste.disparo_whats(celular, agencia, conta, associado, gerente, template) )
