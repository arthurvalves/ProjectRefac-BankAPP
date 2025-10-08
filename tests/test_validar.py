import pytest
from utils.validacao import validar_nome, validar_cpf, validar_telefone, validar_email

def test_validar_nome():
    assert validar_nome("João da Silva")
    assert not validar_nome("João123")
    assert not validar_nome("")

def test_validar_cpf():
    assert validar_cpf("52998224725")  # CPF válido
    assert not validar_cpf("11111111111")  # Inválido
    assert not validar_cpf("1234567890")  # Menor que 11

def test_validar_telefone():
    assert validar_telefone("(82)99999-1234")
    assert validar_telefone("82999991234")
    assert not validar_telefone("9999")

def test_validar_email():
    assert validar_email("teste@email.com")
    assert not validar_email("teste@email")
    assert not validar_email("teste.com")
