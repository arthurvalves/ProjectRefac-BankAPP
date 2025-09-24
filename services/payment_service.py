from models.transaction import Transacao

def pagar_conta(conta, descricao, valor):
    if conta.saque(valor):
        conta.historico.append(Transacao("Pagamento de Conta", valor, descricao=descricao))
        return True
    return False
