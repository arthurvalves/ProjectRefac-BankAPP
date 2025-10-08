def transferir(origem, destino, valor):
    if valor > 0 and origem.saldo >= valor:
        origem.saldo -= valor
        destino.saldo += valor

        origem.registrar_transferencia(valor, destino)
        destino.registrar_recebimento(valor, origem)
        return True
        
    return False
