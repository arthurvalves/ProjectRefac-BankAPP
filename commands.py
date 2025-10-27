from abc import ABC, abstractmethod
from database.ger_bd import DBManager
from database.ger_transacao_bd import salvar_transacao, deletar_transacoes
from models.conta_factory import ContaFactory
from models.user_builder import UserBuilder
from utils.validacao import validar_nome, validar_cpf, validar_email, validar_telefone, gerar_numero_conta
from services.emprest_service import aplicar_investimento
from services.investimento_strategies import CDBStrategy, TesouroDiretoStrategy
from services.transfer_service import transferir
from services.alerta_service import definir_alerta, verificar_alerta
from services.cambio_service import cambio 
from utils.observer import Observavel
from services.pagar_service import pagar_conta
from services.talao_service import solicitar_talao
from services.suporte_service import registrar_suporte, listar_mensagens
from services.facade import FachadaBanco
from services.auth import registrar_credenciais, senha_valida, definir_pergunta_seguranca, PERGUNTAS_SEGURANCA
from services.sessao import papel_atual as current_role, usuario_atual as current_user
from services.auth import verificar_credenciais

simbolos_moeda = {'BRL': 'R$', 'USD': '$', 'EUR': '€', 'JPY': '¥'}

class Command(ABC):
    @abstractmethod
    def execute(self):
       pass

class CriarContaCommand(Command):
    def __init__(self, db, procurar_conta_func):
        self.db = db

    def execute(self):
        # repetir até nome válido
        while True:
            nome = input("Nome do titular: ")
            if validar_nome(nome):
                break
            print("Nome inválido! Use apenas letras e espaços.")

        # repetir até CPF válido
        while True:
            cpf = input("CPF: ")
            if validar_cpf(cpf):
                break
            print("CPF inválido!")

        # verificar CPF duplicado (não revelar número da conta existente)
        from database.ger_bd import DBManager
        dbm = DBManager()
        existing = dbm.carregar_conta_por_cpf(cpf)
        if existing:
            print("\nJá existe uma conta cadastrada com o CPF informado. Se esqueceu a senha, use a opção 'Esqueci a senha'.\n")
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
            usuario = builder.build()
            conta = ContaFactory.criar_conta(tipo, num_conta, usuario.nome, usuario.cpf)
            conta.proprietario.endereco = usuario.endereco
            conta.proprietario.telefone = usuario.telefone
            conta.proprietario.email = usuario.email
            self.db.salvar_conta(conta)
            # perguntar e registrar pergunta de segurança antes da senha
            print('\nEscolha uma pergunta de segurança e responda (será usada para recuperar senha):')
            for pid, texto in PERGUNTAS_SEGURANCA.items():
                print(f" {pid} - {texto}")
            while True:
                try:
                    pid = int(input('Escolha o número da pergunta: '))
                    if pid in PERGUNTAS_SEGURANCA:
                        break
                except ValueError:
                    pass
                print('Pergunta inválida. Escolha um número válido.')
            answer = input('Digite a resposta da pergunta de segurança: ')
            if not answer:
                print('Resposta vazia. A conta será criada sem pergunta de segurança.')
            else:
                try:
                    definir_pergunta_seguranca(num_conta, pid, answer)
                    print('Pergunta de segurança registrada.')
                except Exception as e:
                    print('Erro ao registrar pergunta de segurança:', e)

            # cadastrar credenciais — exigir senha de 6 dígitos numéricos
            while True:
                senha = input("Defina uma senha NUMÉRICA de 6 dígitos para a conta: ")
                if senha_valida(senha):
                    try:
                        registrar_credenciais(num_conta, senha, papel='usuario')
                        print('Credenciais registradas com sucesso.')
                    except Exception as e:
                        print('Erro ao registrar credenciais:', e)
                    break
                print('Senha inválida. Deve ser exatamente 6 dígitos numéricos.')
            print(f"\nConta {conta.tipo} criada com sucesso para {usuario.nome}! Número da conta: {num_conta} | Moeda: BRL\n")
        except ValueError as e:
            print(f"\nErro: {e}\n")


class CriarAdminCommand(Command):
    def __init__(self, db):
        self.db = db

    def execute(self):
        if current_role() != 'admin':
            print('\nApenas administradores podem criar novos administradores.\n')
            return

        num_conta = input('Número da conta a promover: ')
        # optar por registrar pergunta de segurança
        print('\nOpcional: registre uma pergunta de segurança para recuperar senha:')
        for pid, texto in PERGUNTAS_SEGURANCA.items():
            print(f" {pid} - {texto}")
        try:
            pid_in = input('Escolha o número da pergunta (ou enter para pular): ')
            if pid_in:
                pid = int(pid_in)
                if pid in PERGUNTAS_SEGURANCA:
                    ans = input('Digite a resposta da pergunta de segurança: ')
                    if ans:
                        definir_pergunta_seguranca(num_conta, pid, ans)
                        print('Pergunta de segurança registrada.')
        except Exception as e:
            print('Erro ao registrar pergunta de segurança:', e)

        # exigir senha válida
        while True:
            senha = input('Defina uma senha NUMÉRICA de 6 dígitos para o administrador: ')
            if senha_valida(senha):
                try:
                    registrar_credenciais(num_conta, senha, papel='admin')
                    print('\nAdministrador criado/atualizado com sucesso.\n')
                except Exception as e:
                    print('Erro ao registrar credenciais:', e)
                break
            print('Senha inválida. Deve ser exatamente 6 dígitos numéricos.')

class VerSaldoCommand(Command):
    def __init__(self, procurar_conta_func):
       self.procurar_conta = procurar_conta_func

    def execute(self):
        num = current_user()
        if num:
            conta = self.procurar_conta(num)
        else:
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
        self.facade = FachadaBanco()


    def execute(self):
        num = current_user()
        if num:
            conta = self.procurar_conta(num)
        else:
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

        # confirmação por senha no final
        sess = current_user()
        if sess:
            senha = input("Confirme sua senha (6 dígitos): ")
            if not verificar_credenciais(sess, senha):
                print("\nSenha incorreta. Operação cancelada.\n")
                return
        else:
            autor = input("Número da conta autorizadora: ")
            senha = input("Senha da conta autorizadora (6 dígitos): ")
            if not verificar_credenciais(autor, senha):
                print("\nCredenciais inválidas. Operação cancelada.\n")
                return

        # Usar facade para centralizar persistência e lógica
        self.facade.depositar(conta, quantidade)
        print(f"\nDepósito de R$ {quantidade:.2f} realizado com sucesso!\n")
        verificar_alerta(conta)

class SacarCommand(Command):
    def __init__(self, db, procurar_conta_func):
        self.db = db
        self.procurar_conta = procurar_conta_func
        self.facade = FachadaBanco()
    def execute(self):
        num = current_user()
        if num:
            conta = self.procurar_conta(num)
        else:
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

        # pedir senha de confirmação somente após validações
        sess = current_user()
        if sess:
            senha = input("Confirme sua senha (6 dígitos): ")
            if not verificar_credenciais(sess, senha):
                print("\nSenha incorreta. Operação cancelada.\n")
                return
        else:
            autor = input("Número da conta autorizadora: ")
            senha = input("Senha da conta autorizadora (6 dígitos): ")
            if not verificar_credenciais(autor, senha):
                print("\nCredenciais inválidas. Operação cancelada.\n")
                return

        if self.facade.sacar(conta, quantidade):
            print(f"\nSaque de R$ {quantidade:.2f} realizado com sucesso!\n")
            verificar_alerta(conta)
        else:
            print("\nOperação de saque falhou. Saldo insuficiente?\n")
class AplicarInvestimentoCommand(Command):
    def __init__(self, db, procurar_conta_func):
        self.db = db
        self.procurar_conta = procurar_conta_func

    def execute(self):
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

        num = current_user()
        if num:
            conta = self.procurar_conta(num)
        else:
            conta = self.procurar_conta(input("Número da conta para o investimento: "))
        if not conta:
            print("\nConta não encontrada.\n")
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

        # pedir senha de confirmação no final antes de aplicar
        sess = current_user()
        if sess:
            senha = input("Confirme sua senha (6 dígitos): ")
            if not verificar_credenciais(sess, senha):
                print("\nSenha incorreta. Operação cancelada.\n")
                return
        else:
            autor = input("Número da conta autorizadora: ")
            senha = input("Senha da conta autorizadora (6 dígitos): ")
            if not verificar_credenciais(autor, senha):
                print("\nCredenciais inválidas. Operação cancelada.\n")
                return

        retorno = aplicar_investimento(conta, valor, meses, estrategia)

        if retorno is not None:
            salvar_transacao(conta.num_conta, conta.historico[-1])
            self.db.salvar_conta(conta)
            print(f"\nInvestimento realizado. Retorno estimado ao final do período: R$ {retorno:.2f}\n")
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