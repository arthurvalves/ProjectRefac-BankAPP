from database.ger_bd import DBManager
from database.ger_transacao_bd import salvar_transacao
from utils.exceptions import (
    ValidationError,
    InsufficientFundsError,
    AuthError,
    ExternalAPIError,
    NotFoundError,
    DBError,
)
import logging

logger = logging.getLogger(__name__)


class FachadaBanco:
    def __init__(self):
        self.db = DBManager()

    def depositar(self, conta, quantidade: float):
        try:
            conta.deposito(quantidade)
            # persiste transação e conta
            if conta.historico:
                salvar_transacao(conta.num_conta, conta.historico[-1])
            self.db.salvar_conta(conta)
        except (ValidationError, DBError) as e:
            logger.info("depositar falhou: %s", e)
            return False

    def sacar(self, conta, quantidade: float) -> bool:
        try:
            ok = conta.saque(quantidade)
            if ok:
                if conta.historico:
                    salvar_transacao(conta.num_conta, conta.historico[-1])
                self.db.salvar_conta(conta)
            return ok
        except (InsufficientFundsError, ValidationError, DBError) as e:
            logger.info("sacar falhou: %s", e)
            return False

    def transferir(self, origem, destino, quantidade: float) -> bool:
        try:
            ok = origem.transferir_para(destino, quantidade)
            if ok:
                # registrar transações mais recentes de ambas as contas
                if origem.historico:
                    salvar_transacao(origem.num_conta, origem.historico[-1])
                if destino.historico:
                    salvar_transacao(destino.num_conta, destino.historico[-1])
                self.db.salvar_conta(origem)
                self.db.salvar_conta(destino)
            return ok
        except (InsufficientFundsError, ValidationError, DBError) as e:
            logger.info("transferir falhou: %s", e)
            return False

    def pagar(self, conta, descricao: str, valor: float) -> bool:
        try:
            ok = conta.pagar(descricao, valor)
            if ok:
                if conta.historico:
                    salvar_transacao(conta.num_conta, conta.historico[-1])
                self.db.salvar_conta(conta)
            return ok
        except (InsufficientFundsError, ValidationError, DBError) as e:
            logger.info("pagar falhou: %s", e)
            return False

    def solicitar_talao(self, conta, quantidade: int) -> bool:
        try:
            ok = conta.solicitar_talao(quantidade)
            if ok:
                if conta.historico:
                    salvar_transacao(conta.num_conta, conta.historico[-1])
                self.db.salvar_conta(conta)
            return ok
        except (ValidationError, DBError) as e:
            logger.info("solicitar_talao falhou: %s", e)
            return False
