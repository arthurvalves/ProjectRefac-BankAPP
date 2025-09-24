
import sqlite3
import os
from models.transaction import Transacao
from datetime import datetime

def conectar():
    os.makedirs("data", exist_ok=True)
    return sqlite3.connect("data/db.sqlite")

def criar_tabela_transacoes():
    with conectar() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS transacoes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                num_conta TEXT,
                tipo TEXT,
                valor REAL,
                data TEXT,
                descricao TEXT
            )
        """)
        conn.commit()

def salvar_transacao(num_conta, transacao: Transacao):
    with conectar() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO transacoes (num_conta, tipo, valor, data, descricao)
            VALUES (?, ?, ?, ?, ?)
        """, (
            num_conta,
            transacao.tipo,
            transacao.valor,
            transacao.data.isoformat(),
            transacao.descricao
        ))
        conn.commit()

def carregar_transacoes(num_conta):
    transacoes = []
    with conectar() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT tipo, valor, data, descricao
            FROM transacoes
            WHERE num_conta = ?
            ORDER BY data
        """, (num_conta,))
        linhas = cursor.fetchall()
        for tipo, valor, data, descricao in linhas:
            transacoes.append(Transacao(tipo, valor, datetime.fromisoformat(data), descricao))
    return transacoes

def deletar_transacoes(num_conta):
    with conectar() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM transacoes WHERE num_conta = ?", (num_conta,))
        conn.commit()

