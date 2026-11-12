"""Calcula a prioridade (0 a 100) de cada empresa como cliente em potencial.

Ideia: o cliente ideal é um negócio ATIVO (tem avaliações), BEM AVALIADO
(o dono se importa com a imagem), PEQUENO (não é rede grande) e SEM SITE.
"""

from .filtro import SEM_SITE, SO_REDE_SOCIAL, TEM_SITE


def calcular(empresa):
    if empresa["situacao_site"] == TEM_SITE:
        return 0
    if empresa.get("situacao_negocio") not in ("", None, "OPERATIONAL"):
        return 0  # fechado temporária ou permanentemente

    pontos = 0

    # Presença online: quem só tem Instagram já entende o valor de estar online
    if empresa["situacao_site"] == SO_REDE_SOCIAL:
        pontos += 30
    elif empresa["situacao_site"] == SEM_SITE:
        pontos += 25

    # Atividade: número de avaliações (o ponto ideal é entre 20 e 300)
    n = empresa.get("avaliacoes") or 0
    if n >= 20 and n <= 300:
        pontos += 30
    elif n >= 5:
        pontos += 15
    elif n > 300:
        pontos += 10  # provavelmente maior, ou já bem estabelecido

    # Qualidade: nota no Google
    nota = empresa.get("nota") or 0
    if nota >= 4.5:
        pontos += 25
    elif nota >= 4.0:
        pontos += 15
    elif nota > 0:
        pontos += 5

    # Contato: celular permite WhatsApp direto
    if empresa.get("tem_celular"):
        pontos += 15

    return min(pontos, 100)


def rotulo(pontos):
    if pontos >= 75:
        return "Alta"
    if pontos >= 50:
        return "Média"
    if pontos > 0:
        return "Baixa"
    return "Descartar"
