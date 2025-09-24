def transferir(origem, destino, valor):
    if origem.saque(valor):
        destino.deposito(valor)
        origem.registrar_transferencia(valor, destino)
        destino.registrar_recebimento(valor, origem)
        return True
    return False
