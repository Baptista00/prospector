"""Prospector: encontra negócios de Brusque sem site e monta a lista de abordagem.

Uso:
    python main.py            busca de verdade (precisa da chave no .env)
    python main.py --demo     testa com dados fictícios, sem chave
    python main.py --nicho "barbearia"   busca só um nicho
    python main.py --sem-busca           só regera a planilha (não gasta buscas da API)
"""

import argparse
import os
import sys

from dotenv import load_dotenv

import config
from prospector import banco, demo, exportar, filtro, mensagens, places, pontuacao


def processar(bruto):
    e = dict(bruto)
    e["situacao_site"] = filtro.classificar_site(e["site"], config.DOMINIOS_REDE_SOCIAL)
    e["bairro"] = filtro.extrair_bairro(e["endereco"])
    e["tem_celular"] = 1 if filtro.eh_celular(e["telefone_intl"]) else 0
    e["pontos"] = pontuacao.calcular(e)
    e["prioridade"] = pontuacao.rotulo(e["pontos"])
    return e


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

    ap = argparse.ArgumentParser(description="Prospector de clientes para landing pages")
    ap.add_argument("--demo", action="store_true", help="usa dados fictícios, sem API")
    ap.add_argument("--nicho", help="busca só este nicho (ex.: 'pet shop')")
    ap.add_argument("--sem-busca", action="store_true",
                    help="não chama a API: só sincroniza a planilha com o banco e regera")
    args = ap.parse_args()

    load_dotenv()
    variavel = {"serpapi": "SERPAPI_KEY", "google": "GOOGLE_MAPS_API_KEY"}.get(config.PROVEDOR)
    if not variavel:
        print(f"PROVEDOR inválido no config.py: {config.PROVEDOR!r} (use 'serpapi' ou 'google').")
        sys.exit(1)
    chave = os.getenv(variavel, "").strip()
    if not args.demo and not args.sem_busca and not chave:
        print(f"Falta a chave da API. Copie .env.example para .env e preencha "
              f"{variavel}, ou rode com --demo para testar.")
        sys.exit(1)

    os.makedirs(config.PASTA_DADOS, exist_ok=True)
    if args.demo:  # o teste fica numa subpasta, para não misturar com a planilha real
        os.makedirs(os.path.join(config.PASTA_DADOS, "demo"), exist_ok=True)
        arquivo_banco = os.path.join(config.PASTA_DADOS, "demo", "prospects_demo.db")
        arquivo_planilha = os.path.join(config.PASTA_DADOS, "demo", "prospects_demo.xlsx")
    else:
        arquivo_banco, arquivo_planilha = config.ARQUIVO_BANCO, config.ARQUIVO_PLANILHA

    con = banco.conectar(arquivo_banco)

    # 1. Puxa para o banco o status/observações que você editou na planilha
    alterados = banco.importar_status(con, exportar.ler_status(arquivo_planilha))
    con.commit()
    if alterados:
        print(f"Status atualizado a partir da planilha: {alterados} empresa(s).")

    # 2. Busca
    nichos = [] if args.sem_busca else ([args.nicho] if args.nicho else config.NICHOS)
    novas = total = 0
    for nicho in nichos:
        print(f"Buscando: {nicho}...", end=" ", flush=True)
        try:
            if args.demo:
                brutos = demo.empresas_exemplo(nicho)
            else:
                brutos = places.buscar(
                    config.PROVEDOR, nicho, config.CIDADE, chave, config.LATITUDE, config.LONGITUDE,
                    config.RAIO_METROS, config.PAGINAS_POR_NICHO,
                )
        except places.ErroAPI as erro:
            print(f"erro na API -> {erro}")
            continue

        n_novas = 0
        for bruto in brutos:
            if not bruto["place_id"] or not bruto["nome"]:
                continue
            e = processar(bruto)
            # Se a mesma empresa aparece em dois nichos, mantém o primeiro
            existente = con.execute(
                "SELECT nicho FROM empresas WHERE place_id = ?", (e["place_id"],)
            ).fetchone()
            if existente:
                e["nicho"] = existente["nicho"]
            if banco.salvar(con, e):
                n_novas += 1
        con.commit()
        novas += n_novas
        total += len(brutos)
        print(f"{len(brutos)} encontradas, {n_novas} novas")

    # 3. Monta links do WhatsApp e exporta a planilha
    empresas = [dict(r) for r in banco.listar(con)]
    links = {}
    for e in empresas:
        if not e["tem_celular"]:
            continue
        aba = exportar.aba_de(e)
        if aba == exportar.ABA_PRONTOS:
            # Mensagem própria da empresa; sem ela, usa o modelo de site pronto do config.py
            if not (e["mensagem"] or "").strip():
                e["mensagem"] = mensagens.gerar_texto(config.MENSAGEM_SITE_PRONTO, e)
            links[e["place_id"]] = mensagens.gerar_link(e["telefone_intl"], e["mensagem"])
        elif aba == exportar.ABA_RECUSARAM:
            links[e["place_id"]] = mensagens.gerar_link(e["telefone_intl"], "")
        elif e["pontos"] > 0:
            texto = mensagens.gerar_texto(config.MENSAGEM, e)
            links[e["place_id"]] = mensagens.gerar_link(e["telefone_intl"], texto)

    try:
        por_aba = exportar.gerar(arquivo_planilha, empresas, links)
    except PermissionError:
        print(f"\nNão consegui salvar {arquivo_planilha}: feche a planilha no Excel e rode de novo.")
        sys.exit(1)

    alvos = [e for e in empresas if e["pontos"] > 0]
    alta = sum(1 for e in alvos if e["prioridade"] == "Alta")
    print(
        f"\nPronto. {total} resultados, {novas} empresas novas."
        f"\nNo banco: {len(empresas)} empresas, {len(alvos)} sem site próprio "
        f"({alta} de prioridade alta)."
        f"\nSites prontos: {por_aba[exportar.ABA_PRONTOS]} | "
        f"Recusaram: {por_aba[exportar.ABA_RECUSARAM]}"
        f"\nPlanilha: {arquivo_planilha}"
    )


if __name__ == "__main__":
    main()
