from datetime import datetime

class Transacao:
    def __init__(self, tipo, valor, data=None, descricao="", simbolo_moeda="R$"):
        self.tipo = tipo
        self.valor = valor
        self.data = data or datetime.now()
        self.descricao = descricao
        self.simbolo_moeda = simbolo_moeda

    def __str__(self):
        return f"{self.tipo}: {self.simbolo_moeda}{self.valor:.2f} em {self.data:%d/%m/%Y %H:%M} - {self.descricao}"
