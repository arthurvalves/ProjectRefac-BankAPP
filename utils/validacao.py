import re
import random
from database.ger_bd import DBManager

def validar_nome(nome):
    return bool(re.fullmatch(r'[A-Za-zÀ-ÿ ]+', nome))

def validar_cpf(cpf):
    """Valida um CPF básico:
    - remove caracteres não numéricos
    - rejeita sequências com todos dígitos iguais
    - calcula os dois dígitos verificadores
    """
    cpf = re.sub(r'\D', '', cpf)
    if len(cpf) != 11:
        return False
    # rejeita sequências como 11111111111, 00000000000, etc.
    if cpf == cpf[0] * 11:
        return False

    def calc_digit(cpf_part):
        soma = 0
        peso = len(cpf_part) + 1
        for ch in cpf_part:
            soma += int(ch) * peso
            peso -= 1
        resto = soma % 11
        return '0' if resto < 2 else str(11 - resto)

    d1 = calc_digit(cpf[:9])
    d2 = calc_digit(cpf[:9] + d1)
    return cpf[-2:] == d1 + d2

def validar_telefone(telefone):
    telefone = re.sub(r'\D', '', telefone)
    return len(telefone) >= 10 and len(telefone) <= 11

def validar_email(email):
    return bool(re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email))

def gerar_numero_conta():
    db = DBManager()
    cursor = db.get_connection().cursor()
    while True:
        numero = str(random.randint(10000000, 99999999))
        cursor.execute("SELECT 1 FROM contas WHERE num_conta = ?", (numero,))
        if not cursor.fetchone():
            return numero

