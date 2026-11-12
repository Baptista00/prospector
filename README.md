# Prospector

Encontra negócios de Brusque sem site próprio (via API do Google Places),
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
# edite o .env e cole sua chave em GOOGLE_MAPS_API_KEY
python main.py
```

## Chave da API (Google Cloud)

1. Acesse https://console.cloud.google.com e crie um projeto.
2. Ative a **Places API (New)** em "APIs e serviços".
3. Em "Credenciais", crie uma **chave de API** e cole no `.env`.
4. Recomendado: em "Faturamento", configure alerta de orçamento (ex.: R$ 10)
   e restrinja a chave à Places API. A cota gratuita mensal cobre com folga
   o uso normal deste projeto (poucas dezenas de buscas por mês).

## Fluxo de trabalho

1. `python main.py` — busca, atualiza o banco e gera `dados/prospects.xlsx`.
2. Abra a planilha, filtre por **Prioridade = Alta** e clique em **Abrir**
   na coluna WhatsApp: o WhatsApp abre com a mensagem pronta para revisar.
3. Marque a coluna **Status** (contatado, respondeu, fechado...) e anote
   observações.
4. Na próxima rodada, feche o Excel e rode `python main.py` de novo: o
   status que você marcou é preservado e empresas novas entram na lista.

## Estrutura

| Arquivo | Função |
|---|---|
| `config.py` | nichos, cidade, mensagem de abordagem |
| `main.py` | ponto de entrada |
| `prospector/places.py` | chamadas à API do Google Places |
| `prospector/filtro.py` | detecta "sem site" / "só rede social" |
| `prospector/pontuacao.py` | prioridade de cada empresa (0–100) |
| `prospector/banco.py` | SQLite (`dados/prospects.db`) |
| `prospector/mensagens.py` | texto e link `wa.me` |
| `prospector/exportar.py` | planilha `.xlsx` e leitura do status |

Para mudar os nichos ou a mensagem, edite só o `config.py`.
