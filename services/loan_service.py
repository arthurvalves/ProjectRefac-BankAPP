from models.transaction import Transacao

def solicitar_emprestimo(conta, valor):
    conta.deposito(valor)
    conta.historico.append(Transacao("Empréstimo", valor))

def aplicar_investimento(conta, valor, meses, tipo):
    planos = {
        "poupanca": 0.0065,
        "cdb": 0.009,
        "tesouro": 0.0075
    }

    taxa = planos.get(tipo.lower())
    if taxa is None:
        print("Tipo de investimento inválido.")
        return None

    montante = valor * ((1 + taxa) ** meses)

    if conta.saque(valor):
        conta.historico.append(
            Transacao(
                f"Investimento - {tipo.capitalize()}",
                valor,
                descricao=f"{meses} meses @ {taxa*100:.2f}% a.m. → Retorno estimado: R${montante:.2f}"
            )
        )
        return montante
    else:
        print("Saldo insuficiente para aplicar.")
        return None
