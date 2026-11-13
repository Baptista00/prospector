# Prospector

Encontra negócios de Brusque sem site próprio (dados do Google Maps, via SerpApi
ou Google Places API),
pontua os melhores alvos e gera uma planilha com link de WhatsApp pronto
para abordagem. **Nada é enviado automaticamente** — você revisa e envia.

## Como rodar

```powershell
cd $HOME\Documents\prospector
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt

# Teste sem chave da API (dados fictícios):
python main.py --demo

# Busca de verdade:
copy .env.example .env
# edite o .env e cole sua chave em SERPAPI_KEY
python main.py
```

## Chave da API

O provedor é escolhido em `PROVEDOR` no `config.py`.

**SerpApi (padrão, gratuito e sem cartão)**
1. Crie uma conta em https://serpapi.com/users/sign_up e confirme o e-mail.
2. Copie sua chave em https://serpapi.com/manage-api-key.
3. Cole no `.env` em `SERPAPI_KEY`.

O plano gratuito dá 250 buscas por mês. Cada nicho usa 1 ou 2 buscas,
então uma rodada com 5 nichos gasta cerca de 10.

**Google Places API (New) (opcional)**
Exige conta de faturamento no Google Cloud. Ative a Places API (New), crie
uma chave restrita a ela, cole em `GOOGLE_MAPS_API_KEY` e troque
`PROVEDOR = "google"` no `config.py`.

## Fluxo de trabalho

1. `python main.py` — busca, atualiza o banco e gera `dados/prospects.xlsx`.
2. Abra a planilha, filtre por **Prioridade = Alta** e clique em **Abrir**
   na coluna WhatsApp: o WhatsApp abre com a mensagem pronta para revisar.
3. Marque a coluna **Status** (contatado, respondeu, fechado...) e anote
   observações.
4. Na próxima rodada, feche o Excel e rode `python main.py` de novo: o
   status que você marcou é preservado e empresas novas entram na lista.
5. Quando publicar a prévia de uma empresa, cole o endereço na coluna
   **Link da prévia**. Ele também é preservado entre as rodadas.

Para só reorganizar a planilha sem gastar buscas da API (por exemplo,
depois de editar status, observações ou links):

```powershell
python main.py --sem-busca
```

## Estrutura

| Arquivo | Função |
|---|---|
| `config.py` | nichos, cidade, mensagem de abordagem |
| `main.py` | ponto de entrada |
| `prospector/places.py` | busca na SerpApi ou na Google Places API |
| `prospector/filtro.py` | detecta "sem site" / "só rede social" |
| `prospector/pontuacao.py` | prioridade de cada empresa (0–100) |
| `prospector/banco.py` | SQLite (`dados/prospects.db`) |
| `prospector/mensagens.py` | texto e link `wa.me` |
| `prospector/exportar.py` | planilha `.xlsx` e leitura do status |

Para mudar os nichos ou a mensagem, edite só o `config.py`.
