import hashlib
import os
import binascii
import time
from database.ger_bd import DBManager

_tentativas_falhas = {}  # chave -> [contador, ts_primeira]
MAX_TENTATIVAS = 3
LOCK_SEGUNDOS = 300


def _hash_senha(senha: str, salt: bytes = None):
    if salt is None:
        salt = os.urandom(16)
    pwdhash = hashlib.pbkdf2_hmac('sha256', senha.encode('utf-8'), salt, 100000)
    return binascii.hexlify(salt).decode('ascii'), binascii.hexlify(pwdhash).decode('ascii')


def senha_valida(senha: str) -> bool:
    return isinstance(senha, str) and len(senha) == 6 and senha.isdigit()


def registrar_credenciais(num_conta: str, senha: str, papel: str = 'usuario'):
    db = DBManager()
    if not senha_valida(senha):
        raise ValueError('Senha inválida. Deve conter exatamente 6 dígitos numéricos.')
    salt_hex, pwdhash_hex = _hash_senha(senha)
    senha_hash = f"{salt_hex}${pwdhash_hex}"
    db.salvar_credencial(num_conta, senha_hash=senha_hash, role=papel)


def verificar_credenciais(num_conta: str, senha: str) -> bool:
    chave = f"conta:{num_conta}"
    if esta_bloqueado(chave):
        return False
    db = DBManager()
    cred = db.carregar_credencial(num_conta)
    if not cred or not cred.get('senha_hash'):
        registrar_tentativa_falha(chave)
        return False
    try:
        salt_hex, hash_hex = cred['senha_hash'].split('$')
        salt = binascii.unhexlify(salt_hex)
        _, tentada = _hash_senha(senha, salt)
        ok = tentada == hash_hex
        if not ok:
            registrar_tentativa_falha(chave)
        else:
            resetar_tentativas_falha(chave)
        return ok
    except Exception:
        registrar_tentativa_falha(chave)
        return False


def get_role(num_conta: str):
    db = DBManager()
    cred = db.carregar_credencial(num_conta)
    if cred:
        return cred.get('role', 'usuario')
    return None


# Perguntas de segurança
PERGUNTAS_SEGURANCA = {
    1: "Qual o nome da sua cidade natal?",
    2: "Qual é o nome do seu primeiro animal de estimação?",
    3: "Qual é o primeiro nome da sua mãe?",
    4: "Qual escola você frequentou no ensino fundamental?",
    5: "Qual foi o modelo do seu primeiro carro?"
}


def definir_pergunta_seguranca(num_conta: str, pergunta_id: int, resposta: str):
    if pergunta_id not in PERGUNTAS_SEGURANCA:
        raise ValueError('Pergunta inválida')
    db = DBManager()
    salt_hex, ans_hash = _hash_senha(resposta)
    combinado = f"{salt_hex}${ans_hash}"
    cred = db.carregar_credencial(num_conta) or {}
    senha_hash = cred.get('senha_hash')
    papel = cred.get('role', 'usuario')
    db.salvar_credencial(num_conta, senha_hash=senha_hash, role=papel, sec_question_id=pergunta_id, sec_answer_hash=combinado)


def verificar_resposta_seguranca(num_conta: str, resposta: str) -> bool:
    chave = f"seg:{num_conta}"
    if esta_bloqueado(chave):
        return False
    db = DBManager()
    cred = db.carregar_credencial(num_conta)
    if not cred or not cred.get('sec_answer_hash'):
        registrar_tentativa_falha(chave)
        return False
    try:
        salt_hex, hash_hex = cred['sec_answer_hash'].split('$')
        salt = binascii.unhexlify(salt_hex)
        _, tentada = _hash_senha(resposta, salt)
        ok = tentada == hash_hex
        if not ok:
            registrar_tentativa_falha(chave)
        else:
            resetar_tentativas_falha(chave)
        return ok
    except Exception:
        registrar_tentativa_falha(chave)
        return False


def redefinir_senha_por_cpf(cpf: str, nova_senha: str) -> bool:
    db = DBManager()
    conta = db.carregar_conta_por_cpf(cpf)
    if not conta:
        return False
    num_conta = conta.num_conta
    if not senha_valida(nova_senha):
        raise ValueError('Senha inválida. Deve conter exatamente 6 dígitos numéricos.')
    salt_hex, pwdhash_hex = _hash_senha(nova_senha)
    senha_hash = f"{salt_hex}${pwdhash_hex}"
    cred = db.carregar_credencial(num_conta) or {}
    papel = cred.get('role', 'usuario')
    sec_q = cred.get('sec_question_id')
    sec_ans = cred.get('sec_answer_hash')
    db.salvar_credencial(num_conta, senha_hash=senha_hash, role=papel, sec_question_id=sec_q, sec_answer_hash=sec_ans)
    return True


def registrar_tentativa_falha(chave: str):
    agora = int(time.time())
    entry = _tentativas_falhas.get(chave)
    if not entry:
        _tentativas_falhas[chave] = [1, agora]
        return
    contador, ts = entry
    if agora - ts > LOCK_SEGUNDOS:
        _tentativas_falhas[chave] = [1, agora]
        return
    _tentativas_falhas[chave][0] = contador + 1


def esta_bloqueado(chave: str) -> bool:
    entry = _tentativas_falhas.get(chave)
    if not entry:
        return False
    contador, ts = entry
    agora = int(time.time())
    if agora - ts > LOCK_SEGUNDOS:
        del _tentativas_falhas[chave]
        return False
    return contador >= MAX_TENTATIVAS


def resetar_tentativas_falha(chave: str):
    if chave in _tentativas_falhas:
        del _tentativas_falhas[chave]


register_credentials = registrar_credenciais
verify_credentials = verificar_credenciais
is_valid_password = senha_valida
get_role_passthrough = get_role
SECURITY_QUESTIONS = PERGUNTAS_SEGURANCA
set_security_question = definir_pergunta_seguranca
verify_security_answer = verificar_resposta_seguranca
reset_password_by_cpf = redefinir_senha_por_cpf
record_failed_attempt = registrar_tentativa_falha
is_locked = esta_bloqueado

def get_role(num_conta: str):
    try:
        return get_role_passthrough(num_conta)
    except Exception:
        return None

__all__ = [
    'registrar_credenciais', 'verificar_credenciais', 'get_role', 'senha_valida',
    'definir_pergunta_seguranca', 'verificar_resposta_seguranca', 'redefinir_senha_por_cpf',
    'registrar_tentativa_falha', 'esta_bloqueado', 'resetar_tentativas_falha', 'PERGUNTAS_SEGURANCA',
    # english aliases
    'register_credentials', 'verify_credentials', 'get_role_passthrough', 'is_valid_password',
    'SECURITY_QUESTIONS', 'set_security_question', 'verify_security_answer', 'reset_password_by_cpf',
    'record_failed_attempt', 'is_locked'
]
