from utils.exceptions import ValidationError, InsufficientFundsError


def transferir(origem, destino, valor):
    if valor <= 0:
        raise ValidationError("Valor de transferência deve ser maior que zero", code="INVALID_AMOUNT")

    if origem.saldo < valor:
        raise InsufficientFundsError("Saldo insuficiente para transferência", details={"conta_origem": origem.num_conta, "valor": valor})

    origem.saldo -= valor
    destino.saldo += valor

    origem.registrar_transferencia(valor, destino)
    destino.registrar_recebimento(valor, origem)
    return True
