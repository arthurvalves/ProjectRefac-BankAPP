
import requests
from datetime import datetime, timedelta

def get_cambio(moeda_destino):
    if moeda_destino not in ["USD", "EUR", "JPY", "EUR"]:
        print("Moeda inválida.")
        return None

    # Data de ontem (último dia útil)
    ontem = datetime.now() - timedelta(days=1)
    data_formatada = ontem.strftime("%m-%d-%Y")

    url_map = {
        "USD": f"https://olinda.bcb.gov.br/olinda/servico/PTAX/versao/v1/odata/CotacaoDolarDia(dataCotacao=@dataCotacao)?@dataCotacao='{data_formatada}'&$top=1&$orderby=cotacaoCompra desc&$format=json",
        "EUR": f"https://olinda.bcb.gov.br/olinda/servico/PTAX/versao/v1/odata/CotacaoEuroDia(dataCotacao=@dataCotacao)?@dataCotacao='{data_formatada}'&$top=1&$orderby=cotacaoCompra desc&$format=json",
        "JPY": f"https://olinda.bcb.gov.br/olinda/servico/PTAX/versao/v1/odata/CotacaoJPYDia(dataCotacao=@dataCotacao)?@dataCotacao='{data_formatada}'&$top=1&$orderby=cotacaoCompra desc&$format=json"
    }

    try:
        resposta = requests.get(url_map[moeda_destino], timeout=5)
        resposta.raise_for_status()
        dados = resposta.json()

        if "value" in dados and dados["value"]:
            return dados["value"][0]["cotacaoCompra"]
        else:
            print("Não foi possível obter a cotação.")
            return None
    except Exception as e:
        print(f"[Erro ao obter cotação]: {e}")
        return None
