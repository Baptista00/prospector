"""Armazena as empresas no SQLite, sem duplicar e sem apagar o seu status."""

import sqlite3
from datetime import date

STATUS_VALIDOS = ["novo", "contatado", "respondeu", "reunião", "fechado", "recusou"]

ESQUEMA = """
CREATE TABLE IF NOT EXISTS empresas (
    place_id        TEXT PRIMARY KEY,
    nome            TEXT NOT NULL,
    nicho           TEXT,
    bairro          TEXT,
    endereco        TEXT,
    telefone        TEXT,
    telefone_intl   TEXT,
    tem_celular     INTEGER,
    nota            REAL,
    avaliacoes      INTEGER,
    site            TEXT,
    situacao_site   TEXT,
    maps            TEXT,
    pontos          INTEGER,
    prioridade      TEXT,
    status          TEXT DEFAULT 'novo',
    observacoes     TEXT DEFAULT '',
    link_previa     TEXT DEFAULT '',
    mensagem        TEXT DEFAULT '',
    encontrado_em   TEXT,
    atualizado_em   TEXT
);
"""


def conectar(caminho):
    con = sqlite3.connect(caminho)
    con.row_factory = sqlite3.Row
    con.execute(ESQUEMA)
    # Migração: bancos criados antes das colunas link_previa e mensagem
    colunas = {linha["name"] for linha in con.execute("PRAGMA table_info(empresas)")}
    for coluna in ("link_previa", "mensagem"):
        if coluna not in colunas:
            con.execute(f"ALTER TABLE empresas ADD COLUMN {coluna} TEXT DEFAULT ''")
            con.commit()
    return con


def salvar(con, empresa):
    """Insere uma empresa nova ou atualiza os dados públicos de uma existente.

    status, observacoes, link_previa e mensagem NUNCA são sobrescritos, para não perder o seu controle.
    Retorna True se a empresa é nova.
    """
    hoje = date.today().isoformat()
    existe = con.execute(
        "SELECT 1 FROM empresas WHERE place_id = ?", (empresa["place_id"],)
    ).fetchone()

    campos = [
        "nome", "nicho", "bairro", "endereco", "telefone", "telefone_intl",
        "tem_celular", "nota", "avaliacoes", "site", "situacao_site", "maps",
        "pontos", "prioridade",
    ]
    valores = [empresa.get(c) for c in campos]

    if existe:
        sets = ", ".join(f"{c} = ?" for c in campos)
        con.execute(
            f"UPDATE empresas SET {sets}, atualizado_em = ? WHERE place_id = ?",
            valores + [hoje, empresa["place_id"]],
        )
        return False

    colunas = ", ".join(["place_id"] + campos + ["encontrado_em", "atualizado_em"])
    marcas = ", ".join("?" * (len(campos) + 3))
    con.execute(
        f"INSERT INTO empresas ({colunas}) VALUES ({marcas})",
        [empresa["place_id"]] + valores + [hoje, hoje],
    )
    return True


def listar(con):
    return con.execute(
        "SELECT * FROM empresas ORDER BY pontos DESC, avaliacoes DESC"
    ).fetchall()


def importar_status(con, linhas):
    """Recebe [(place_id, status, observacoes, link_previa, mensagem)] vindos da planilha.

    mensagem = None quer dizer que a aba não tem essa coluna: o valor do banco fica como está.
    """
    alterados = 0
    for place_id, status, obs, link, mensagem in linhas:
        if not place_id:
            continue
        atual = con.execute(
            "SELECT status, IFNULL(mensagem, '') AS mensagem FROM empresas WHERE place_id = ?",
            (place_id,),
        ).fetchone()
        if not atual:
            continue
        obs, link = str(obs or "").strip(), str(link or "").strip()
        mensagem = atual["mensagem"] if mensagem is None else str(mensagem).strip()
        status = str(status or "novo").strip().lower()
        if status not in STATUS_VALIDOS:
            # Texto fora da lista: mantém o status do banco e guarda o texto
            # nas observações, para nada do que você escreveu se perder.
            if status and status not in obs.lower():
                obs = f"{obs} ({status})".strip() if obs else status
            status = atual["status"]
        cur = con.execute(
            "UPDATE empresas SET status = ?, observacoes = ?, link_previa = ?, mensagem = ? "
            "WHERE place_id = ? AND (status != ? OR IFNULL(observacoes, '') != ? "
            "OR IFNULL(link_previa, '') != ? OR IFNULL(mensagem, '') != ?)",
            (status, obs, link, mensagem, place_id, status, obs, link, mensagem),
        )
        alterados += cur.rowcount
    return alterados
