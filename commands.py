from abc import ABC, abstractmethod
from database.ger_bd import DBManager
from database.ger_transacao_bd import salvar_transacao, deletar_transacoes
from models.conta_factory import ContaFactory
from models.user_builder import UserBuilder
from utils.validacao import validar_nome, validar_cpf, validar_email, validar_telefone, gerar_numero_conta
from services.emprest_service import aplicar_investimento, solicitar_emprestimo
from services.investimento_strategies import CDBStrategy, TesouroDiretoStrategy
from services.transfer_service import transferir
from services.alerta_service import definir_alerta, verificar_alerta
from services.cambio_service import cambio
from services.pagar_service import pagar_conta
from services.talao_service import solicitar_talao
from services.suporte_service import registrar_suporte, listar_mensagens

simbolos_moeda = {'BRL': 'R$', 'USD': '$', 'EUR': '€', 'JPY': '¥'}

class Command(ABC):
    @abstractmethod
    def execute(self):
        pass

class CriarContaCommand(Command):
    def __init__(self, db, procurar_conta_func):
        self.db = db
    
    def execute(self):
        nome = input("Nome do titular: ")
        if not validar_nome(nome):
            print("Nome inválido! Use apenas letras e espaços.")
            return
        
        cpf = input("CPF: ")
        if not validar_cpf(cpf):
            print("CPF inválido!")
            return
        
        endereco = input("Endereço (opcional): ")
        telefone = input("Telefone (opcional): ")
        
        if telefone and not validar_telefone(telefone):
            print("Telefone inválido! Informe um número nacional válido.")
            return
        
        email = input("E-mail (opcional): ")
        if email and not validar_email(email):
            print("E-mail inválido!")
            return
        
        num_conta = gerar_numero_conta()
        
        while True:
            tipo = input("Tipo de conta (corrente/poupanca): ").strip().lower()
            if tipo in ["corrente", "poupanca"]:
                break
            print("\nTipo de conta incorreta, escolha entre Corrente ou Poupanca\n")

        print("\nA conta será aberta em BRL (Real). Você poderá fazer câmbio para outra moeda depois pelo menu de câmbio.")

        builder = UserBuilder().set_nome(nome).set_cpf(cpf)
        if endereco: builder.set_endereco(endereco)
        if telefone: builder.set_telefone(telefone)
        if email: builder.set_email(email)

        try:
            user = builder.build()
            conta = ContaFactory.criar_conta(tipo, num_conta, user.nome, user.cpf)
            conta.proprietario.endereco = user.endereco
            conta.proprietario.telefone = user.telefone
            conta.proprietario.email = user.email
            self.db.salvar_conta(conta)
            print(f"\nConta {conta.tipo} criada com sucesso para {user.nome}! Número da conta: {num_conta} | Moeda: BRL\n")
        except ValueError as e:
            print(f"\nErro: {e}\n")

class VerSaldoCommand(Command):
    def __init__(self, procurar_conta_func):
        self.procurar_conta = procurar_conta_func

    def execute(self):
        conta = self.procurar_conta(input("Número da conta: "))
        if conta:
            print("\n--- Saldo da Conta ---")
            print(f"Saldo em BRL: R${conta.saldo:.2f}")
            if conta.saldos_estrangeiros:
                for moeda, valor in conta.saldos_estrangeiros.items():
                    simbolo = simbolos_moeda.get(moeda, moeda)
                    print(f"Saldo em {moeda}: {simbolo}{valor:.2f}")
        else:
            print("\nConta não encontrada.\n")

class DepositarCommand(Command):
    def __init__(self, db, procurar_conta_func):
        self.db = db
        self.procurar_conta = procurar_conta_func

    def execute(self):
        conta = self.procurar_conta(input("Número da conta: "))
        if not conta:
            print("\nConta não encontrada.\n")
            return
        
        try:
            quantidade = float(input("Valor para depósito: "))
            if quantidade <= 0:
                print("\nValor inválido. O depósito deve ser um número positivo.\n")
                return
        except ValueError:
            print("\nValor inválido.\n")
            return
            
        conta.deposito(quantidade)
        salvar_transacao(conta.num_conta, conta.historico[-1])
        self.db.salvar_conta(conta)
        print(f"\nDepósito de R${quantidade:.2f} realizado com sucesso!\n")
        verificar_alerta(conta)

class SacarCommand(Command):
    def __init__(self, db, procurar_conta_func):
        self.db = db
        self.procurar_conta = procurar_conta_func

    def execute(self):
        conta = self.procurar_conta(input("Número da conta: "))
        if not conta:
            print("\nConta não encontrada.\n")
            return

        try:
            quantidade = float(input("Valor para saque: "))
        except ValueError:
            print("\nValor inválido.\n")
            return

        if quantidade <= 0:
            print("\nValor inválido para saque.\n")
            return

        if conta.saque(quantidade):
            salvar_transacao(conta.num_conta, conta.historico[-1])
            self.db.salvar_conta(conta)
            print(f"\nSaque de R${quantidade:.2f} realizado com sucesso!\n")
            verificar_alerta(conta)
        else:
            print("\nOperação de saque falhou. Saldo insuficiente?\n")

class AplicarInvestimentoCommand(Command):
    def __init__(self, db, procurar_conta_func):
        self.db = db
        self.procurar_conta = procurar_conta_func

    def execute(self):
        conta = self.procurar_conta(input("Número da conta: "))
        if not conta:
            print("\nConta não encontrada.\n")
            return

        print("\nEscolha o tipo de investimento:")
        print("1 - CDB (0,90% a.m.)")
        print("2 - Tesouro Direto (0,75% a.m.)")
        opcao = input("Digite o número da opção: ")

        estrategias = {
            
            "1": CDBStrategy(),
            "2": TesouroDiretoStrategy()
        }
        estrategia = estrategias.get(opcao)

        if estrategia is None:
            print("\nOpção inválida.\n")
            return

        try:
            valor = float(input("Valor a aplicar: "))
            meses = int(input("Prazo em meses: "))
        except ValueError:
            print("\nValor ou prazo inválido.\n")
            return

        if meses > 1200:
            print("\nPrazo de investimento muito longo. O máximo permitido é 1200 meses.\n")
            return

        retorno = aplicar_investimento(conta, valor, meses, estrategia)

        if retorno is not None:
            salvar_transacao(conta.num_conta, conta.historico[-1])
            self.db.salvar_conta(conta)
            print(f"\nInvestimento realizado. Retorno estimado ao final do período: R${retorno:.2f}\n")
            verificar_alerta(conta)
        else:
            print("\nFalha ao aplicar investimento. Saldo insuficiente?\n")

class SairCommand(Command):
    def __init__(self, app):
        self.app = app

    def execute(self):
        self.app.running = False
        print("\nEncerrando o sistema. Obrigado!\n")


class NullCommand(Command):
    def execute(self):
        print("\nOpção inválida!\n")