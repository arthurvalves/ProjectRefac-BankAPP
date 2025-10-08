from database.ger_bd import DBManager
from database.ger_transacao_bd import salvar_transacao, criar_tabela_transacoes, deletar_transacoes
from services.emprest_service import solicitar_emprestimo
from services.transfer_service import transferir
from services.alerta_service import definir_alerta, verificar_alerta
from services.cambio_service import cambio 
from services.pagar_service import pagar_conta
from services.talao_service import solicitar_talao
from services.suporte_service import registrar_suporte, listar_mensagens
from commands import (
    CriarContaCommand, VerSaldoCommand, DepositarCommand, SacarCommand,
    AplicarInvestimentoCommand, SairCommand, NullCommand)
from services.investimento_strategies import CDBStrategy, TesouroDiretoStrategy
from observer import ObservadorAlertaTransacao
import os

simbolos_moeda = {'BRL': 'R$', 'USD': '$', 'EUR': '€', 'JPY': '¥'}

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
        # Anexa o observador aqui, garantindo que seja feito apenas uma vez por sessão
        alert_observer = ObservadorAlertaTransacao()
        conta.anexar(alert_observer)

    return conta

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

def ver_historico():
    acc_num = input("Número da conta: ")
    conta = procurar_conta(acc_num)
    if conta:
        print("\n --- Histórico de Transações ---\n ")
        if not conta.historico:
            print("\n Nenhuma transação registrada.\n")
        else:
            for transacao in conta.historico:
                texto = str(transacao)
                print(f"- {texto}")
    else:
        print("\nConta não encontrada.\n")

def limpar_historico():
    acc_num = input("Número da conta: ")
    conta = procurar_conta(acc_num)
    if conta:
        confirm = input("Tem certeza que deseja apagar TODO o histórico? (s/n): ").lower()
        if confirm == "s":
            conta.historico.clear()                 
            deletar_transacoes(conta.num_conta)     
            db.salvar_conta(conta)                     
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
        # Anexar o observador para notificar sobre o saque do pagamento
        alert_observer = ObservadorAlertaTransacao()
        conta.anexar(alert_observer)
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
            # Anexar o observador para notificar sobre o saque do talão
            alert_observer = ObservadorAlertaTransacao()
            conta.anexar(alert_observer)
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


def menu():
    while True:
        print("\n========= AV BANK =========\n")
        
        print("--- Gestão da Conta ---")
        print(" 1 - Criar conta")
        print(" 2 - Ver saldo")
        print(" 3 - Ver histórico de transações")
        print(" 4 - Definir alerta de saldo")
        print(" 5 - Limpar histórico da conta")
        
        print("\n--- Operações Financeiras ---")
        print(" 6 - Depositar")
        print(" 7 - Sacar")
        print(" 8 - Transferir")
        print(" 9 - Pagar conta")

        print("\n--- Produtos e Serviços ---")
        print("10 - Solicitar empréstimo")
        print("11 - Câmbio de moedas")
        print("12 - Aplicar em Investimentos")
        print("13 - Solicitar talão de cheques")

        print("\n--- Sistema e Suporte ---")
        print("14 - Suporte ao Cliente")
        print("15 - Sair")

        opcao = input("\nEscolha uma opção: ")

        if opcao == "1":
            CriarContaCommand(db, procurar_conta).execute()
        elif opcao == "2":
            VerSaldoCommand(procurar_conta).execute()
        elif opcao == "3":
            ver_historico()
        elif opcao == "4":
            conta = procurar_conta(input("Número da conta: "))
            if conta:
                limite = float(input("Definir alerta se saldo for menor que: R$"))
                definir_alerta(conta, limite)
                print(f"\nAlerta definido para a conta {conta.num_conta} com limite de R${limite:.2f}.\n")

            else:
                print("\nConta não encontrada.\n")
                
        elif opcao == "5":
            limpar_historico()
            
        elif opcao == "6":
            DepositarCommand(db, procurar_conta).execute()
            
        elif opcao == "7":
            SacarCommand(db, procurar_conta).execute()
            
        elif opcao == "8":
            transferir_entre_contas()
            
        elif opcao == "9":
            pagamento_de_conta()
            
        elif opcao == "10":
            conta = procurar_conta(input("Número da conta: "))
            if conta:
                # Anexar o observador para notificar sobre o crédito do empréstimo
                alert_observer = ObservadorAlertaTransacao()
                conta.anexar(alert_observer)
                valor = float(input("Valor do empréstimo: "))
                solicitar_emprestimo(conta, valor)
                salvar_transacao(conta.num_conta, conta.historico[-1])
                db.salvar_conta(conta)
                print("\nEmpréstimo realizado.\n")
            else:
                print("\nConta não encontrada.\n")
                
        elif opcao == "11":
            conta = procurar_conta(input("Número da conta: "))
            if conta:
                # Anexar o observador para notificar sobre o saque do câmbio
                alert_observer = ObservadorAlertaTransacao()
                conta.anexar(alert_observer)
                while True:
                    moeda = input("Para qual moeda (USD, EUR, JPY): ").upper()
                    if moeda in ["USD", "EUR", "JPY"]:
                        break
                    print("\nMoeda inválida. Por favor, escolha entre USD, EUR ou JPY.\n")

                valor = float(input("Valor em R$: "))
                valor_convertido = cambio(conta, moeda, valor)
                
                if valor_convertido is not None:
                    salvar_transacao(conta.num_conta, conta.historico[-1])
                    db.salvar_conta(conta)
                    print(f"\nOperação realizada com sucesso! Valor convertido: {valor_convertido:.2f} {moeda}\n")
                else:
                    print("\nOperação de câmbio falhou.\n")
            else:
                print("\nConta não encontrada.\n")
                
        elif opcao == "12":
            AplicarInvestimentoCommand(db, procurar_conta).execute()
        elif opcao == "13":
            solicitar_talao_cheques()
        elif opcao == "14":
            suporte_cliente()
        elif opcao == "15":
            print("\nEncerrando o sistema. Obrigado!\n")
            break
        else:
            os.system('cls')
            print("\nOpção inválida!\n")
            

if __name__ == "__main__":
    db = DBManager()
    db.criar_tabelas()
    criar_tabela_transacoes()
    menu()
