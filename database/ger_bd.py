import sqlite3
import os
from models.user import User
from models.conta import Conta
from models.transacoes import Transacao
from database.ger_transacao_bd import (
    criar_tabela_transacoes,
    salvar_transacao,
    carregar_transacoes
)

class DBManager:
    _instance = None
    _connection = None

    def __new__(cls): 
        if cls._instance is None:
            cls._instance = super(DBManager, cls).__new__(cls)
            cls._instance._init_connection()
        return cls._instance




    def _init_connection(self):
        os.makedirs("data", exist_ok=True)
        self._connection = sqlite3.connect("data/db.sqlite")

    def get_connection(self):
        return self._connection

    def criar_tabelas(self):
        cursor = self._connection.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS contas (
                num_conta TEXT PRIMARY KEY,
                nome TEXT,
                cpf TEXT,
                saldo REAL
            )
        """)
        self._connection.commit()
        criar_tabela_transacoes()

    def salvar_conta(self, conta):
        cursor = self._connection.cursor()
        cursor.execute(
            "INSERT OR REPLACE INTO contas (num_conta, nome, cpf, saldo) VALUES (?, ?, ?, ?)",
            (conta.num_conta, conta.proprietario.nome, conta.proprietario.cpf, conta.saldo)
        )
        self._connection.commit()
        #for transacao in conta.historico:
        #    salvar_transacao(conta.num_conta, transacao)

    def carregar_conta(self, num_conta):
        cursor = self._connection.cursor()
        cursor.execute("SELECT num_conta, nome, cpf, saldo FROM contas WHERE num_conta = ?", (num_conta,))
        row = cursor.fetchone()
        if row:
            user = User(row[1], row[2])
            conta = Conta(row[0], user, row[3])
            conta.historico = carregar_transacoes(row[0])
            return conta
        return None
