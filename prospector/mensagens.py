"""Gera a mensagem de abordagem e o link do WhatsApp (wa.me) com o texto pronto.

Nada é enviado automaticamente: o link só abre o WhatsApp com a mensagem
escrita, e você revisa e envia se quiser.
"""

from urllib.parse import quote


def gerar_texto(modelo, empresa):
    return modelo.format(
        nome=empresa["nome"], nicho=empresa["nicho"], link=empresa.get("link_previa") or ""
    )


def gerar_link(telefone_intl, texto):
    digitos = "".join(c for c in (telefone_intl or "") if c.isdigit())
    if not digitos:
        return ""
    if not digitos.startswith("55"):
        digitos = "55" + digitos
    if not texto:
        return f"https://wa.me/{digitos}"
    return f"https://wa.me/{digitos}?text={quote(texto)}"
