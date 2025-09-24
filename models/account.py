from datetime import datetime
from models.transaction import Transacao

class Conta:
    def __init__(self, num_conta, proprietario, saldo=0.0, moeda='BRL'):
        self.num_conta = num_conta
        self.proprietario = proprietario
        self.saldo = saldo
        self.moeda = moeda  # Suporte a múltiplas moedas
        self.historico = []
        self.alerta_saldo = None

    def deposito(self, quantidade):
        if quantidade > 0.0:
            self.saldo += quantidade
            self.historico.append(Transacao("Depósito", quantidade))

    def saque(self, quantidade):
        if 0 < quantidade <= self.saldo:
            self.saldo -= quantidade
            self.historico.append(Transacao("Saque", quantidade))
            return True
        else:
            self.historico.append(Transacao("Saque falhou", quantidade, descricao="Saldo insuficiente"))
            return False

    def registrar_transferencia(self, valor, destino):
        self.historico.append(Transacao("Transferência enviada", valor, descricao=f"Para conta {destino.num_conta}"))

    def registrar_recebimento(self, valor, origem):
        self.historico.append(Transacao("Transferência recebida", valor, descricao=f"De conta {origem.num_conta}"))
