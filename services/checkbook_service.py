
from models.transaction import Transacao

def solicitar_talao(conta, quantidade=1, cheques_por_talao=25, custo_por_talao=15.0):
    total = quantidade * custo_por_talao
    if conta.saque(total):
        descricao = f"Solicitado {quantidade} talão(ões) com {cheques_por_talao} cheques cada (R${total:.2f})"
        conta.historico.append(Transacao("Solicitação de Talão", total, descricao=descricao))
        return True
    else:
        conta.historico.append(Transacao("Solicitação de Talão falhou", 0.0, descricao="Saldo insuficiente"))
        return False
