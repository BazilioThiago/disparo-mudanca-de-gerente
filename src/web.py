from selenium.webdriver.common.keys import Keys
from datetime import datetime, timedelta
import time
import sys
import os
if "src" not in sys.path:
     sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))) # pra poder rodar tanto pelo main (app.py) quanto direto (web.py)
from globals import Constants as cs
from src.navigations import Browser, Logs

#region WEB
LOG = Logs.load_log(__name__)


class PortalEngajamento:

    def __init__(self): 
        driver = Browser()
        self.driver = driver.set_browser()
        self.link_portal = 'https://portal-aplicacoes.prd-sicredi.in/admin/engajamento-digital/campanhas/2606/'
        

    def login_portal(self) -> bool:
        try: # Preenche email, senha e confirma
            self.driver.get(self.link_portal)
            time.sleep(3)

            Browser.wait_until_located(self.driver, 10, "xpath", "//*[@role='avatar']")
            # LOG.info("Sucesso ao logar no portal")
            time.sleep(2)
            return True

        except Exception as e:
            self.driver.save_screenshot(os.path.join(cs.PATH_LOGS, "screenshots", "error_screenshot(login_portal).png"))
            LOG.error(f"Falha no login_portal: {e}")
            return False
        

    def criar_campanha(
            self, 
            base: str, 
            gerente: str, 
            path_planilha_cpfs: str, 
            nome_campanha: str, 
            des_campanha: str, 
            assunto_email: str, 
            previa_email: str, 
            corpo_email: str, 
            titulo_push: str, 
            msg_push: str
            ) -> bool:
        try: # Começa uma campanha Legado ou Digital do tipo Relacionamento
            # LOG.info(f"-Campanha {base} Iniciada")
            # print(f"-Campanha {base} Iniciada")
            
            tentativas = 0
            if base == "Legado": 
                self.driver.get(self.link_portal + 'relacionamento/registro-campanha/?legado=true')
            else: #Digital
                self.driver.get(self.link_portal + 'relacionamento/registro-campanha/')

            # Preenche a campanha
            while True:
                try:
                    preenche = Browser.wait_until_located(self.driver, 10, 'id', 'name-input') # Nome da campanha
                    preenche.click()
                    data = (datetime.now() + timedelta(days=1)).strftime("%d/%m/%Y")
                    preenche.send_keys(f"{nome_campanha}\t{nome_campanha}\t{data}\t{data}\t\t\n")

                except Exception as e:
                    tentativas += 1
                    if tentativas >= 4: # Tenta 4 vezes
                        LOG.error(f"Falha ao preencher a campanha após {tentativas} tentativas: {e}")
                        raise
                    time.sleep(4) # Espera 4 segundos e tenta novamente
                else:
                    tentativas = 0
                    time.sleep(1)
                    break # Sai do loop se deu certo

            # Anexa a planilha dos CPFs e avança
            while True:
                try:
                    anexo = Browser.wait_until_located(self.driver, 10, 'id', 'files-file') # Campo de anexo
                    anexo.send_keys(path_planilha_cpfs)
                    time.sleep(3)
                    Browser.click_element_by_text(self.driver, "//*[@type='button' and @class='_84478122-07ba-4625-8dcf-141fec3ec0aa']", "Avançar")

                except Exception as e:
                    tentativas += 1
                    if tentativas >= 4: # Tenta 4 vezes
                        LOG.error(f"Falha ao anexar a planilha após {tentativas} tentativas: {e}")
                        raise
                    time.sleep(4) # Espera 4 segundos e tenta novamente
                else:
                    tentativas = 0
                    time.sleep(3)
                    break # Sai do loop se deu certo
            
            # Avança na lista de contatos
            while True:
                try: 
                    Browser.click_element_by_text(self.driver, "//*[@type='button' and @class='_84478122-07ba-4625-8dcf-141fec3ec0aa']", "Avançar")

                finally:
                    tentativas += 1
                    if tentativas >= 3: # Força o clique 3 vezes
                        tentativas = 0
                        break
                    time.sleep(3) # Espera 3 segundos e tenta novamente

            # Cria e preenche a Comunicação
            while True:
                try:
                    time.sleep(2)
                    Browser.click_element_by_text(self.driver, "//*[@class='_8b879481-bec8-4b28-b12c-e96750590ec0']", "Criar comunicação")
                    
                    if base == "Legado": 
                        pass
                    else: #Digital
                        Browser.click_element_by_text(self.driver, "//*[@class='_24c2aae8-4c0e-410a-98b4-814d7db15db0']", "Notificações por push")

                    comunicacao = Browser.wait_until_clickable(self.driver, 10, 'id', 'objective-input') # Objetivo de negócio
                    comunicacao.click()
                    comunicacao.send_keys(f'{des_campanha}\t{data}')
                    Browser.click_element_by_text(self.driver, "//*[@class='_24c2aae8-4c0e-410a-98b4-814d7db15db0']", "Relacionamento")
                    time.sleep(3)
                    
                    Browser.click_element_by_text(self.driver, "//*[@class='_d5ce4403-ee45-43d9-b028-de631862c96f " \
                    "_941d8c70-a534-423b-809d-41d2d9893a69']", "Como você gostaria de definir o horário de envio?")
                    hora = Browser.wait_until_clickable(self.driver, 10, 'id', 'undefined-input') # Hora do envio
                    hora.click()
                    hora.send_keys(Keys.DOWN)
                    hora.send_keys(Keys.RETURN)
                    hora.send_keys(f'\t\t\t\t')
                    hora.send_keys(Keys.RETURN) # 

                except Exception as e:
                    tentativas += 1
                    if tentativas >= 4: # Tenta 4 vezes
                        LOG.error(f"Falha ao preencher a Comunicação após {tentativas} tentativas: {e}")
                        raise
                    time.sleep(4) # Espera 4 segundos e tenta novamente
                else:
                    tentativas = 0
                    time.sleep(2)
                    break # Sai do loop se deu certo

            # Cria a Peça
            while True:
                try:
                    Browser.click_element_by_text(self.driver, "//*[@class='_8b879481-bec8-4b28-b12c-e96750590ec0']", "Criar peça")

                except:
                    tentativas += 1
                    if tentativas >= 4: # Tenta 4 vezes
                        LOG.error(f"Falha ao criar a Peça após {tentativas} tentativas: {e}")
                        raise
                    time.sleep(5) # Espera 5 segundos e tenta novamente
                else:
                    tentativas = 0
                    time.sleep(2)
                    break # Sai do loop se deu certo
            
            # Preenche a Peça
            while True:
                try:
                    if base == "Legado": 
                        aemail = Browser.wait_until_located(self.driver, 10, 'id', 'subject-input') # Assunto do Email
                        aemail.send_keys(assunto_email)

                        previa_email = previa_email.replace("{NOME_GERENTE}", gerente)
                        pemail = Browser.wait_until_located(self.driver, 10, 'id', 'previewText-input') # Texto da prévia
                        pemail.send_keys(previa_email)

                        # Sem imagem
                        # Browser.click_element_by_text(self.driver, "//*[@class='_fc7e7792-6b86-45b9-9d54-66cb738bc272']", "Não usar imagem")
                        #Com imagem
                        Browser.click_element_by_text(self.driver, "//*[@class='_8b879481-bec8-4b28-b12c-e96750590ec0']", "Escolher Imagem")
                        Browser.click_element_by_text(self.driver, "//*[@class='style_label__fr5XG']", "Colaboradora do Sicredi apertando")
                        Browser.click_element_by_text(self.driver, "//*[@class='_8b879481-bec8-4b28-b12c-e96750590ec0']", "Confirmar")

                        Browser.click_element_by_text(self.driver, "//*[@class='_fc7e7792-6b86-45b9-9d54-66cb738bc272']", "Escrever um título com o nome do associado no fim")
                        
                        temail = Browser.wait_until_located(self.driver, 10, 'id', 'title-input') # Título do Email
                        temail.send_keys("Olá")

                        Browser.click_element_by_text(self.driver, "//*[@class='_fc7e7792-6b86-45b9-9d54-66cb738bc272']", "E-mail sem botão final")

                        body_email = corpo_email.replace("{NOME_GERENTE}", gerente).replace("{S}", "\n")
                        cemail = Browser.wait_until_located(self.driver, 10, 'xpath', "//*[@class='tiptap ProseMirror']") # Corpo do Email
                        cemail.click()
                        cemail.send_keys(body_email)

                    else: #Digital
                        tpush = Browser.wait_until_located(self.driver, 10, 'id', 'title-input') # Título do Push
                        tpush.send_keys(titulo_push)
                        
                        mensagem_push = msg_push.replace("{NOME_GERENTE}", gerente)
                        mpush = Browser.wait_until_located(self.driver, 10, 'id', 'description-textarea') # Mensagem do Push
                        mpush.send_keys(mensagem_push)

                except Exception as e:
                    tentativas += 1
                    if tentativas >= 4: # Tenta 4 vezes
                        LOG.error(f"Falha ao preencher a Peça após {tentativas} tentativas: {e}")
                        raise
                    time.sleep(4) # Espera 4 segundos e tenta novamente
                else:
                    tentativas = 0
                    time.sleep(1)
                    break # Sai do loop se deu certo
            
            #Avança até a última aba
            acertos = 0
            while True:
                try:
                    Browser.click_element_by_text(self.driver, "//*[@class='_8b879481-bec8-4b28-b12c-e96750590ec0']", "Avançar")

                except:
                    tentativas += 1
                    if tentativas >= 4: # Tenta 4 vezes
                        LOG.error(f"Falha ao avançar até a última página após {tentativas} tentativas: {e}")
                        raise
                    time.sleep(5) # Espera 5 segundos e tenta novamente
                else:
                    acertos += 1
                    if acertos >= 4:
                        tentativas = 0
                        acertos = 0
                        time.sleep(2)
                        break # Sai do loop se deu certo (4 avanços)
                    time.sleep(2)

            # Concorda com os termos e publica a Campanha
            while True:
                try:
                    self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    time.sleep(1)
                    Browser.click_element_by_text(self.driver, "//*[@class='_9724235a-bd52-4ac8-a845-8732cbe7b593 " \
                    "_0e541f30-a6d1-4b24-b748-cc6913d6d40e _e57f8bee-b27b-40df-b589-ecc987f382a7']", "Li e concordo com os")
                    Browser.click_element_by_text(self.driver, "//*[@class='_8b879481-bec8-4b28-b12c-e96750590ec0']", "Publicar campanha")
                    time.sleep(1)
                    # Mensagem de campanha publicada
                    Browser.wait_until_located(self.driver, 10, "xpath", "//*[@class='_d5ce4403-ee45-43d9-b028-de631862c96f _399716f3-3bac-4bdd-806d-7f323123a757']")

                except Exception as e:
                    tentativas += 1
                    if tentativas >= 4: # Tenta 4 vezes
                        LOG.error(f"Falha ao publicar a Campanha após {tentativas} tentativas: {e}")
                        raise
                    time.sleep(4) # Espera 4 segundos e tenta novamente
                else:
                    tentativas = 0
                    time.sleep(2)
                    break # Sai do loop se deu certo

        except: #Exceção Geral
            self.driver.save_screenshot(os.path.join(cs.PATH_LOGS, "error_screenshot(criar_campanha).png"))
            LOG.error(f"x--Falha ao criar campanha {base}--x")
            return False
        
        else: # Se deu tudo certo
            LOG.info(f"-Campanha {base} Publicada")
            # print("-Campanha Publicada")
            time.sleep(1)
            return True


    def encerrar(self):
        self.driver.quit()


# Para fins de teste
if __name__ == '__main__':
    teste = PortalEngajamento()
    teste.login_portal()
    teste.criar_campanha()
    teste.encerrar()
