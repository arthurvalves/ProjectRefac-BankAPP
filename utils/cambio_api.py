
import requests
from datetime import datetime, timedelta

def get_cambio(moeda_destino):
    moedas_suportadas = ["USD", "EUR", "JPY"]
    if moeda_destino not in moedas_suportadas:
        print("Moeda inválida.")
        return None

    formato_data_bcb = "%m-%d-%Y"

    for dias_atras in range(1, 8):
        data = datetime.now() - timedelta(days=dias_atras)

        if data.weekday() >= 5:
            continue

        data_formatada = data.strftime(formato_data_bcb)
        url = f"https://olinda.bcb.gov.br/olinda/servico/PTAX/versao/v1/odata/CotacaoMoedaDia(moeda=@moeda,dataCotacao=@dataCotacao)?@moeda='{moeda_destino}'&@dataCotacao='{data_formatada}'&$top=1&$format=json&$select=cotacaoCompra"

        try:
            resposta = requests.get(url, timeout=5)
            resposta.raise_for_status()  
            dados = resposta.json()
            if dados.get("value"):
                return dados["value"][0]["cotacaoCompra"]
        except requests.exceptions.RequestException as e:
            print(f"Erro ao contatar a API do BCB: {e}")
            break

    print("Moeda inválida ou erro ao obter taxa de câmbio.")
    return None
