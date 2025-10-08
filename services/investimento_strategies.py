from abc import ABC, abstractmethod

class InvestimentoStrategy(ABC):
    @abstractmethod
    def calcular_retorno(self, valor, meses):
        pass

class CDBStrategy(InvestimentoStrategy):
    def calcular_retorno(self, valor, meses):
        taxa_mensal = 0.0090
        return valor * ((1 + taxa_mensal) ** meses - 1)

class TesouroDiretoStrategy(InvestimentoStrategy):
    def calcular_retorno(self, valor, meses):
        taxa_mensal = 0.0075 
        return valor * ((1 + taxa_mensal) ** meses - 1)