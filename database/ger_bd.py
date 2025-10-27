import sqlite3
import os
import json
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
                saldo REAL,
                saldos_estrangeiros TEXT
            )
        """)
        # tabela de credenciais: separada da tabela de contas
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS credenciais (
                num_conta TEXT PRIMARY KEY,
                senha_hash TEXT,
                role TEXT,
                sec_question_id INTEGER,
                sec_answer_hash TEXT
            )
        """)
        # Garantir colunas (migração simples para bancos antigos)
        cursor.execute("PRAGMA table_info(credenciais)")
        cols = [r[1] for r in cursor.fetchall()]
        # se colunas estiverem faltando, adicionar via ALTER TABLE
        if 'sec_question_id' not in cols:
            cursor.execute("ALTER TABLE credenciais ADD COLUMN sec_question_id INTEGER")
        if 'sec_answer_hash' not in cols:
            cursor.execute("ALTER TABLE credenciais ADD COLUMN sec_answer_hash TEXT")
        # garantir coluna saldos_estrangeiros em contas para versões antigas
        cursor.execute("PRAGMA table_info(contas)")
        conta_cols = [r[1] for r in cursor.fetchall()]
        if 'saldos_estrangeiros' not in conta_cols:
            cursor.execute("ALTER TABLE contas ADD COLUMN saldos_estrangeiros TEXT DEFAULT '{}' ")
        self._connection.commit()
        criar_tabela_transacoes()

    def salvar_conta(self, conta):
        cursor = self._connection.cursor()
        saldos_json = json.dumps(conta.saldos_estrangeiros or {})
        cursor.execute(
            "INSERT OR REPLACE INTO contas (num_conta, nome, cpf, saldo, saldos_estrangeiros) VALUES (?, ?, ?, ?, ?)",
            (conta.num_conta, conta.proprietario.nome, conta.proprietario.cpf, conta.saldo, saldos_json)
        )
        self._connection.commit()
        #for transacao in conta.historico:
        #    salvar_transacao(conta.num_conta, transacao)

    def carregar_conta(self, num_conta):
        cursor = self._connection.cursor()
        cursor.execute("SELECT num_conta, nome, cpf, saldo, saldos_estrangeiros FROM contas WHERE num_conta = ?", (num_conta,))
        row = cursor.fetchone()
        if row:
            user = User(row[1], row[2])
            conta = Conta(row[0], user, row[3])
            # carregar saldos estrangeiros se presente
            try:
                conta.saldos_estrangeiros = json.loads(row[4]) if row[4] else {}
            except Exception:
                conta.saldos_estrangeiros = {}
            conta.historico = carregar_transacoes(row[0])
            return conta
        return None

    def carregar_conta_por_cpf(self, cpf):
        cursor = self._connection.cursor()
        cursor.execute("SELECT num_conta, nome, cpf, saldo, saldos_estrangeiros FROM contas WHERE cpf = ?", (cpf,))
        row = cursor.fetchone()
        if row:
            user = User(row[1], row[2])
            conta = Conta(row[0], user, row[3])
            try:
                conta.saldos_estrangeiros = json.loads(row[4]) if row[4] else {}
            except Exception:
                conta.saldos_estrangeiros = {}
            conta.historico = carregar_transacoes(row[0])
            return conta
        return None

    # Credenciais
    def salvar_credencial(self, num_conta, senha_hash=None, role='user', sec_question_id=None, sec_answer_hash=None):
        cursor = self._connection.cursor()
        cursor.execute(
            "INSERT OR REPLACE INTO credenciais (num_conta, senha_hash, role, sec_question_id, sec_answer_hash) VALUES (?, ?, ?, ?, ?)",
            (num_conta, senha_hash, role, sec_question_id, sec_answer_hash)
        )
        self._connection.commit()

    def carregar_credencial(self, num_conta):
        cursor = self._connection.cursor()
        cursor.execute("SELECT senha_hash, role, sec_question_id, sec_answer_hash FROM credenciais WHERE num_conta = ?", (num_conta,))
        row = cursor.fetchone()
        if row:
            return {'senha_hash': row[0], 'role': row[1], 'sec_question_id': row[2], 'sec_answer_hash': row[3]}
        return None

    def deletar_credencial(self, num_conta):
        cursor = self._connection.cursor()
        cursor.execute("DELETE FROM credenciais WHERE num_conta = ?", (num_conta,))
        self._connection.commit()
