import re
import random
from database.ger_bd import DBManager

def validar_nome(nome):
    return bool(re.fullmatch(r'[A-Za-zÀ-ÿ ]+', nome))

def validar_cpf(cpf):
    cpf = re.sub(r'\D', '', cpf)
    return len(cpf) == 11

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

