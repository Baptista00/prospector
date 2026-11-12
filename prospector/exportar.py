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

    for linha, e in enumerate(empresas, start=2):
        valores = [
            e["prioridade"], e["pontos"], e["nome"], e["nicho"], e["bairro"],
            e["telefone"], e["nota"], e["avaliacoes"], e["situacao_site"],
            e["status"], e["observacoes"], None, None, e["site"], e["place_id"],
        ]
        for col, v in enumerate(valores, start=1):
            ws.cell(row=linha, column=col, value=v)

        wa = links_whatsapp.get(e["place_id"])
        if wa:
            c = ws.cell(row=linha, column=12, value="Abrir")
            c.hyperlink, c.font = wa, link_font
        if e["maps"]:
            c = ws.cell(row=linha, column=13, value="Ver no mapa")
            c.hyperlink, c.font = e["maps"], link_font

        cor = CORES_PRIORIDADE.get(e["prioridade"])
        if cor:
            ws.cell(row=linha, column=1).fill = PatternFill("solid", fgColor=cor)

    ultima = max(len(empresas) + 1, 2)

    # Lista suspensa de status
    dv = DataValidation(
        type="list", formula1='"' + ",".join(STATUS_VALIDOS) + '"', allow_blank=True
    )
    ws.add_data_validation(dv)
    dv.add(f"J2:J{ultima + 500}")

    # Destaque de status fechado
    ws.conditional_formatting.add(
        f"J2:J{ultima + 500}",
        CellIsRule(operator="equal", formula=['"fechado"'],
                   fill=PatternFill("solid", fgColor="C6EFCE")),
    )

    ws.auto_filter.ref = f"A1:{ws.cell(row=1, column=len(COLUNAS)).column_letter}{ultima}"
    ws.column_dimensions["O"].hidden = True  # ID interno, usado para sincronizar

    wb.save(caminho)


def ler_status(caminho):
    """Retorna [(place_id, status, observacoes)] da planilha, se ela existir."""
    try:
        wb = load_workbook(caminho, read_only=True)
    except FileNotFoundError:
        return []
    ws = wb["Prospects"]
    cab = [c.value for c in next(ws.iter_rows(min_row=1, max_row=1))]
    i_id, i_st, i_obs = cab.index("ID"), cab.index("Status"), cab.index("Observações")
    linhas = []
    for row in ws.iter_rows(min_row=2, values_only=True):
        if row[i_id]:
            linhas.append((row[i_id], row[i_st], row[i_obs]))
    wb.close()
    return linhas
