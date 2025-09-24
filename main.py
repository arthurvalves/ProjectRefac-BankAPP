from database.db_manager import DBManager
from database.db_transaction_manager import salvar_transacao, criar_tabela_transacoes, deletar_transacoes
from models.account_factory import ContaFactory
from models.user_builder import UserBuilder
from utils.validation import validar_nome, validar_cpf, gerar_numero_conta
from services.loan_service import aplicar_investimento, solicitar_emprestimo
from services.transfer_service import transferir
from services.notification_service import definir_alerta, verificar_alerta
from services.currency_service import cambio 
from services.payment_service import pagar_conta
from services.checkbook_service import solicitar_talao
from services.support_service import registrar_suporte, listar_mensagens



db = DBManager()
db.criar_tabelas()

users = []
contas = []


def procurar_conta(num_conta):
    for conta in contas:
        if conta.num_conta == num_conta:
            return conta
    conta = db.carregar_conta(num_conta)
    if conta:
        contas.append(conta)
    return conta






def criando_user():
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
    tipo = input("Tipo de conta (corrente/poupanca): ").strip().lower()
    moeda = input("Moeda da conta (BRL/USD/EUR): ").strip().upper()

    builder = UserBuilder().set_nome(nome).set_cpf(cpf)
    if endereco:
        builder.set_endereco(endereco)
    if telefone:
        builder.set_telefone(telefone)
    if email:
        builder.set_email(email)

    try:
        user = builder.build()
        conta = ContaFactory.criar_conta(tipo, num_conta, user.nome, user.cpf)
        conta.moeda = moeda if moeda in ['BRL', 'USD', 'EUR'] else 'BRL'
        conta.proprietario.endereco = user.endereco
        conta.proprietario.telefone = user.telefone
        conta.proprietario.email = user.email
        db.salvar_conta(conta)
        print(f"\nConta {conta.tipo} criada com sucesso para {user.nome}! Número da conta: {num_conta} | Moeda: {conta.moeda}\n")
    except ValueError as e:
        print(f"\nErro: {e}\n")


def depositar():
    acc_num = input("Número da conta: ")
    conta = procurar_conta(acc_num)

    if conta:
        quantidade = float(input("Valor para depósito: "))
        conta.deposito(quantidade)
        transacao = conta.historico[-1]
        salvar_transacao(conta.num_conta, transacao)
        db.salvar_conta(conta)

        print(f"\nDepósito de R${quantidade:.2f} realizado com sucesso!\n")
        verificar_alerta(conta)
    else:
        print("\nConta não encontrada.\n")

def sacar():
    acc_num = input("Número da conta: ")
    conta = procurar_conta(acc_num)

    if conta:
        quantidade = float(input("Valor para saque: "))
        if quantidade <= 0:
            print("\nValor inválido para saque.\n")
            return
        if quantidade > conta.saldo:
            print("\nSaldo insuficiente.\n")
            return
        if conta.saque(quantidade):
            salvar_transacao(conta.num_conta, conta.historico[-1])
            db.salvar_conta(conta)
            print(f"\nSaque de R${quantidade:.2f} realizado com sucesso!\n")
            verificar_alerta(conta)
        else:
            print("\nOperação de saque falhou.\n")
    else:
        print("\nConta não encontrada.\n")

def transferir_entre_contas():
    acc_origem = input("Conta de origem: ")
    acc_destino = input("Conta de destino: ")
    quantidade = float(input("Valor da transferência: "))

    origem = procurar_conta(acc_origem)
    destino = procurar_conta(acc_destino)

    if origem and destino:
        if quantidade <= 0:
            print("\nValor inválido para transferência.\n")
            return
        if quantidade > origem.saldo:
            print("\nSaldo insuficiente na conta de origem.\n")
            return
        if transferir(origem, destino, quantidade):
            salvar_transacao(origem.num_conta, origem.historico[-1])
            salvar_transacao(destino.num_conta, destino.historico[-1])
            db.salvar_conta(origem)
            db.salvar_conta(destino)
            print("\nTransferência realizada com sucesso!\n")
            verificar_alerta(origem)
        else:
            print("\nOperação de transferência falhou.\n")
    else:
        print("\nConta(s) não encontrada(s).\n")

def ver_saldo():
    acc_num = input("Número da conta: ")
    conta = procurar_conta(acc_num)
    if conta:
        print(f"\nSaldo atual: R${conta.saldo:.2f}\n")
    else:
        print("\nConta não encontrada.\n")

def ver_historico():
    acc_num = input("Número da conta: ")
    conta = procurar_conta(acc_num)
    if conta:
        print("\n --- Histórico de Transações ---\n ")
        if not conta.historico:
            print("\n Nenhuma transação registrada.\n")
        else:
            for transacao in conta.historico:
                print(f"- {transacao}")
    else:
        print("\nConta não encontrada.\n")

def limpar_historico():
    acc_num = input("Número da conta: ")
    conta = procurar_conta(acc_num)
    if conta:
        confirm = input("Tem certeza que deseja apagar TODO o histórico? (s/n): ").lower()
        if confirm == "s":
            conta.historico.clear()                 # Limpa na memória
            deletar_transacoes(conta.num_conta)     # Limpa no banco
            db.salvar_conta(conta)                     # Atualiza saldo
            print("\nHistórico apagado com sucesso!\n")
        else:
            print("\nOperação cancelada.\n")
    else:
        print("\nConta não encontrada.\n")

def pagamento_de_conta():
    acc_num = input("Número da conta: ")
    conta = procurar_conta(acc_num)
    if conta:
        descricao = input("Descrição da conta (ex: Conta de luz): ")
        valor = float(input("Valor a pagar: "))
        if valor <= 0:
            print("\nValor inválido para pagamento.\n")
            return
        if valor > conta.saldo:
            print("\nSaldo insuficiente para pagar a conta.\n")
            return
        if pagar_conta(conta, descricao, valor):
            salvar_transacao(conta.num_conta, conta.historico[-1])
            db.salvar_conta(conta)
            print("\nPagamento realizado com sucesso!\n")
            verificar_alerta(conta)
        else:
            print("\nOperação de pagamento falhou.\n")
    else:
        print("\nConta não encontrada.\n")

def solicitar_talao_cheques():
    acc_num = input("Número da conta: ")
    conta = procurar_conta(acc_num)
    if conta:
        try:
            quantidade = int(input("Quantidade de talões a solicitar (R$15,00 cada): "))
            if quantidade <= 0:
                raise ValueError
        except ValueError:
            print("\nQuantidade inválida. Deve ser um número inteiro positivo.\n")
            return
        if solicitar_talao(conta, quantidade):
            salvar_transacao(conta.num_conta, conta.historico[-1])
            db.salvar_conta(conta)
            print(f"\n{quantidade} talão(ões) solicitado(s) com sucesso!\n")
            verificar_alerta(conta)
        else:
            salvar_transacao(conta.num_conta, conta.historico[-1])
            db.salvar_conta(conta)
            print("\nSaldo insuficiente para solicitar talão.\n")
    else:
        print("\nConta não encontrada.\n")

def suporte_cliente():
    acc_num = input("Número da conta: ")
    conta = procurar_conta(acc_num)
    if conta:
        print("\n1 - Enviar nova mensagem")
        print("2 - Ver mensagens anteriores")
        opcao = input("Escolha uma opção: ")

        if opcao == "1":
            mensagem = input("Descreva seu problema ou dúvida: ")
            registrar_suporte(acc_num, mensagem)
            print("\nMensagem enviada com sucesso. Um atendente entrará em contato.\n")
        elif opcao == "2":
            mensagens = listar_mensagens(acc_num)
            if mensagens:
                print("\n--- Histórico de Suporte ---")
                for linha in mensagens:
                    print(linha.strip())
                print()
            else:
                print("\nNenhuma mensagem registrada.\n")
        else:
            print("\nOpção inválida.\n")
    else:
        print("\nConta não encontrada.\n")

def aplicar_investimento_opcao():
    conta = procurar_conta(input("Número da conta: "))
    if conta:
        print("\nEscolha o tipo de investimento:")
        print("1 - Poupança (0,65% a.m.)")
        print("2 - CDB (0,90% a.m.)")
        print("3 - Tesouro Direto (0,75% a.m.)")
        opcao = input("Digite o número da opção: ")

        tipos = {"1": "poupanca", "2": "cdb", "3": "tesouro"}
        tipo = tipos.get(opcao)

        if tipo is None:
            print("\nOpção inválida.\n")
            return

        valor = float(input("Valor a aplicar: "))
        meses = int(input("Prazo em meses: "))
        retorno = aplicar_investimento(conta, valor, meses, tipo)

        if retorno:
            salvar_transacao(conta.num_conta, conta.historico[-1])
            db.salvar_conta(conta)
            print(f"\nInvestimento realizado. Retorno estimado: R${retorno:.2f}\n")
    else:
        print("\nConta não encontrada.\n")


def menu():
    while True:
        print("\n========= AV BANK =========\n")
        print("1 - Criar conta")
        print("2 - Depositar")
        print("3 - Sacar")
        print("4 - Transferir")
        print("5 - Ver saldo")
        print("6 - Ver histórico de transações")
        print("7 - Solicitar empréstimo")
        print("8 - Definir alerta de saldo")
        print("9 - Câmbio de moedas")
        print("10 - Aplicar em Poupança/Investimentos")
        print("11 - Limpar histórico da conta")
        print("12 - Pagar conta")
        print("13 - Solicitar talão de cheques")
        print("14 - Suporte ao Cliente")
        print("15 - Sair")



        opcao = input("Escolha uma opção: ")

        if opcao == "1":
            criando_user()
        elif opcao == "2":
            depositar()
        elif opcao == "3":
            sacar()
        elif opcao == "4":
            transferir_entre_contas()
        elif opcao == "5":
            ver_saldo()
        elif opcao == "6":
            ver_historico()
        elif opcao == "7":
            conta = procurar_conta(input("Número da conta: "))
            if conta:
                valor = float(input("Valor do empréstimo: "))
                solicitar_emprestimo(conta, valor)
                salvar_transacao(conta.num_conta, conta.historico[-1])
                db.salvar_conta(conta)

                print("\nEmpréstimo realizado.\n")
            else:
                print("\nConta não encontrada.\n")
        elif opcao == "8":
            db.salvar_conta(conta)
            
            if conta:
                limite = float(input("Definir alerta se saldo for menor que: R$"))
                print("\n")
                definir_alerta(conta, limite)
            else:
                print("\nConta não encontrada.\n")
        elif opcao == "9":
            conta = procurar_conta(input("Número da conta: "))
            if conta:
                moeda = input("Para qual moeda (USD, EUR, JPY): ").upper()
                valor = float(input("Valor em R$: "))
                valor_convertido = cambio(conta, moeda, valor)
                if valor_convertido is not None:
                    salvar_transacao(conta.num_conta, conta.historico[-1])
                    salvar_conta(conta)
                    print(f"\nOperação realizada com sucesso! Valor convertido: {valor_convertido:.2f} {moeda}\n")
                else:
                    print("\nOperação de câmbio falhou.\n")
            else:
                print("\nConta não encontrada.\n")
                db.salvar_conta(conta)
                
            aplicar_investimento_opcao()
        elif opcao == "11":
            limpar_historico()
        elif opcao == "12":
            pagamento_de_conta()
        elif opcao == "13":
            solicitar_talao_cheques()
        elif opcao == "14":
            suporte_cliente()
        elif opcao == "15":
            print("\nEncerrando o sistema. Obrigado!\n")
            break
        else:
            print("\nOpção inválida!\n")

if __name__ == "__main__":
    db = DBManager()
    db.criar_tabelas()
    criar_tabela_transacoes()
    menu()

