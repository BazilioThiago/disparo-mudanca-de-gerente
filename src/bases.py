import pandas as pd
import requests
import sys
import os
if "src" not in sys.path:
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from globals import Constants as cs
from src.navigations import Logs

#region BASES
LOG = Logs.load_log(__name__)


class Databricks():

    def __init__(self):
        self.endpoint= cs.EP_DATABRICKS
        self.headers = {"Authorization": f"Bearer {cs.DATABRICKS_TOKEN}"}

    def get_table_csv(self, table: str, download_name: str) -> None:
        response = requests.request("GET", url=f"{self.endpoint}/{table}", headers=self.headers)

        if response.status_code == 200:
            with open(f"{cs.PATH_BASES}/{download_name}.csv", 'wb') as file:
                file.write(response.content)
            # print(f"File downloaded successfully as {download_name}.csv")
        else:
            # print(f"Failed to download file. Status code: {response.status_code}, Response: {response.text}")
            LOG.error(f"Failed to download file. Status code: {response.status_code}, Response: {response.text}")


class Bases():
    '''
    Bases ::
        --Associados PF:
        Plataforma - Push (portal)
        Legado, principalidade maduro - Whats (api)
        Legado, outros - email (portal)

        --Associados PJ:
        Principalidade maduro - Whats (api)
        Outros - email (analisar)
    '''
    def __init__(self, agencia: int, carteira: int):
        self.lista_dfs = []
        self.databricks = Databricks()

        self.databricks.get_table_csv("mudanca_gestores.csv", "mudanca_gestores") # Atualiza a tabela mudanca_gestores
        df = pd.read_csv(f"{cs.PATH_BASES}/mudanca_gestores.csv")

        df['telefone'] = df['telefone'].astype(str).str.rstrip(',') # Remove a vírgula no final do telefone
        df['telefone'] = pd.to_numeric(df['telefone'], errors='coerce').fillna(0).astype(int) # Converte para inteiro, substituindo vazios por 0

        df = df[df['agencia'] == agencia]
        df['carteira'] = pd.to_numeric(df['carteira'], errors='coerce').fillna(0).astype(int)
        df = df[df['carteira'] == carteira]

        self.df_pf = df[(df['segmento'] == 'PF') & (df['flg_digital'].notna())]
        self.df_pj = df[(df['segmento'] == 'PJ')]


    def preparar_df(self, id_base: int) -> pd.DataFrame:
        match id_base:
            case 0:
                dataframe = self.df_pf[self.df_pf['flg_digital'] == 'S']
            case 1:
                dataframe = self.df_pf[(self.df_pf['flg_digital'] == 'N') & (self.df_pf['faixa_principalidade'] == 'Maduro')]
                dataframe = dataframe[dataframe['telefone'] != 0]
            case 2:
                dataframe = self.df_pf[(self.df_pf['flg_digital'] == 'N') & (self.df_pf['faixa_principalidade'] != 'Maduro')]
                dataframe = dataframe[dataframe['faixa_principalidade'].notna()]
            case 3:
                dataframe = self.df_pj[self.df_pj['faixa_principalidade'] == 'Maduro']
                dataframe = dataframe[dataframe['telefone'] != 0]
            case 4:
                dataframe = self.df_pj[self.df_pj['faixa_principalidade'] != 'Maduro']
                dataframe = dataframe[dataframe['faixa_principalidade'].notna()]

        dataframe = dataframe.drop_duplicates(subset=['cpf_cnpj'])
        return dataframe


    def preparar_bases(self) -> tuple:
        '''
        Retorna os dataframes
            0: Pf digital
            1: Pf maduro
            2: Pf outros
            3: Pj maduro
            4: Pj outros
        '''
        pf_digital = self.preparar_df(0)
        pf_maduro = self.preparar_df(1)
        pf_outros = self.preparar_df(2)
        pj_maduro = self.preparar_df(3)
        pj_outros = self.preparar_df(4)

        pf_digital.to_csv(f"{cs.PATH_BASES}/pf_digital.csv", index=False)
        pf_maduro.to_csv(f"{cs.PATH_BASES}/pf_maduro.csv", index=False)
        pf_outros.to_csv(f"{cs.PATH_BASES}/pf_outros.csv", index=False)
        pj_maduro.to_csv(f"{cs.PATH_BASES}/pj_maduro.csv", index=False)
        pj_outros.to_csv(f"{cs.PATH_BASES}/pj_outros.csv", index=False)

        pf_digital['cpf_cnpj'].to_csv(f"{cs.PATH_BASES}/cpf_cnpj-pf_digital.csv", index=False, header=False)
        pf_outros['cpf_cnpj'].to_csv(f"{cs.PATH_BASES}/cpf_cnpj-pf_outros.csv", index=False, header=False)

        return (pf_digital, pf_maduro, pf_outros, pj_maduro, pj_outros)


# Para fins de teste
if __name__ == '__main__':
    bases = Bases(33, 131)
    print(bases.preparar_bases())
