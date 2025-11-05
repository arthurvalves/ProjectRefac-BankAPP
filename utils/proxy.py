import time
from typing import Dict


class ProxyCacheCambio:
    def __init__(self, fornecedor, ttl_segundos: int = 300):
        self.fornecedor = fornecedor
        self.ttl = ttl_segundos
        self.cache: Dict[str, tuple] = {}

    def obter_taxa(self, moeda: str) -> float:
        chave = moeda.upper()
        entrada = self.cache.get(chave)
        agora = time.time()
        
        if entrada:
            taxa, ts = entrada
            if agora - ts < self.ttl:
                return taxa
            
        taxa = self.fornecedor.obter_taxa(moeda)
        self.cache[chave] = (taxa, agora)
        return taxa
    
CambioCacheProxy = ProxyCacheCambio

__all__ = ['ProxyCacheCambio', 'CambioCacheProxy']
