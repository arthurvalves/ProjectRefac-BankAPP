from database.ger_bd import DBManager
from database.ger_transacao_bd import salvar_transacao, criar_tabela_transacoes, deletar_transacoes
from services.emprest_service import solicitar_emprestimo
from services.transfer_service import transferir
from services.alerta_service import definir_alerta, verificar_alerta
from services.cambio_service import cambio 
from services.pagar_service import pagar_conta
from services.talao_service import solicitar_talao
from services.facade import FachadaBanco
from services.suporte_service import registrar_suporte, listar_mensagens
from commands import (
    CriarContaCommand, VerSaldoCommand, DepositarCommand, SacarCommand,
    AplicarInvestimentoCommand, SairCommand, NullCommand)
from services.investimento_strategies import CDBStrategy, TesouroDiretoStrategy
from utils.observer import ObservadorAlertaTransacao
import os
from services.auth import verificar_credenciais, registrar_credenciais, esta_bloqueado, registrar_tentativa_falha
from services.sessao import logar_sessao as login_session, deslogar_sessao as logout_session, usuario_atual as current_user, papel_atual as current_role

simbolos_moeda = {'BRL': 'R$', 'USD': '$', 'EUR': '€', 'JPY': '¥'}

db = DBManager() 
db.criar_tabelas()

# Facade para operações bancárias
facade = FachadaBanco()

users = []
contas = []





def procurar_conta(num_conta):
    for conta in contas:
        if conta.num_conta == num_conta:
            return conta
    conta = db.carregar_conta(num_conta)
    if conta:
        contas.append(conta)
        alert_observer = ObservadorAlertaTransacao()
        conta.anexar(alert_observer)

    return conta

def transferir_entre_contas():
    # se usuário logado, origem é a conta da sessão
    from services.sessao import usuario_atual as session_user
    sess = session_user()
    acc_origem = sess or input("Conta de origem: ")
    acc_destino = input("Conta de destino: ")

    if acc_origem == acc_destino:
        print("\nNão é possível transferir para a própria conta.\n")
        return

    try:
        quantidade = float(input("Valor da transferência: "))
    except ValueError:
        print("\nValor inválido para transferência.\n")
        return

    origem = procurar_conta(acc_origem)
    destino = procurar_conta(acc_destino)

    if not origem or not destino:
        print("\nConta(s) não encontrada(s).\n")
        return

    if quantidade <= 0:
        print("\nValor inválido para transferência.\n")
        return
    if quantidade > origem.saldo:
        print("\nSaldo insuficiente na conta de origem.\n")
        return

    # confirmação por senha: se sessão, confirme com conta da sessão; caso contrário, peça credenciais da conta de origem
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

    if facade.transferir(origem, destino, quantidade):
        print("\nTransferência realizada com sucesso!\n")
        verificar_alerta(origem)
    else:
        print("\nOperação de transferência falhou.\n")

def ver_historico():
    from services.sessao import usuario_atual as session_user
    acc_num = session_user() or input("Número da conta: ")
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
    from services.sessao import usuario_atual as session_user
    acc_num = session_user() or input("Número da conta: ")
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
    from services.sessao import usuario_atual as session_user
    acc_num = session_user() or input("Número da conta: ")
    conta = procurar_conta(acc_num)
    
    if conta:
        descricao = input("Descrição da conta (ex: Conta de luz): ")
        try:
            valor = float(input("Valor a pagar: "))
        except ValueError:
            print("\nValor inválido para pagamento.\n")
            return

        if valor <= 0:
            print("\nValor inválido para pagamento.\n")
            return
        if valor > conta.saldo:
            print("\nSaldo insuficiente para pagar a conta.\n")
            return

    # confirmação por senha antes de efetivar
        sess = session_user()
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

        if facade.pagar(conta, descricao, valor):
            print("\nPagamento realizado com sucesso!\n")
            verificar_alerta(conta)
        else:
            print("\nOperação de pagamento falhou.\n")
    else:
        print("\nConta não encontrada.\n")

def solicitar_talao_cheques():
    from services.sessao import usuario_atual as session_user
    acc_num = session_user() or input("Número da conta: ")
    conta = procurar_conta(acc_num)
    
    if conta:
        try:
            quantidade = int(input("Quantidade de talões a solicitar (R$15,00 cada): "))
            if quantidade <= 0:
                raise ValueError
        except ValueError:
            print("\nQuantidade inválida. Deve ser um número inteiro positivo.\n")
            return
    # confirmação por senha antes de efetivar pedido de talões
        sess = session_user()
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

        if facade.solicitar_talao(conta, quantidade):
            print(f"\n{quantidade} talão(ões) solicitado(s) com sucesso!\n")
            verificar_alerta(conta)
        else:
            print("\nSaldo insuficiente para solicitar talão.\n")
    else:
        print("\nConta não encontrada.\n")

def suporte_cliente():
    from services.sessao import usuario_atual as session_user
    acc_num = session_user() or input("Número da conta: ")
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
    # exigir login antes de mostrar o menu
    while True:
        print('\n========= AV BANK - LOGIN =========\n')
        print('1 - Entrar')
        print('2 - Criar nova conta')
        print('3 - Esqueci a senha')
        print('4 - Sair')
        opc = input('\nEscolha uma opção: ')
        if opc == '1':
            cpf = input('CPF: ').strip()
            key = f"cpf:{cpf}"
            if esta_bloqueado(key):
                print('\nMuitas tentativas falhas. Tente novamente mais tarde.\n')
                continue
            senha = input('Senha: ')
            # localizar conta pelo CPF
            from database.ger_bd import DBManager
            dbm = DBManager()
            conta = dbm.carregar_conta_por_cpf(cpf)
            if not conta:
                print('\nCPF não encontrado.\n')
                registrar_tentativa_falha(key)
                continue
            num = conta.num_conta
            if verificar_credenciais(num, senha):
                login_session(num)
                print(f"\nBem-vindo, conta {num}! Papel: {current_role()}\n")
                break
            else:
                print('\nCPF ou senha inválidos.\n')
                registrar_tentativa_falha(key)
        elif opc == '2':
            CriarContaCommand(db, procurar_conta).execute()
        elif opc == '3':
            # Esqueci a senha: pedir CPF e reset via pergunta de segurança
            cpf = input('Informe o CPF cadastrado: ')
            if esta_bloqueado(f"cpf:{cpf}"):
                print('\nMuitas tentativas falhas. Tente novamente mais tarde.\n')
                continue
            conta = db.carregar_conta_por_cpf(cpf)
            if not conta:
                print('\nCPF não encontrado.\n')
                continue
            # obter credencial e pergunta
            cred = db.carregar_credencial(conta.num_conta)
            from services.auth import PERGUNTAS_SEGURANCA, verificar_resposta_seguranca, redefinir_senha_por_cpf
            qid = cred.get('sec_question_id') if cred else None
            if not qid:
                print('\nNenhuma pergunta de segurança cadastrada para essa conta. Contate um administrador.\n')
                continue
            pergunta = PERGUNTAS_SEGURANCA.get(qid)
            print(f"Pergunta: {pergunta}")
            resposta = input('Resposta: ')
            if verificar_resposta_seguranca(conta.num_conta, resposta):
                while True:
                    nova = input('Digite a nova senha NUMÉRICA de 6 dígitos: ')
                    try:
                        if redefinir_senha_por_cpf(cpf, nova):
                            print('\nSenha redefinida com sucesso. Faça login com a nova senha.\n')
                            break
                    except Exception as e:
                        print('Erro ao redefinir senha:', e)
                    print('Senha inválida. Deve ser exatamente 6 dígitos numéricos.')
            else:
                print('\nResposta incorreta.\n')
                registrar_tentativa_falha(f"cpf:{cpf}")
        elif opc == '4':
            print('\nEncerrando.\n')
            return
        else:
            print('\nOpção inválida.\n')

    while True:
        usr = current_user()
        role = current_role()
        print("\n========= AV BANK =========\n")
        
        print("--- Gestão da Conta ---")
        print(" 0 - Minha Conta")
        print(" 1 - Ver saldo")
        print(" 2 - Ver histórico de transações")
        print(" 3 - Definir alerta de saldo")
        print(" 4 - Limpar histórico da conta")
        
        print("\n--- Operações Financeiras ---")
        print(" 5 - Depositar")
        print(" 6 - Sacar")
        print(" 7 - Transferir")
        print(" 8 - Pagar conta")

        print("\n--- Produtos e Serviços ---")
        print("9 - Solicitar empréstimo")
        print("10 - Câmbio de moedas")
        print("11 - Aplicar em Investimentos")
        print("12 - Solicitar talão de cheques")

        print("\n--- Sistema e Suporte ---")
        print("13 - Suporte ao Cliente")
        print("14 - Sair")

        opcao = input("\nEscolha uma opção: ")

        if opcao == "1":
            VerSaldoCommand(procurar_conta).execute()
        elif opcao == "0":
            minha_conta()
        
        elif opcao == "2":
            ver_historico()
        elif opcao == "3":
            from services.sessao import usuario_atual as session_user
            num = session_user() or input("Número da conta: ")
            conta = procurar_conta(num)
            if conta:
                try:
                    limite = float(input("Definir alerta se saldo for menor que: R$"))
                except ValueError:
                    print("\nValor inválido. Operação cancelada.\n")
                    continue
                # confirmação por senha no final
                sess = session_user()
                if sess:
                    senha = input("Confirme sua senha (6 dígitos): ")
                    if not verificar_credenciais(sess, senha):
                        print("\nSenha incorreta. Operação cancelada.\n")
                        continue
                else:
                    autor = input("Número da conta autorizadora: ")
                    senha = input("Senha da conta autorizadora (6 dígitos): ")
                    if not verificar_credenciais(autor, senha):
                        print("\nCredenciais inválidas. Operação cancelada.\n")
                        continue

                definir_alerta(conta, limite)
                print(f"\nAlerta definido para a conta {conta.num_conta} com limite de R${limite:.2f}.\n")
            else:
                print("\nConta não encontrada.\n")
                
        elif opcao == "4":
            limpar_historico()
            
        elif opcao == "5":
            DepositarCommand(db, procurar_conta).execute()
            
        elif opcao == "6":
            SacarCommand(db, procurar_conta).execute()
            
        elif opcao == "7":
            transferir_entre_contas()
            
        elif opcao == "8":
            # pagamento_de_conta cuidará da confirmação de senha após validações
            pagamento_de_conta()
            
        elif opcao == "9":
            # solicitar empréstimo: coletar inputs e deixar confirmação por senha na sequência
            from services.sessao import usuario_atual as session_user
            num = session_user() or input("Número da conta: ")
            conta = procurar_conta(num)
            if conta:
                try:
                    valor = float(input("Valor do empréstimo: "))
                except ValueError:
                    print("\nValor inválido.\n")
                    continue
                # pedir confirmação por senha antes de efetivar
                sess = session_user()
                if sess:
                    senha = input("Confirme sua senha (6 dígitos): ")
                    if not verificar_credenciais(sess, senha):
                        print("\nSenha incorreta. Operação cancelada.\n")
                        continue
                else:
                    autor = input("Número da conta autorizadora: ")
                    senha = input("Senha da conta autorizadora (6 dígitos): ")
                    if not verificar_credenciais(autor, senha):
                        print("\nCredenciais inválidas. Operação cancelada.\n")
                        continue

                solicitar_emprestimo(conta, valor)
                salvar_transacao(conta.num_conta, conta.historico[-1])
                db.salvar_conta(conta)
                print("\nEmpréstimo realizado.\n")
            else:
                print("\nConta não encontrada.\n")
                
        elif opcao == "10":
            # câmbio: coletar inputs primeiro, depois pedir confirmação por senha
            from services.sessao import usuario_atual as session_user
            num = session_user() or input("Número da conta: ")
            conta = procurar_conta(num)
            if conta:
                while True:
                    moeda = input("Para qual moeda (USD, EUR, JPY): ").upper()
                    if moeda in ["USD", "EUR", "JPY"]:
                        break
                    print("\nMoeda inválida. Por favor, escolha entre USD, EUR ou JPY.\n")

                try:
                    valor = float(input("Valor em R$: "))
                except ValueError:
                    print("\nValor inválido.\n")
                    continue

                # pedir confirmação por senha antes de efetivar
                sess = session_user()
                if sess:
                    senha = input("Confirme sua senha (6 dígitos): ")
                    if not verificar_credenciais(sess, senha):
                        print("\nSenha incorreta. Operação cancelada.\n")
                        continue
                else:
                    autor = input("Número da conta autorizadora: ")
                    senha = input("Senha da conta autorizadora (6 dígitos): ")
                    if not verificar_credenciais(autor, senha):
                        print("\nCredenciais inválidas. Operação cancelada.\n")
                        continue

                valor_convertido = cambio(conta, moeda, valor)
                
                if valor_convertido is not None:
                    salvar_transacao(conta.num_conta, conta.historico[-1])
                    db.salvar_conta(conta)
                    print(f"\nOperação realizada com sucesso! Valor convertido: {valor_convertido:.2f} {moeda}\n")
                else:
                    print("\nOperação de câmbio falhou.\n")
            else:
                print("\nConta não encontrada.\n")
                
        elif opcao == "11":
            AplicarInvestimentoCommand(db, procurar_conta).execute()
        elif opcao == "12":
            solicitar_talao_cheques()
        elif opcao == "13":
            suporte_cliente()
        elif opcao == "14":
            logout_session()
            print('\nSessão encerrada. Voltando para o login.\n')
            return
        else:
            os.system('cls')
            print("\nOpção inválida!\n")
            

def minha_conta():
    from services.sessao import usuario_atual as session_user
    from services.auth import verificar_credenciais
    acc_num = session_user()
    if not acc_num:
        print("\nNenhuma sessão ativa. Faça login primeiro.\n")
        return
    # pedir senha para confirmar acesso
    senha = input("Confirme sua senha (6 dígitos) para acessar 'Minha Conta': ")
    if not verificar_credenciais(acc_num, senha):
        print("\nSenha incorreta. Acesso negado.\n")
        return
    conta = procurar_conta(acc_num)
    if conta:
        print("\n--- Minha Conta ---")
        print(f"Titular: {conta.proprietario.nome}")
        print(f"CPF: {conta.proprietario.cpf}")
        print(f"Número da conta: {conta.num_conta}")
        # imprimir contatos se disponíveis
        if hasattr(conta.proprietario, 'endereco') and conta.proprietario.endereco:
            print(f"Endereço: {conta.proprietario.endereco}")
        if hasattr(conta.proprietario, 'telefone') and conta.proprietario.telefone:
            print(f"Telefone: {conta.proprietario.telefone}")
        if hasattr(conta.proprietario, 'email') and conta.proprietario.email:
            print(f"E-mail: {conta.proprietario.email}")
        print()
    else:
        print("\nConta não encontrada.\n")


if __name__ == "__main__":
    db = DBManager()
    db.criar_tabelas()
    criar_tabela_transacoes()
    menu()
