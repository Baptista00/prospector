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

# Mensagem padrão da aba "Sites prontos", usada quando a empresa ainda não tem
# mensagem própria. Variáveis: {nome}, {nicho}, {link}
# A mensagem de cada empresa aparece (e pode ser editada) na coluna Mensagem da planilha.
MENSAGEM_SITE_PRONTO = (
    "Oi, tudo bem? Aqui é o Lucas, sou de Brusque e faço sites para negócios da cidade.\n\n"
    "Montei um site para a {nome}: {link}\n\n"
    "Ele já está pronto. Se vocês gostarem, eu coloco no ar com o endereço de vocês "
    "e cuido das atualizações. Dá uma olhada e me diz o que achou?"
)

PASTA_DADOS = "dados"
ARQUIVO_BANCO = "dados/prospects.db"
ARQUIVO_PLANILHA = "dados/prospects.xlsx"
