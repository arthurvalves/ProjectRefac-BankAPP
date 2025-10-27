from .fornecedor_cambio import IFornecedorCambio
from . import cambio_api

ICambioProvider = IFornecedorCambio

class AdaptadorBCB(IFornecedorCambio):

    def obter_taxa(self, moeda: str) -> float:
        tabela = {
            'USD': 5.4456,
            'EUR': 6.1234,
            'GBP': 7.1234,
        }

        taxa = tabela.get(moeda.upper())
        if taxa is not None:
            return taxa
        try:
            taxa_api = cambio_api.get_cambio(moeda)
        except Exception:
            taxa_api = None

        return taxa_api if taxa_api is not None else 1.0

BCBAdapter = AdaptadorBCB

__all__ = ['IFornecedorCambio', 'ICambioProvider', 'AdaptadorBCB', 'BCBAdapter']
