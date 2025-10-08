from models.transacoes import Transacao
from .investimento_strategies import InvestimentoStrategy

def solicitar_emprestimo(conta, valor):
    if valor > 0:
        conta.deposito(valor)
        descricao = f"Empréstimo de R${valor:.2f} solicitado e creditado."
        conta.historico.append(Transacao("Empréstimo", valor, descricao=descricao))
        return True
    return False

def aplicar_investimento(conta, valor, meses, estrategia: InvestimentoStrategy):
    if valor <= 0 or meses <= 0:
        print("\nValor e prazo devem ser positivos.\n")
        return None

    if conta.saldo >= valor:
        conta.saldo -= valor
        retorno = estrategia.calcular_retorno(valor, meses)
        descricao = f"Aplicação de R${valor:.2f} por {meses} meses"
        conta.historico.append(Transacao("Investimento", -valor, descricao=descricao))
        return retorno
    else:
        print("\nSaldo insuficiente para realizar o investimento.\n")
        return None