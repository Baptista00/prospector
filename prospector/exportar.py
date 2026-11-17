"""Gera a planilha .xlsx e lê de volta o que você preencher nela.

A planilha tem quatro abas, e cada empresa aparece em só uma delas:

    Sites prontos       empresas com o link do site preenchido (a fila de abordagem)
    Em desenvolvimento  empresas com status "em desenvolvimento" (site sendo feito)
    Prospects           empresas encontradas que ainda não entraram no funil
    Recusaram           empresas com status "recusou"

Para mudar uma empresa de aba, edite a planilha e rode de novo: o status
"em desenvolvimento" leva para "Em desenvolvimento", preencher o link do
site leva para "Sites prontos" e o status "recusou" leva para "Recusaram".
"""

import math

from openpyxl import Workbook, load_workbook
from openpyxl.formatting.rule import CellIsRule
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.worksheet.datavalidation import DataValidation

from .banco import COLUNAS_MENSAGEM, STATUS_VALIDOS

ABA_PROSPECTS, ABA_PRONTOS, ABA_RECUSARAM = "Prospects", "Sites prontos", "Recusaram"
ABA_DEV = "Em desenvolvimento"
ORDEM_ABAS = (ABA_PRONTOS, ABA_DEV, ABA_PROSPECTS, ABA_RECUSARAM)

COLUNAS = {
    # aba: [(cabeçalho, largura)]
    ABA_PROSPECTS: [
        ("Prioridade", 11), ("Pontos", 8), ("Nome", 32), ("Nicho", 14), ("Bairro", 16),
        ("Telefone", 16), ("Nota", 7), ("Avaliações", 11), ("Situação do site", 16),
        ("Status", 12), ("Observações", 30), ("Link da prévia", 34), ("WhatsApp", 12),
        ("Google Maps", 12), ("Site/rede", 28), ("ID", 10),
    ],
    ABA_PRONTOS: [
        ("Nome", 28), ("Nicho", 13), ("Telefone", 16), ("Nota", 7), ("Avaliações", 11),
        ("Status", 12), ("Observações", 28), ("Link do site", 30),
        ("Mensagem 1", 34), ("Enviar 1ª", 10), ("Mensagem 2", 46), ("Enviar 2ª", 10),
        ("Mensagem 3", 52), ("Enviar 3ª", 10), ("Google Maps", 13), ("ID", 10),
    ],
    ABA_DEV: [
        ("Nome", 30), ("Nicho", 14), ("Bairro", 16), ("Telefone", 16), ("Nota", 7),
        ("Avaliações", 11), ("Status", 18), ("Observações", 34), ("Link do site", 40),
        ("Site/rede", 34), ("Google Maps", 13), ("ID", 10),
    ],
    ABA_RECUSARAM: [
        ("Nome", 30), ("Nicho", 14), ("Telefone", 16), ("Status", 12),
        ("Observações", 44), ("Link do site", 56), ("WhatsApp", 12), ("Google Maps", 13),
        ("ID", 10),
    ],
}

COR_CABECALHO = {ABA_PROSPECTS: "1F3A5F", ABA_PRONTOS: "2E6B3A", ABA_DEV: "B5651D",
                 ABA_RECUSARAM: "7A7A7A"}
CORES_PRIORIDADE = {"Alta": "C6EFCE", "Média": "FFEB9C", "Baixa": "F2F2F2"}
TEXTO_WHATSAPP = {ABA_PROSPECTS: "Abrir", ABA_RECUSARAM: "Abrir"}
# Colunas das mensagens na aba Sites prontos: (mensagem, link de envio, coluna no banco)
MENSAGENS = [(f"Mensagem {i}", f"Enviar {i}ª", c) for i, c in enumerate(COLUNAS_MENSAGEM, start=1)]
AVISO_VAZIO = {
    ABA_PRONTOS: "Quando o site de uma empresa ficar pronto, cole o endereço em "
                 "\"Link da prévia\" na aba Prospects e rode: python main.py --sem-busca",
    ABA_DEV: "Quando começar o site de uma empresa, mude o Status dela para "
             "\"em desenvolvimento\" na aba Prospects e rode: python main.py --sem-busca",
    ABA_RECUSARAM: "Quando uma empresa recusar, mude o Status dela para \"recusou\" "
                   "e rode: python main.py --sem-busca",
}

# Cabeçalhos aceitos na leitura (planilhas antigas usam "Link da prévia" em tudo
# e uma coluna "Mensagem" só, que vale como a mensagem 1)
CABECALHOS_LINK = ("Link do site", "Link da prévia")
CABECALHOS_MENSAGEM = [("Mensagem 1", "Mensagem"), ("Mensagem 2",), ("Mensagem 3",)]


def aba_de(empresa):
    """Em qual aba a empresa fica."""
    if (empresa.get("status") or "").strip().lower() == "recusou":
        return ABA_RECUSARAM
    if (empresa.get("link_previa") or "").strip():
        return ABA_PRONTOS
    if (empresa.get("status") or "").strip().lower() == "em desenvolvimento":
        return ABA_DEV
    return ABA_PROSPECTS


def _cabecalho(ws, aba):
    for i, (titulo, largura) in enumerate(COLUNAS[aba], start=1):
        c = ws.cell(row=1, column=i, value=titulo)
        c.font = Font(bold=True, color="FFFFFF")
        c.fill = PatternFill("solid", fgColor=COR_CABECALHO[aba])
        c.alignment = Alignment(vertical="center")
        ws.column_dimensions[c.column_letter].width = largura
    ws.row_dimensions[1].height = 22
    ws.sheet_properties.tabColor = COR_CABECALHO[aba]


def _linhas_de_texto(texto, largura_coluna):
    """Estimativa de quantas linhas o texto ocupa numa célula com quebra de linha."""
    por_linha = max(int(largura_coluna * 1.1), 10)
    return sum(max(1, math.ceil(len(par) / por_linha)) for par in str(texto).split("\n"))


def _aba(wb, aba, empresas, links_whatsapp, primeira=False):
    ws = wb.active if primeira else wb.create_sheet()
    ws.title = aba
    _cabecalho(ws, aba)
    colunas = COLUNAS[aba]
    col = {titulo: i for i, (titulo, _) in enumerate(colunas, start=1)}
    letra = {t: ws.cell(row=1, column=i).column_letter for t, i in col.items()}
    largura = dict(colunas)
    link_font = Font(color="0563C1", underline="single")
    topo = Alignment(vertical="top", wrap_text=True)

    for linha, e in enumerate(empresas, start=2):
        valores = {
            "Prioridade": e["prioridade"], "Pontos": e["pontos"], "Nome": e["nome"],
            "Nicho": e["nicho"], "Bairro": e["bairro"], "Telefone": e["telefone"],
            "Nota": e["nota"], "Avaliações": e["avaliacoes"],
            "Situação do site": e["situacao_site"], "Status": e["status"],
            "Observações": e["observacoes"], "Site/rede": e["site"], "ID": e["place_id"],
        }
        for titulo_msg, _, coluna in MENSAGENS:
            valores[titulo_msg] = e.get(coluna) or ""
        for titulo, v in valores.items():
            if titulo in col:
                ws.cell(row=linha, column=col[titulo], value=v)

        link = (e.get("link_previa") or "").strip()
        titulo_link = next((t for t in CABECALHOS_LINK if t in col), None)
        if link and titulo_link:
            c = ws.cell(row=linha, column=col[titulo_link], value=link)
            c.hyperlink = link if "://" in link else f"https://{link}"
            c.font = link_font
        wa = links_whatsapp.get(e["place_id"])
        if isinstance(wa, list):
            # Sites prontos: um link por mensagem, cada um abre a conversa com o texto
            for (_, titulo_envio, _), url in zip(MENSAGENS, wa):
                if url:
                    c = ws.cell(row=linha, column=col[titulo_envio], value="Enviar")
                    c.hyperlink, c.font = url, link_font
        elif wa and "WhatsApp" in col:
            c = ws.cell(row=linha, column=col["WhatsApp"], value=TEXTO_WHATSAPP[aba])
            c.hyperlink, c.font = wa, link_font
        if e["maps"]:
            c = ws.cell(row=linha, column=col["Google Maps"], value="Ver no mapa")
            c.hyperlink, c.font = e["maps"], link_font

        cor = CORES_PRIORIDADE.get(e["prioridade"])
        if cor and "Prioridade" in col:
            ws.cell(row=linha, column=col["Prioridade"]).fill = PatternFill("solid", fgColor=cor)

        if aba != ABA_PROSPECTS:
            # Abas curtas: texto no topo da célula e mensagem inteira à vista
            for i in range(1, len(colunas) + 1):
                ws.cell(row=linha, column=i).alignment = topo
            n = max((_linhas_de_texto(valores[t], largura[t]) for t, _, _ in MENSAGENS
                     if t in col and valores[t]), default=0)
            if n:
                ws.row_dimensions[linha].height = min(15 * n + 6, 400)

    ultima = max(len(empresas) + 1, 2)
    if not empresas and aba in AVISO_VAZIO:
        c = ws.cell(row=2, column=1, value=AVISO_VAZIO[aba])
        c.font = Font(italic=True, color="7A7A7A")

    # Lista suspensa de status
    dv = DataValidation(
        type="list", formula1='"' + ",".join(STATUS_VALIDOS) + '"', allow_blank=True
    )
    ws.add_data_validation(dv)
    faixa_status = f"{letra['Status']}2:{letra['Status']}{ultima + 500}"
    dv.add(faixa_status)

    # Cores do status: fechado em verde, conversa andando em amarelo, contatado em azul
    for valor, cor in (("fechado", "C6EFCE"), ("respondeu", "FFEB9C"),
                       ("reunião", "FFEB9C"), ("contatado", "DDEBF7"),
                       ("em desenvolvimento", "FCE4D6")):
        ws.conditional_formatting.add(
            faixa_status,
            CellIsRule(operator="equal", formula=[f'"{valor}"'],
                       fill=PatternFill("solid", fgColor=cor)),
        )

    ws.freeze_panes = "D2" if aba == ABA_PROSPECTS else "B2"
    ws.auto_filter.ref = f"A1:{ws.cell(row=1, column=len(colunas)).column_letter}{ultima}"
    ws.column_dimensions[letra["ID"]].hidden = True  # ID interno, usado para sincronizar
    return ws


def gerar(caminho, empresas, links_whatsapp):
    grupos = {aba: [] for aba in COLUNAS}
    for e in empresas:
        grupos[aba_de(e)].append(e)

    wb = Workbook()
    for i, aba in enumerate(ORDEM_ABAS):
        _aba(wb, aba, grupos[aba], links_whatsapp, primeira=(i == 0))
    wb.active = 0
    wb.save(caminho)
    return {aba: len(lista) for aba, lista in grupos.items()}


def _texto_celula(valor):
    if valor is None:
        return ""
    # O Excel às vezes grava quebra de linha do Windows (\r\n ou _x000D_)
    return str(valor).replace("_x000D_", "").replace("\r\n", "\n").replace("\r", "\n")


def ler_status(caminho):
    """Retorna [(place_id, status, observacoes, link, [msg1, msg2, msg3])] de todas as abas.

    Cada mensagem vem como None quando a aba não tem aquela coluna. Funciona
    também com planilhas antigas, só com a aba Prospects e sem a coluna de link.
    """
    try:
        wb = load_workbook(caminho, read_only=True)
    except FileNotFoundError:
        return []
    linhas = []
    for ws in wb.worksheets:
        primeira = next(ws.iter_rows(min_row=1, max_row=1, values_only=True), None)
        if not primeira:
            continue
        cab = list(primeira)
        if not all(t in cab for t in ("ID", "Status", "Observações")):
            continue
        i_id, i_st, i_obs = cab.index("ID"), cab.index("Status"), cab.index("Observações")
        i_link = next((cab.index(t) for t in CABECALHOS_LINK if t in cab), None)
        i_msgs = [next((cab.index(t) for t in nomes if t in cab), None)
                  for nomes in CABECALHOS_MENSAGEM]
        for row in ws.iter_rows(min_row=2, values_only=True):
            if len(row) <= i_id or not row[i_id]:
                continue
            link = row[i_link] if i_link is not None else ""
            msgs = [_texto_celula(row[i]) if i is not None else None for i in i_msgs]
            linhas.append((row[i_id], row[i_st], row[i_obs], link, msgs))
    wb.close()
    return linhas
