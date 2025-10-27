from database.ger_bd import DBManager
from database.ger_transacao_bd import salvar_transacao


class FachadaBanco:
    def __init__(self):
        self.db = DBManager()

    def depositar(self, conta, quantidade: float):
        conta.deposito(quantidade)
        # persiste transação e conta
        if conta.historico:
            salvar_transacao(conta.num_conta, conta.historico[-1])
        self.db.salvar_conta(conta)

    def sacar(self, conta, quantidade: float) -> bool:
        ok = conta.saque(quantidade)
        if ok:
            if conta.historico:
                salvar_transacao(conta.num_conta, conta.historico[-1])
            self.db.salvar_conta(conta)
        return ok

    def transferir(self, origem, destino, quantidade: float) -> bool:
        ok = origem.transferir_para(destino, quantidade)
        if ok:
            # registrar transações mais recentes de ambas as contas
            if origem.historico:
                salvar_transacao(origem.num_conta, origem.historico[-1])
            if destino.historico:
                salvar_transacao(destino.num_conta, destino.historico[-1])
            self.db.salvar_conta(origem)
            self.db.salvar_conta(destino)
        return ok

    def pagar(self, conta, descricao: str, valor: float) -> bool:
        ok = conta.pagar(descricao, valor)
        if ok:
            if conta.historico:
                salvar_transacao(conta.num_conta, conta.historico[-1])
            self.db.salvar_conta(conta)
        return ok

    def solicitar_talao(self, conta, quantidade: int) -> bool:
        ok = conta.solicitar_talao(quantidade)
        if ok:
            if conta.historico:
                salvar_transacao(conta.num_conta, conta.historico[-1])
            self.db.salvar_conta(conta)
        return ok
