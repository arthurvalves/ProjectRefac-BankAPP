from datetime import datetime

class Transacao:
    def __init__(self, tipo, valor, data=None, descricao=""):
        self.tipo = tipo
        self.valor = valor
        self.data = data or datetime.now()
        self.descricao = descricao

    def __str__(self):
        return f"{self.tipo}: R${self.valor:.2f} em {self.data:%d/%m/%Y %H:%M} - {self.descricao}"
