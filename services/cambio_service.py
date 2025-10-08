from utils.cambio_api import get_cambio
from models.transacoes import Transacao

def cambio(conta, moeda_destino, valor_em_reais):
    taxa = get_cambio(moeda_destino)

    if taxa is None:
        print("\nMoeda inválida ou erro ao obter taxa de câmbio.")
        return None

    if conta.saque(valor_em_reais):
        valor_convertido = valor_em_reais / taxa
        descricao = f"Conversão de R${valor_em_reais:.2f} para {valor_convertido:.2f} {moeda_destino} (Taxa: {taxa:.4f})"
        conta.historico.append(Transacao("Câmbio", valor_em_reais, descricao=descricao))

        # Adiciona o valor convertido ao dicionário de saldos estrangeiros
        saldo_anterior = conta.saldos_estrangeiros.get(moeda_destino, 0)
        conta.saldos_estrangeiros[moeda_destino] = saldo_anterior + valor_convertido
        return valor_convertido
    else:
        print("\nSaldo insuficiente.")
        return None
