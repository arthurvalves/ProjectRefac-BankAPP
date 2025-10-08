from database.ger_bd import DBManager
from models.conta_factory import ContaFactory

class AccountService:
    def __init__(self):
        self.db = DBManager()
        self.contas = []

    def procurar_conta(self, num_conta):
        for conta in self.contas:
            if conta.num_conta == num_conta:
                return conta
        conta = self.db.carregar_conta(num_conta)
        if conta:
            self.contas.append(conta)
        return conta

    def criar_conta(self, tipo, nome, cpf, endereco=None, telefone=None, email=None):
        num_conta = None
        from utils.validacao import gerar_numero_conta
        num_conta = gerar_numero_conta()
        conta = ContaFactory.criar_conta(tipo, num_conta, nome, cpf)
        conta.proprietario.endereco = endereco
        conta.proprietario.telefone = telefone
        conta.proprietario.email = email
        self.db.salvar_conta(conta)
        self.contas.append(conta)
        return conta
