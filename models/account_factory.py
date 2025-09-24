from models.account import Conta
from models.user import User

class ContaCorrente(Conta):
    def __init__(self, num_conta, proprietario, saldo=0.0):
        super().__init__(num_conta, proprietario, saldo)
        self.tipo = "Corrente"

class ContaPoupanca(Conta):
    def __init__(self, num_conta, proprietario, saldo=0.0):
        super().__init__(num_conta, proprietario, saldo)
        self.tipo = "Poupança"

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
