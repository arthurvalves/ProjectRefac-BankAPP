from datetime import datetime
from models.transacoes import Transacao
from utils.observer import Observavel

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

    def saque(self, quantidade, registrar=True):
        """
        Realiza saque. Por padrão registra a transação no histórico.
        Se registrar=False, apenas ajusta o saldo (útil para operações internas como câmbio,
        que registrarão uma transação própria com tipo diferente).
        """
        if 0 < quantidade <= self.saldo:
            self.saldo -= quantidade
            if registrar:
                self.historico.append(Transacao("Saque", quantidade))
            self.notificar()
            return True
        else:
            if registrar:
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

    def transferir_para(self, destino, quantidade):
        # Não permitir transferir para a mesma conta
        if destino is None or destino.num_conta == self.num_conta:
            self.historico.append(Transacao("Transferência falhou", quantidade, descricao="Destino inválido"))
            return False
        if 0 < quantidade <= self.saldo:
            self.saldo -= quantidade
            # creditar o saldo do destino — antes isso não acontecia e resultava em histórico sem ajuste de saldo
            destino.saldo += quantidade
            # registra envio
            self.registrar_transferencia(quantidade, destino)
            # registra recebimento no destino
            destino.registrar_recebimento(quantidade, self)
            self.notificar()
            return True
        else:
            self.historico.append(Transacao("Transferência falhou", quantidade, descricao="Saldo insuficiente"))
            return False

    def pagar(self, descricao, valor):
        # pagamento de conta: debita do saldo se houver fundos
        if valor <= 0:
            self.historico.append(Transacao("Pagamento falhou", valor, descricao="Valor inválido"))
            return False
        if valor <= self.saldo:
            self.saldo -= valor
            self.historico.append(Transacao("Pagamento", valor, descricao=descricao))
            self.notificar()
            return True
        else:
            self.historico.append(Transacao("Pagamento falhou", valor, descricao="Saldo insuficiente"))
            return False

    def solicitar_talao(self, quantidade, cheques_por_talao=25, custo_por_talao=15.0):
        """
        Solicita talões e debita o custo da conta. Registra no histórico o valor total.
        """
        if quantidade <= 0:
            self.historico.append(Transacao("Solicitação de talão falhou", 0, descricao="Quantidade inválida"))
            return False
        total = quantidade * custo_por_talao
        # usa saque sem registro separado para evitar duplicação se quisermos um registro específico
        if self.saque(total, registrar=False):
            descricao = f"Quantidade: {quantidade} talão(ões) x R${custo_por_talao:.2f} = R${total:.2f}"
            self.historico.append(Transacao("Solicitação de talão", total, descricao=descricao))
            self.notificar()
            return True
        else:
            self.historico.append(Transacao("Solicitação de talão falhou", total, descricao="Saldo insuficiente"))
            return False
