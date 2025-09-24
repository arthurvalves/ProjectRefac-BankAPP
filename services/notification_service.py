def definir_alerta(conta, limite):
    conta.alerta_saldo = limite

def verificar_alerta(conta):
    if conta.alerta_saldo is not None and conta.saldo < conta.alerta_saldo:
        print(f"[ALERTA] Saldo de {conta.num_conta} abaixo de R${conta.alerta_saldo:.2f}!")
