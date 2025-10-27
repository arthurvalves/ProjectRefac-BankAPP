from services.auth import (
    registrar_credenciais as register_credentials,
    verificar_credenciais as verify_credentials,
    get_role as get_role_passthrough,
    senha_valida as is_valid_password,
    PERGUNTAS_SEGURANCA as SECURITY_QUESTIONS,
    definir_pergunta_seguranca as set_security_question,
    verificar_resposta_seguranca as verify_security_answer,
    redefinir_senha_por_cpf as reset_password_by_cpf,
    registrar_tentativa_falha as record_failed_attempt,
    esta_bloqueado as is_locked
)

def get_role(num_conta: str):
    try:
        return get_role_passthrough(num_conta)
    except Exception:
        return None

