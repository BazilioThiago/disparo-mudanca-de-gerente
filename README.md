# Disparo Mudança de Gerentes

Automação para envio de comunicações (push, e-mail e WhatsApp) aos associados da Cooperativa Sicredi quando há mudança de gerente de contas.
Segmenta a base de associados por agência, carteira, sistema (Legado/Digital), segmento (PF/PJ) e principalidade (Maduro/Outros), e realiza o disparo via:

- Portal de Engajamento (Push e E-mail)
- API WhatsApp (Cooperatech)

---

## Funcionalidades

- Filtra e separa associados por critérios de negócio
- Envio de notificações automatizado:
  - PF Digital → Push (Web)
  - PF Legado (Maduro) → WhatsApp (API)
  - PF Legado (Outros) → E-mail (Web)
  - PJ Maduro → WhatsApp (API)
  - PJ Outros → Geração de relatório Excel
- Registro de resultados de cada envio em planilha de logs

---

## Pré-requisitos

- Python 3.8 ou superior
- Microsoft Edge (navegador)
- Edge WebDriver compatível (PATH_DRIVER)

## Instalação

1. Clone este repositório
2. Crie e ative um ambiente virtual:
   ```powershell
   python -m venv venv
   .\venv\Scripts\activate
   ```
3. Instale dependências:
   ```powershell
   pip install -r requirements.txt
   ```
4. Configure `parametros.txt` na raiz do projeto com textos de campanha
5. Ajuste os caminhos e tokens em `globals.py` ou variáveis de ambiente

---

## Estrutura de Pastas

```
├── bin/                    Executável e arquivos binários
├── data/                   Tabelas geradas e arquivos usados (bases CSV)
├── docs/                   Arquivos e documentação
├── logs/                   Logs e screenshots
├── src/                    Código-fonte
│   ├── bases.py            Preparação das bases
│   ├── web.py              Automação do Portal de Engajamento
│   ├── mtls.py             Disparo via API WhatsApp
│   ├── navigations.py      Helpers Selenium e logs
│   └── gui.py              Interface com telas_2606
├── globals.py              Constantes e variáveis globais (melhor que .env)
├── parametros.txt          Parâmetros das campanhas
├── app.py                  Código principal
├── requirements.txt        Dependências Python
└── installer_command.txt   Comandos pra gerar o executável
```

---

## Configuração do Ambiente

Em `globals.py`, revise e ajuste os seguintes parâmetros:

- **CLIENT_ID**, **CLIENT_SECRET**, **USERNAME**, **PASSWORD** e **SCOPE** da API
- **PATH_DRIVER** → caminho para o executável do Edge WebDriver
- **PATH_BASES** → pasta onde estão os arquivos CSV de base
- **PATH_LOGS** → pasta onde logs e relatórios serão salvos

## Configuração de Campanha

Edite `parametros.txt` na raiz do projeto para ajustar textos:

```txt
NOME_CAMPANHA = "Título da campanha"
DES_CAMPANHA = "Descrição breve"
ASSUNTO_EMAIL = "Assunto do e-mail"
PREVIA_EMAIL = "Texto da prévia"
CORPO_EMAIL = "Conteúdo do e-mail com {S} para quebra de linha"
TITULO_PUSH = "Título da notificação Push"
MSG_PUSH = "Mensagem da notificação Push"
```

---

## Uso da Aplicação

Execute o orquestrador principal:

```powershell
python app.py
```

Fluxo de execução:

1. Tela de login (e-mail e senha)
2. Informar agência, carteira e novo gerente
3. Confirmação na tela principal
4. Automação faz envios e publica campanhas
5. Tela final exibe resumo dos resultados

---

## Logs e Relatórios

- Envios: resultados salvos em `logs/linhas_enviadas.xlsx`
- Campanhas: logs detalhados em `logs/`

---

## Contribuição

Pull requests são bem-vindos. Para grandes mudanças, abra uma issue primeiro para discutir o que você deseja mudar.
Certifique-se de atualizar os testes, se aplicável.

---

**Autor:** *Thiago Bazilio*
**&copy;2025 Sicredi Vale Litoral SC**
