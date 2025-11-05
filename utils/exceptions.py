
from typing import Optional, Dict, Any


class AppError(Exception):

    def __init__(self, message: str, code: Optional[str] = None, details: Optional[Dict[str, Any]] = None,
                 original_exception: Optional[Exception] = None):
        super().__init__(message)
        self.message = message
        self.code = code
        self.details = details or {}
        self.original_exception = original_exception

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.__class__.__name__,
            "message": self.message,
            "code": self.code,
            "details": self.details,
        }

    def __str__(self) -> str:  
        if self.code:
            return f"{self.__class__.__name__}({self.code}): {self.message}"
        return f"{self.__class__.__name__}: {self.message}"


class ValidationError(AppError):
    """Erros de validação de entrada/negócio."""


class AuthError(AppError):
    """Falha de autenticação/autorizaçãO."""


class NotFoundError(AppError):
    """Recurso não encontrado (conta, usuário, transação)."""


class DBError(AppError):
    """Erro vindo da camada de persistência/DB."""


class TransactionError(AppError):
    """Problema em operação transacional que requer rollback."""


class InsufficientFundsError(AppError):
    """Saldo insuficiente para operação financeira."""


class ExternalAPIError(AppError):
    """Falha ao chamar API externa (rede, timeout, resposta inválida)."""


class ConcurrencyError(AppError):
    """Conflitos de concorrência ou versão (optimistic/pessimistic locking)."""


class FileError(AppError):
    """Erros de I/O em arquivos (logs, imports, exports)."""


class RetryableError(AppError):
    """Marca uma operação como passível de retry (ex.: timeout temporário)."""


def wrap_exception(exc: Exception, cls: type = AppError, message: Optional[str] = None, **kwargs) -> AppError:
    """Envolve uma exceção externa em uma AppError.

    Exemplo:
        try:
            cur.execute(sql)
        except sqlite3.Error as e:
            raise wrap_exception(e, DBError, "Erro DB ao executar query", details={"sql": sql})
    """
    msg = message or str(exc)
    return cls(msg, original_exception=exc, **{k: v for k, v in kwargs.items()})


__all__ = [
    "AppError",
    "ValidationError",
    "AuthError",
    "NotFoundError",
    "DBError",
    "TransactionError",
    "InsufficientFundsError",
    "ExternalAPIError",
    "ConcurrencyError",
    "FileError",
    "RetryableError",
    "wrap_exception",
]
