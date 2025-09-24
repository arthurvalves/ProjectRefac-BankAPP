class UserBuilder:
    def __init__(self):
        self._nome = None
        self._cpf = None
        self._endereco = None
        self._telefone = None
        self._email = None

    def set_nome(self, nome):
        self._nome = nome
        return self

    def set_cpf(self, cpf):
        self._cpf = cpf
        return self

    def set_endereco(self, endereco):
        self._endereco = endereco
        return self

    def set_telefone(self, telefone):
        self._telefone = telefone
        return self

    def set_email(self, email):
        self._email = email
        return self

    def build(self):
        if not self._nome or not self._cpf:
            raise ValueError("Nome e CPF são obrigatórios!")
        user = User(self._nome, self._cpf)
        user.endereco = self._endereco
        user.telefone = self._telefone
        user.email = self._email
        return user

from models.user import User
