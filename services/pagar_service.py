from models.transacoes import Transacao
from utils.exceptions import InsufficientFundsError, ValidationError


def pagar_conta(conta, descricao, valor):
    if valor <= 0:
        raise ValidationError("Valor do pagamento deve ser maior que zero", code="INVALID_AMOUNT")

    if conta.saque(valor):
        conta.historico.append(Transacao("Pagamento de Conta", valor, descricao=descricao))
        return True

    raise InsufficientFundsError("Saldo insuficiente para pagamento", details={"conta": conta.num_conta, "valor": valor})
