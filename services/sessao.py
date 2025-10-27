_sessao_atual = {
    'num_conta': None,
    'role': None
}


def logar_sessao(num_conta: str, role: str = 'usuario'):
    _sessao_atual['num_conta'] = num_conta
    _sessao_atual['role'] = role


def deslogar_sessao():
    _sessao_atual['num_conta'] = None
    _sessao_atual['role'] = None


def usuario_atual():
    return _sessao_atual['num_conta']


def papel_atual():
    return _sessao_atual['role']


def exige_papel(necessario: str):
    def decorator(func):
        def wrapper(*args, **kwargs):
            if _sessao_atual['role'] != necessario:
                raise PermissionError('Ação requer papel: %s' % necessario)
            return func(*args, **kwargs)
        return wrapper
    return decorator
