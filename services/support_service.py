import os
from datetime import datetime

def registrar_suporte(num_conta, mensagem):
    os.makedirs("data/suporte", exist_ok=True)
    caminho = f"data/suporte/{num_conta}.txt"
    with open(caminho, "a", encoding="utf-8") as arquivo:
        timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        arquivo.write(f"[{timestamp}] {mensagem}\n")

def listar_mensagens(num_conta):
    caminho = f"data/suporte/{num_conta}.txt"
    if os.path.exists(caminho):
        with open(caminho, "r", encoding="utf-8") as arquivo:
            return arquivo.readlines()
    return None
