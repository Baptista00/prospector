"""Dados fictícios para testar o fluxo sem chave da API (python main.py --demo)."""


def empresas_exemplo(nicho):
    base = [
        # nome, nota, avaliações, site, celular?
        ("Exemplo Banho & Tosa", 4.8, 87, "", True),
        ("Exemplo Pet Center", 4.6, 142, "https://instagram.com/exemplo", True),
        ("Exemplo Rede Nacional", 4.3, 1250, "https://www.exemplo-rede.com.br", False),
        ("Exemplo Cantinho Animal", 4.1, 9, "", False),
        ("Exemplo Bichos & Cia", 3.6, 31, "", True),
    ]
    saida = []
    for i, (nome, nota, n, site, cel) in enumerate(base):
        tel_intl = "+55 47 99999-00%02d" % i if cel else "+55 47 3355-00%02d" % i
        saida.append(
            {
                "place_id": f"demo-{nicho}-{i}",
                "nome": f"{nome} ({nicho})",
                "nicho": nicho,
                "endereco": f"Rua Exemplo, {100 + i} - Centro, Brusque - SC, 88350-000, Brasil",
                "telefone": tel_intl.replace("+55 ", "(").replace(" ", ") ", 1),
                "telefone_intl": tel_intl,
                "nota": nota,
                "avaliacoes": n,
                "site": site,
                "maps": "https://maps.google.com/?q=Brusque",
                "situacao_negocio": "OPERATIONAL",
            }
        )
    return saida
