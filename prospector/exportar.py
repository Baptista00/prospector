"""Gera a planilha .xlsx e lê de volta o status que você preencher nela."""

from openpyxl import Workbook, load_workbook
from openpyxl.formatting.rule import CellIsRule
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.worksheet.datavalidation import DataValidation

from .banco import STATUS_VALIDOS

COLUNAS = [
    # (cabeçalho, largura)
    ("Prioridade", 11),
    ("Pontos", 8),
    ("Nome", 32),
    ("Nicho", 14),
    ("Bairro", 16),
    ("Telefone", 16),
    ("Nota", 7),
    ("Avaliações", 11),
    ("Situação do site", 16),
    ("Status", 12),
    ("Observações", 30),
    ("Link da prévia", 34),
    ("WhatsApp", 12),
    ("Google Maps", 12),
    ("Site/rede", 28),
    ("ID", 10),
]

AZUL = "1F3A5F"
CORES_PRIORIDADE = {"Alta": "C6EFCE", "Média": "FFEB9C", "Baixa": "F2F2F2"}


def gerar(caminho, empresas, links_whatsapp):
    wb = Workbook()
    ws = wb.active
    ws.title = "Prospects"

    for i, (titulo, largura) in enumerate(COLUNAS, start=1):
        c = ws.cell(row=1, column=i, value=titulo)
        c.font = Font(bold=True, color="FFFFFF")
        c.fill = PatternFill("solid", fgColor=AZUL)
        c.alignment = Alignment(vertical="center")
        ws.column_dimensions[c.column_letter].width = largura
    ws.row_dimensions[1].height = 22
    ws.freeze_panes = "D2"

    link_font = Font(color="0563C1", underline="single")

    col = {titulo: i for i, (titulo, _) in enumerate(COLUNAS, start=1)}
    letra = {t: ws.cell(row=1, column=i).column_letter for t, i in col.items()}

    for linha, e in enumerate(empresas, start=2):
        valores = {
            "Prioridade": e["prioridade"], "Pontos": e["pontos"], "Nome": e["nome"],
            "Nicho": e["nicho"], "Bairro": e["bairro"], "Telefone": e["telefone"],
            "Nota": e["nota"], "Avaliações": e["avaliacoes"],
            "Situação do site": e["situacao_site"], "Status": e["status"],
            "Observações": e["observacoes"], "Site/rede": e["site"], "ID": e["place_id"],
        }
        for titulo, v in valores.items():
            ws.cell(row=linha, column=col[titulo], value=v)

        previa = (e.get("link_previa") or "").strip()
        if previa:
            c = ws.cell(row=linha, column=col["Link da prévia"], value=previa)
            c.hyperlink = previa if "://" in previa else f"https://{previa}"
            c.font = link_font
        wa = links_whatsapp.get(e["place_id"])
        if wa:
            c = ws.cell(row=linha, column=col["WhatsApp"], value="Abrir")
            c.hyperlink, c.font = wa, link_font
        if e["maps"]:
            c = ws.cell(row=linha, column=col["Google Maps"], value="Ver no mapa")
            c.hyperlink, c.font = e["maps"], link_font

        cor = CORES_PRIORIDADE.get(e["prioridade"])
        if cor:
            ws.cell(row=linha, column=col["Prioridade"]).fill = PatternFill("solid", fgColor=cor)

    ultima = max(len(empresas) + 1, 2)

    # Lista suspensa de status
    dv = DataValidation(
        type="list", formula1='"' + ",".join(STATUS_VALIDOS) + '"', allow_blank=True
    )
    ws.add_data_validation(dv)
    dv.add(f"{letra['Status']}2:{letra['Status']}{ultima + 500}")

    # Destaque de status fechado
    ws.conditional_formatting.add(
        f"{letra['Status']}2:{letra['Status']}{ultima + 500}",
        CellIsRule(operator="equal", formula=['"fechado"'],
                   fill=PatternFill("solid", fgColor="C6EFCE")),
    )

    ws.auto_filter.ref = f"A1:{ws.cell(row=1, column=len(COLUNAS)).column_letter}{ultima}"
    ws.column_dimensions[letra["ID"]].hidden = True  # ID interno, usado para sincronizar

    wb.save(caminho)


def ler_status(caminho):
    """Retorna [(place_id, status, observacoes, link_previa)] da planilha, se ela existir.

    Funciona também com planilhas antigas, sem a coluna "Link da prévia".
    """
    try:
        wb = load_workbook(caminho, read_only=True)
    except FileNotFoundError:
        return []
    ws = wb["Prospects"]
    cab = [c.value for c in next(ws.iter_rows(min_row=1, max_row=1))]
    i_id, i_st, i_obs = cab.index("ID"), cab.index("Status"), cab.index("Observações")
    i_link = cab.index("Link da prévia") if "Link da prévia" in cab else None
    linhas = []
    for row in ws.iter_rows(min_row=2, values_only=True):
        if row[i_id]:
            link = row[i_link] if i_link is not None else ""
            linhas.append((row[i_id], row[i_st], row[i_obs], link))
    wb.close()
    return linhas
