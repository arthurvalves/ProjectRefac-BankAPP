
# 🏦 Banking Application - AV Bank

Este é um sistema de **gerenciamento bancário**, desenvolvido em Python como parte da disciplina de Projeto de Software.

O projeto utiliza **padrões de projeto criacionais** (Singleton, Factory Method, Builder) e **comportamentais** (Command, Strategy).

---

## ✅ Funcionalidades implementadas

* ✅ **Cadastro de usuários** (nome, CPF, telefone e e-mail com validação)
* ✅ **Cadastro de contas** (corrente ou poupança, com escolha de moeda)
* ✅ **Operações básicas** (depósito, saque, transferência)
* ✅ **Pagamento de contas**
* ✅ **Histórico de transações** (visualização e limpeza)
* ✅ **Investimentos** com diferentes estratégias (CDB e Tesouro Direto)
* ✅ **Câmbio de moedas** (USD, EUR, JPY) com consulta a API externa
* ✅ **Solicitação de empréstimos**
* ✅ **Solicitação de talão de cheques**
* ✅ **Alerta de saldo mínimo**
* ✅ **Suporte ao cliente** para registro de ocorrências
* ✅ **Persistência em banco de dados SQLite**
* ✅ **Validação de dados de entrada** (nome, CPF, telefone, e-mail)
* ✅ **Testes automatizados com pytest** (para validação e operações básicas)


---

## 📚 Estrutura do Código

### 🧱 Classes e módulos principais

* `models/conta.py`: modelo de conta bancária
* `models/user.py`: modelo de usuário
* `models/conta_factory.py`: Factory Method para criação de contas
* `models/user_builder.py`: Builder para construção de objetos `User`
* `database/ger_bd.py`: Singleton para conexão e operações no banco de dados
* `commands.py`: Padrão Command para encapsular as ações do menu
* `services/investimento_strategies.py`: Padrão Strategy para diferentes tipos de investimento
* `services/*`: Módulos de serviço para cada funcionalidade (transferência, câmbio, etc.)
* `utils/validacao.py`: validações de dados de entrada
* `main.py`: interface principal (menu de interação com o sistema)

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
  * [x] CDB
  * [x] Tesouro Direto
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

# Instale as dependências
pip install -r requirements.txt

# Execute o sistema
python main.py
```
