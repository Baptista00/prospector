"""Configurações do prospector. Edite aqui os nichos e a cidade."""

CIDADE = "Brusque, SC"

# De onde vêm os dados:
#   "serpapi" -> SerpApi, plano gratuito sem cartão (chave SERPAPI_KEY no .env)
#   "google"  -> Google Places API (New) (chave GOOGLE_MAPS_API_KEY no .env)
PROVEDOR = "serpapi"

# Cada nicho vira uma busca: "<nicho> em <CIDADE>"
NICHOS = [
    "pet shop",
    "banho e tosa",
    "barbearia",
    "hamburgueria",
    "pizzaria",
]

# Centro aproximado de Brusque, para a API priorizar resultados da cidade
LATITUDE = -27.0977
LONGITUDE = -48.9175
RAIO_METROS = 12000

# Máximo de páginas por nicho (cada página tem até 20 resultados; máx. 3 páginas)
PAGINAS_POR_NICHO = 2

# Domínios que contam como "só rede social", e não como site próprio
DOMINIOS_REDE_SOCIAL = [
    "instagram.com",
    "facebook.com",
    "fb.com",
    "linktr.ee",
    "wa.me",
    "whatsapp.com",
    "api.whatsapp.com",
    "ifood.com.br",
    "tiktok.com",
    "linkin.bio",
    "bio.link",
]

# Mensagem de abordagem. Variáveis disponíveis: {nome}, {nicho}
MENSAGEM = (
    "Oi, tudo bem? Aqui é o Lucas, sou de Brusque e trabalho com sites para "
    "negócios locais. Vi que a {nome} tem ótimas avaliações no Google, mas "
    "ainda não tem um site próprio. Montei uma prévia de como poderia ficar, "
    "posso te mandar o link para dar uma olhada? Sem compromisso."
)

# Mensagens padrão da aba "Sites prontos" (3, mandadas em sequência), usadas
# quando a empresa ainda não tem mensagens próprias. Variáveis: {nome}, {nicho}, {link}
# As mensagens de cada empresa aparecem (e podem ser editadas) nas colunas
# Mensagem 1, 2 e 3 da planilha. Sem quebra de linha dentro delas: assim
# copiar a célula não traz aspas junto.
MENSAGEM_SITE_PRONTO = (
    "Boa tarde! Tudo bem? Me chamo Lucas Baptista, trabalho com criação de sites "
    "para empresas aqui de Brusque.",
    "Preparei um site para a {nome}. Ele já está pronto, dá uma olhada: {link}",
    "Se gostarem, eu cuido de tudo para colocar no ar: endereço próprio (.com.br), "
    "hospedagem e as atualizações sempre que precisarem. Também ajusto qualquer "
    "detalhe que quiserem mudar. Sobre o valor, a gente conversa e combina algo "
    "que faça sentido para vocês.",
)

PASTA_DADOS = "dados"
ARQUIVO_BANCO = "dados/prospects.db"
ARQUIVO_PLANILHA = "dados/prospects.xlsx"
