from datetime import datetime
from models.transacoes import Transacao
from observer import Observavel

class Conta(Observavel):
    def __init__(self, num_conta, proprietario, saldo=0.0, moeda='BRL'):
        super().__init__()  # Inicializa a lista de observadores
        self.num_conta = num_conta
        self.proprietario = proprietario
        self.saldo = saldo  # Saldo principal sempre em BRL
        self.saldos_estrangeiros = {}  # Dicionário para { 'USD': 100.0, 'EUR': 50.0 }
        self.historico = []
        self.alerta_saldo = None

    def anexar(self, observador):
        if observador not in self._observadores:
            self._observadores.append(observador)

    def desanexar(self, observador):
        self._observadores.remove(observador)

    def notificar(self):
        for observador in self._observadores:
            observador.update(self)

    def deposito(self, quantidade):
        if quantidade > 0.0:
            self.saldo += quantidade
            from main import simbolos_moeda
            self.historico.append(Transacao("Depósito", quantidade, simbolo_moeda='R$'))
            self.notificar()

    def saque(self, quantidade):
        if 0 < quantidade <= self.saldo:
            self.saldo -= quantidade
            self.historico.append(Transacao("Saque", quantidade))
            self.notificar()
            return True
        else:
            self.historico.append(Transacao("Saque falhou", quantidade, descricao="Saldo insuficiente"))
            # Opcional: notificar também em caso de falha
            # self.notificar()
            return False

    def registrar_transferencia(self, valor, destino):
        self.historico.append(Transacao("Transferência enviada", valor, descricao=f"Para conta {destino.num_conta}"))
        self.notificar()

    def registrar_recebimento(self, valor, origem):
        nome_remetente = origem.proprietario.nome
        self.historico.append(Transacao("Transferência recebida", valor, descricao=f"De: {nome_remetente} (Conta: {origem.num_conta})"))
        self.notificar()
