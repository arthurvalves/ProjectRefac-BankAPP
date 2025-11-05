from models.transacoes import Transacao
from utils.adapter import AdaptadorBCB
from utils.proxy import ProxyCacheCambio
from utils.exceptions import ExternalAPIError, InsufficientFundsError, ValidationError
from . import cambio_service as _module_ref


def cambio(conta, moeda_destino, valor_em_reais, provider=None):

    if valor_em_reais <= 0:
        raise ValidationError("Valor para câmbio deve ser maior que zero", code="INVALID_AMOUNT")

    if provider is None:
        base = AdaptadorBCB()
        provider = ProxyCacheCambio(base)

    taxa = provider.obter_taxa(moeda_destino)

    if taxa is None:
        # falha ao obter taxa -> exceção external
        raise ExternalAPIError("Moeda inválida ou erro ao obter taxa de câmbio", details={"moeda": moeda_destino})

    # efetua o débito sem criar um registro de 'Saque' separado; registramos uma transação do tipo 'Câmbio'
    if conta.saque(valor_em_reais, registrar=False):
        valor_convertido = valor_em_reais / taxa
        descricao = f"Conversão de R${valor_em_reais:.2f} para {valor_convertido:.2f} em {moeda_destino})"
        conta.historico.append(Transacao("Câmbio", valor_em_reais, descricao=descricao))

        # Adiciona o valor convertido ao dicionário de saldos estrangeiros
        saldo_anterior = conta.saldos_estrangeiros.get(moeda_destino, 0)
        conta.saldos_estrangeiros[moeda_destino] = saldo_anterior + valor_convertido
        return valor_convertido
    else:
        raise InsufficientFundsError("Saldo insuficiente para câmbio", details={"conta": conta.num_conta, "valor": valor_em_reais})
