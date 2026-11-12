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
    encontrado_em   TEXT,
    atualizado_em   TEXT
);
"""


def conectar(caminho):
    con = sqlite3.connect(caminho)
    con.row_factory = sqlite3.Row
    con.execute(ESQUEMA)
    return con


def salvar(con, empresa):
    """Insere uma empresa nova ou atualiza os dados públicos de uma existente.

    status e observacoes NUNCA são sobrescritos, para não perder o seu controle.
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
    """Recebe [(place_id, status, observacoes)] vindos da planilha."""
    alterados = 0
    for place_id, status, obs in linhas:
        if not place_id:
            continue
        status = (status or "novo").strip().lower()
        if status not in STATUS_VALIDOS:
            continue
        cur = con.execute(
            "UPDATE empresas SET status = ?, observacoes = ? "
            "WHERE place_id = ? AND (status != ? OR observacoes != ?)",
            (status, obs or "", place_id, status, obs or ""),
        )
        alterados += cur.rowcount
    return alterados
