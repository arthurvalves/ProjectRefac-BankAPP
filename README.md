
# 🏦 Banking Application - AV Bank

Este é um sistema refatorado de **gerenciamento bancário**, desenvolvido em Python como parte da disciplina de Projeto de Software.

Além disso, foi projetado utilizando **padrões de projeto criacionais** (Singleton, Factory Method e Builder), garantindo melhor organização, reuso e extensibilidade do código.

---

## ✅ Funcionalidades implementadas

* ✅ **Cadastro de usuários** (nome, CPF, telefone e e-mail com validação)
* ✅ **Cadastro de contas** (corrente ou poupança, com escolha de moeda)
* ✅ **Listagem de contas e usuários**
* ✅ **Depósito e saque** (com validação de saldo e permissões)
* ✅ **Transferência entre contas** (somente contas da mesma moeda)
* ✅ **Pagamento de boletos**
* ✅ **Validação de dados** (nome, CPF com 11 dígitos, telefone, e-mail)
* ✅ **Persistência em banco de dados SQLite**
* ✅ **Testes automatizados com pytest** (para validação e operações básicas)


---

## 📚 Estrutura do Código

### 🧱 Classes e módulos principais

* `models/account.py`: modelo de conta bancária
* `models/user.py`: modelo de usuário
* `models/account_factory.py`: Factory Method para criação de contas
* `models/user_builder.py`: Builder para criação de usuários
* `database/db_manager.py`: Singleton para conexão e operações no banco de dados
* `services/account_service.py`: operações de conta (depósito, saque, transferência, boleto)
* `utils/validation.py`: validações de dados de entrada
* `main.py`: interface principal (menu de interação com o sistema)

### 🔧 Funções principais

* `cadastrar_usuario()`
* `cadastrar_conta()`
* `listar_usuarios()`
* `listar_contas()`
* `depositar()`
* `sacar()`
* `transferir()`
* `pagar_boleto()`
* `menu()` – interface principal

---

## 📌 Modelagem dos dados

A modelagem é simples, modular e orientada a objetos, com cada classe encapsulando seus atributos e comportamentos.

* **Usuário**

  * Nome
  * CPF
  * Telefone
  * E-mail

* **Conta**

  * Número da conta
  * Tipo (Corrente/Poupança)
  * Saldo
  * Moeda
  * Usuário associado

## 🛠️ Desenvolvimentos futuros

* [ ] **Interface gráfica** para facilitar a interação do usuário.
* [ ] **Sistema de login** com autenticação segura e gerenciamento de credenciais.
* [ ] **Módulo de investimentos** com suporte a:

  * [ ] Poupança
  * [ ] CDB
  * [ ] FIIs
  * [ ] Ações
* [ ] **Gestão de permissões** diferenciando **administradores** e **usuários comuns**.


## 🚀 Execução

Para rodar o sistema:

```bash
# Clone o repositório
git clone https://github.com/arthurvalves/ProjectRefac-BankAPP.git

# Entre na pasta do projeto
cd ProjectRefac-BankAPP

# Execute o sistema
python main.py
```


