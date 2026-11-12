"""Busca de empresas. Dois provedores, mesma saída:

- "serpapi": SerpApi (motor google_maps). Plano gratuito sem cartão, 250 buscas/mês.
- "google":  Google Places API (New). Exige conta de faturamento no Google Cloud.
"""

import time

import requests


class ErroAPI(Exception):
    pass


def buscar(provedor, nicho, cidade, chave, lat, lng, raio, paginas=2):
    if provedor == "serpapi":
        return _buscar_serpapi(nicho, cidade, chave, lat, lng, paginas)
    if provedor == "google":
        return _buscar_google(nicho, cidade, chave, lat, lng, raio, paginas)
    raise ErroAPI(f"Provedor desconhecido: {provedor}")


# ---------------------------------------------------------------- SerpApi

URL_SERPAPI = "https://serpapi.com/search.json"


def _buscar_serpapi(nicho, cidade, chave, lat, lng, paginas):
    resultados = []
    for pagina in range(paginas):
        params = {
            "engine": "google_maps",
            "type": "search",
            "q": f"{nicho} em {cidade}",
            "ll": f"@{lat},{lng},13z",
            "hl": "pt-br",
            "gl": "br",
            "start": pagina * 20,
            "api_key": chave,
        }
        resp = requests.get(URL_SERPAPI, params=params, timeout=60)
        dados = resp.json() if resp.headers.get("content-type", "").startswith("application/json") else {}

        if resp.status_code != 200 or "error" in dados:
            erro = dados.get("error", resp.text[:300])
            if "hasn't returned any results" in erro:
                break  # acabaram os resultados
            raise ErroAPI(f"{resp.status_code}: {erro}")

        locais = dados.get("local_results")
        if locais is None and dados.get("place_results"):
            locais = [dados["place_results"]]  # a busca caiu direto em um único lugar
        locais = locais or []
        resultados.extend(locais)

        if len(locais) < 20 or not dados.get("serpapi_pagination", {}).get("next"):
            break

    return [_normalizar_serpapi(p, nicho) for p in resultados]


def _normalizar_serpapi(p, nicho):
    telefone = p.get("phone", "") or ""
    digitos = "".join(c for c in telefone if c.isdigit())
    if digitos and not digitos.startswith("55") and len(digitos) in (10, 11):
        digitos = "55" + digitos
    estado = (p.get("open_state") or "").lower()
    fechado = "permanente" in estado or "permanently" in estado
    place_id = p.get("place_id", "")
    return {
        "place_id": place_id,
        "nome": p.get("title", ""),
        "nicho": nicho,
        "endereco": p.get("address", ""),
        "telefone": telefone,
        "telefone_intl": f"+{digitos}" if digitos else "",
        "nota": p.get("rating"),
        "avaliacoes": p.get("reviews") or 0,
        "site": p.get("website", ""),
        "maps": f"https://www.google.com/maps/place/?q=place_id:{place_id}" if place_id else "",
        "situacao_negocio": "CLOSED_PERMANENTLY" if fechado else "OPERATIONAL",
    }


# ---------------------------------------------------------------- Google Places (New)

URL_GOOGLE = "https://places.googleapis.com/v1/places:searchText"

# Só pedimos os campos que usamos: isso define o custo de cada chamada
CAMPOS_GOOGLE = ",".join(
    [
        "places.id",
        "places.displayName",
        "places.formattedAddress",
        "places.nationalPhoneNumber",
        "places.internationalPhoneNumber",
        "places.rating",
        "places.userRatingCount",
        "places.websiteUri",
        "places.googleMapsUri",
        "places.businessStatus",
        "nextPageToken",
    ]
)


def _buscar_google(nicho, cidade, chave, lat, lng, raio, paginas):
    cabecalhos = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": chave,
        "X-Goog-FieldMask": CAMPOS_GOOGLE,
    }
    corpo = {
        "textQuery": f"{nicho} em {cidade}",
        "languageCode": "pt-BR",
        "regionCode": "BR",
        "locationBias": {
            "circle": {"center": {"latitude": lat, "longitude": lng}, "radius": raio}
        },
    }

    resultados = []
    for _ in range(paginas):
        resp = requests.post(URL_GOOGLE, headers=cabecalhos, json=corpo, timeout=30)
        if resp.status_code != 200:
            raise ErroAPI(f"{resp.status_code}: {resp.text[:300]}")
        dados = resp.json()
        resultados.extend(dados.get("places", []))

        token = dados.get("nextPageToken")
        if not token:
            break
        corpo["pageToken"] = token
        time.sleep(2)  # o token da próxima página demora um pouco a valer

    return [_normalizar_google(p, nicho) for p in resultados]


def _normalizar_google(p, nicho):
    return {
        "place_id": p.get("id"),
        "nome": (p.get("displayName") or {}).get("text", ""),
        "nicho": nicho,
        "endereco": p.get("formattedAddress", ""),
        "telefone": p.get("nationalPhoneNumber", ""),
        "telefone_intl": p.get("internationalPhoneNumber", ""),
        "nota": p.get("rating"),
        "avaliacoes": p.get("userRatingCount") or 0,
        "site": p.get("websiteUri", ""),
        "maps": p.get("googleMapsUri", ""),
        "situacao_negocio": p.get("businessStatus", ""),
    }
