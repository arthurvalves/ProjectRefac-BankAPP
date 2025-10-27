from abc import ABC, abstractmethod


class IFornecedorCambio(ABC):
    @abstractmethod
    def obter_taxa(self, moeda: str) -> float:
        raise NotImplementedError()
