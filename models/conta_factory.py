from models.conta import Conta
from models.user import User

class ContaCorrente(Conta):
    def __init__(self, num_conta, proprietario, saldo=0.0):
        super().__init__(num_conta, proprietario, saldo)
        self.tipo = "Corrente"

class ContaPoupanca(Conta):
    def __init__(self, num_conta, proprietario, saldo=0.0):
        super().__init__(num_conta, proprietario, saldo)
        self.tipo = "Poupança"
        self.ultima_data_rendimento = None

    def render(self, dias = 1): 
        taxa = 0.00016
        for _ in range(dias):
            self.saldo = self.saldo * (1 + taxa)
            
        from models.transacoes import Transacao
        self.historico.append(Transacao("Rendimento poupança", self.saldo * taxa, descricao=f"Rendimento de {dias} dia(s)"))

class ContaFactory:
    @staticmethod
    def criar_conta(tipo, num_conta, nome, cpf, saldo=0.0):
        user = User(nome, cpf)
        if tipo == "corrente":
            return ContaCorrente(num_conta, user, saldo)
        elif tipo == "poupanca":
            return ContaPoupanca(num_conta, user, saldo)
        else:
            raise ValueError("Tipo de conta inválido")
