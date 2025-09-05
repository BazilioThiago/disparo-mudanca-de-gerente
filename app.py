from datetime import datetime
from pathlib import Path
import pandas as pd
import os
from globals import Constants as cs
from src.navigations import Logs, USER
from src.web import PortalEngajamento
from src.mtls import Disparo
from src.bases import Bases
from src.gui import Screens

LOG = Logs.load_log(__name__)

# 0203080_Disparo_Mudança_de_Gerente
#responsável: Thiago Bazilio


#region registrar_resultado
def registrar_resultado(dataframe: pd.DataFrame) -> None:
    '''
    Registra os resultados dos envios no excel de log
    '''
    log_path = Path(cs.PATH_LOGS) / "linhas_enviadas.xlsx"

    if log_path.exists():
        # Se já existe, lê e concatena
        existente = pd.read_excel(log_path)
        combinado = pd.concat([existente, dataframe], ignore_index=True)
    else:
        # Se não existe, apenas usa o df atual
        combinado = dataframe

    # Salva de volta no Excel
    combinado.to_excel(log_path, index=False)


#region ler_parametros
def ler_parametros() -> tuple[str, str, str, str, str, str, str]:
    '''
    Lê os parâmetros de campanha de parametros.txt
        Retornos:
            nome_campanha | des_campanha | assunto_email | previa_email | corpo_email | titulo_push | msg_push
    '''
    params = {}
    config_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'parametros.txt'))
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                if '=' in line:
                    key, val = line.split('=', 1)
                    key = key.strip()
                    # Remove aspas externas
                    val = val.strip().strip('"')
                    params[key] = val
    except FileNotFoundError:
        LOG.error(f"Arquivo de parâmetros não encontrado: {config_path}")
        raise

    # Retorna valores na ordem esperada
    return (
        params.get('NOME_CAMPANHA'),
        params.get('DES_CAMPANHA'),
        params.get('ASSUNTO_EMAIL'),
        params.get('PREVIA_EMAIL'),
        params.get('CORPO_EMAIL'),
        params.get('TITULO_PUSH'),
        params.get('MSG_PUSH'),
    )


#region fazer_envios
def fazer_envios(pf_digital, pf_maduro, pf_outros, pj_maduro, pj_outros, novo_gerente: str) -> tuple[bool, bool, int, int]:
    '''
    Retorno
        resultado_campanha_digital | resultado_campanha_legado | sucessos_whats | falhas_whats
    '''
    retorno1: bool = False
    retorno2: bool = False
    sucessos_whats: int = 0
    falhas_whats: int = 0

    # Envia whatsapp
    if not pf_maduro.empty or not pj_maduro.empty: 
        disparo = Disparo()

        if not pf_maduro.empty: # PF Maduro
            for index, row in pf_maduro.iterrows():
                celular = str(row['telefone'])
                conta = str(row['conta'])
                agencia = str(row['agencia']).zfill(2) # Completa 2 dígitos pra agência
                associado = str(row['nome']).split()[0].capitalize()  # Só o primeiro nome, com caps no inicial

                result = disparo.disparo_whats(celular, agencia, conta, associado, novo_gerente, 'generico_novo_gerente_contapf')

                # registra o resultado do disparo em uma nova coluna, e a data
                pf_maduro.loc[index, 'resultado_whats'] = 'Sucesso' if result == 1 else 'Falha'
                pf_maduro.loc[index, 'data_hora_envio'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                if result == 1: sucessos_whats += 1
                elif result == 0: falhas_whats += 1

            # Atualiza o arquivo com os resultados de cada linha
            registrar_resultado(pf_maduro)

        if not pj_maduro.empty: # PJ Maduro
            for index, row in pj_maduro.iterrows():
                celular = str(row['telefone'])
                conta = str(row['conta'])
                agencia = str(row['agencia']).zfill(2) # Completa 2 dígitos pra agência
                associado = str(row['nome']).split()[0].capitalize()  # Só o primeiro nome, com caps no inicial

                result = disparo.disparo_whats(celular, agencia, conta, associado, novo_gerente, 'generico_novo_gerente_contapj')

                # registra o resultado do disparo em uma nova coluna, e a data
                pj_maduro.loc[index, 'resultado_whats'] = 'Sucesso' if result == 1 else 'Falha'
                pj_maduro.loc[index, 'data_hora_envio'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                if result == 1: sucessos_whats += 1
                elif result == 0: falhas_whats += 1

            # Atualiza o arquivo com os resultados de cada linha
            registrar_resultado(pj_maduro)

        LOG.info(f"Disparo WhatsApp - Sucessos: {sucessos_whats}, Falhas: {falhas_whats}")

    # Cria as campanhas no portal
    if not pf_digital.empty or not pf_outros.empty:
        portal = PortalEngajamento()
        portal.login_portal()
        nome_camp, des_camp, as_em, prev_em, body_em, tit_push, msg_push = ler_parametros()

        if not pf_digital.empty: # PF Digital
            digital_path = os.path.abspath(os.path.join(cs.PATH_BASES, "cpf_cnpj-pf_digital.csv"))
            
            retorno1 = portal.criar_campanha('Digital', novo_gerente, digital_path, nome_camp, des_camp, as_em, prev_em, body_em, tit_push, msg_push)
            LOG.info(f"Campanha Digital ({len(pf_digital)} associados) - {('Sucesso' if retorno1 else 'Falha')}")

            # registra o resultado em todas as linhas e adiciona a data atual
            pf_digital['resultado_whats'] = 'Sucesso' if retorno1 else 'Falha'
            pf_digital['data_hora_envio'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            registrar_resultado(pf_digital)

        if not pf_outros.empty: # PF Outros
            outros_path = os.path.abspath(os.path.join(cs.PATH_BASES, "cpf_cnpj-pf_outros.csv"))

            retorno2 = portal.criar_campanha('Legado', novo_gerente, outros_path, nome_camp, des_camp, as_em, prev_em, body_em, tit_push, msg_push)
            LOG.info(f"Campanha Legado ({len(pf_outros)} associados) - {('Sucesso' if retorno2 else 'Falha')}")

            # registra o resultado em todas as linhas e adiciona a data atual
            pf_outros['resultado_whats'] = 'Sucesso' if retorno2 else 'Falha'
            pf_outros['data_hora_envio'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            registrar_resultado(pf_outros)

        portal.encerrar()

    return (retorno1, retorno2, sucessos_whats, falhas_whats)


#region Main
def main():
    LOG.info("::Iniciando o script de Disparo Mudança de Gerente::")
    LOG.info("|"+USER)
    encontrados: str = ""
    resultados: str = ""

    # Obtém informações pela interface
    info = Screens.info_gerente()
    agencia: int = int(info['agencia'])
    carteira: int = int(info['carteira'])
    novo_gerente: str = info['gerente']
    LOG.info(f"Agência: {agencia}, Carteira: {carteira}, Novo Gerente: {novo_gerente}")

    # Filtra as bases
    b = Bases(agencia, carteira)
    pf_digital, pf_maduro, pf_outros, pj_maduro, pj_outros = b.preparar_bases()
    LOG.info(f"pf_digital: {len(pf_digital)}, pf_maduro: {len(pf_maduro)}, pf_outros: {len(pf_outros)}, pj_maduro: {len(pj_maduro)}, pj_outros: {len(pj_outros)}")

    # Mostra as bases encontradas
    encontrados += f"| PF Digital: {len(pf_digital)} |" if len(pf_digital) > 0 else ""
    encontrados += f"| PF Maduro: {len(pf_maduro)} |" if len(pf_maduro) > 0 else ""
    encontrados += f"| PF Outros: {len(pf_outros)} |" if len(pf_outros) > 0 else ""
    encontrados += f"| PJ Maduro: {len(pj_maduro)} |" if len(pj_maduro) > 0 else ""
    encontrados += f"| PJ Outros: {len(pj_outros)} |" if len(pj_outros) > 0 else ""

    enviar = Screens.principal(encontrados)

    if enviar: # Resultados dos envios
       r1, r2, green, red = fazer_envios(pf_digital, pf_maduro, pf_outros, pj_maduro, pj_outros, novo_gerente)
       resultados += f"{("Sucesso" if r1 else "Falha")} na Campanha Digital ({len(pf_digital)} associados).\n" if len(pf_digital) > 0 else ""
       resultados += f"{("Sucesso" if r2 else "Falha")} na Campanha Legado ({len(pf_outros)} associados).\n" if len(pf_outros) > 0 else ""
       resultados += f"{green} envios de whatsapp com sucesso.\n" if green > 0 else ""
       resultados += f"{red} envios com falha.\n" if red > 0 else ""

    # Mostra os resultados
    Screens.final(f"Envios finalizados! Log disponível para verificação.\n{resultados}")


# app.py main()
if __name__ == '__main__':
    try: 
        main()
    finally: 
        LOG.info("Aplicativo finalizado.\n")
