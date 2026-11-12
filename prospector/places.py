"""Busca de empresas na API do Google Places (Text Search, versão nova)."""

import time

import requests

URL = "https://places.googleapis.com/v1/places:searchText"

# Só pedimos os campos que usamos: isso define o custo de cada chamada
CAMPOS = ",".join(
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


class ErroAPI(Exception):
    pass


def buscar(nicho, cidade, chave, lat, lng, raio, paginas=2):
    """Retorna uma lista de dicts com os dados brutos de cada empresa."""
    cabecalhos = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": chave,
        "X-Goog-FieldMask": CAMPOS,
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
        resp = requests.post(URL, headers=cabecalhos, json=corpo, timeout=30)
        if resp.status_code != 200:
            raise ErroAPI(f"{resp.status_code}: {resp.text[:300]}")
        dados = resp.json()
        resultados.extend(dados.get("places", []))

        token = dados.get("nextPageToken")
        if not token:
            break
        corpo["pageToken"] = token
        time.sleep(2)  # o token da próxima página demora um pouco a valer

    return [_normalizar(p, nicho) for p in resultados]


def _normalizar(p, nicho):
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
