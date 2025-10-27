from abc import ABC, abstractmethod

class Observavel(ABC):
    def __init__(self):
        self._observadores = []

    @abstractmethod
    def anexar(self, observador):
        pass

    @abstractmethod
    def desanexar(self, observador):
        pass

    @abstractmethod
    def notificar(self):
        pass


class Observador(ABC):
    @abstractmethod
    def update(self, sujeito):
        pass


class ObservadorAlertaTransacao(Observador): 
    def update(self, sujeito):
        ultima_transacao = sujeito.historico[-1] if sujeito.historico else None
        if ultima_transacao:
            if ultima_transacao.tipo == "Transferência recebida":
                nome_remetente = "Remetente"
                try:
                    nome_remetente = ultima_transacao.descricao.split("De: ")[1].split(" (")[0]
                except IndexError:
                    pass  
                print(f"\n[NOVA TRANSAÇÃO] {nome_remetente} enviou R${ultima_transacao.valor:.2f} para você.\n")

            elif ultima_transacao.tipo == "Depósito":
                print(f"\n[NOVA TRANSAÇÃO] Um depósito de R${ultima_transacao.valor:.2f} foi realizado na sua conta.\n")
            