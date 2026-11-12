"""Classifica a presença online e extrai o bairro do endereço."""

from urllib.parse import urlparse

SEM_SITE = "sem site"
SO_REDE_SOCIAL = "só rede social"
TEM_SITE = "tem site"


def classificar_site(url, dominios_rede_social):
    if not url:
        return SEM_SITE
    host = urlparse(url if "://" in url else f"https://{url}").netloc.lower()
    host = host.removeprefix("www.").removeprefix("m.")
    if any(host == d or host.endswith("." + d) for d in dominios_rede_social):
        return SO_REDE_SOCIAL
    return TEM_SITE


def extrair_bairro(endereco):
    """'R. Azambuja, 100 - Centro, Brusque - SC, 88350-000, Brasil' -> 'Centro'"""
    for parte in endereco.split(","):
        if " - " in parte:
            esquerda, direita = parte.split(" - ", 1)
            # "100 - Centro" -> bairro é a direita; "Brusque - SC" -> não é bairro
            if len(direita.strip()) == 2 and direita.strip().isupper():
                continue
            return direita.strip()
    return ""


def eh_celular(telefone_intl):
    """Celular brasileiro: +55, DDD (2 dígitos) e 9 dígitos começando com 9."""
    digitos = "".join(c for c in telefone_intl if c.isdigit())
    if digitos.startswith("55"):
        digitos = digitos[2:]
    return len(digitos) == 11 and digitos[2] == "9"
