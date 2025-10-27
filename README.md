
# 🏦 Banking Application - AV Bank

Este é um sistema de **gerenciamento bancário**, desenvolvido em Python como parte da disciplina de Projeto de Software.


O projeto utiliza um conjunto de **padrões de projeto** para garantir a separação de responsabilidades e a flexibilidade do código:
*   **Criacionais**: Singleton, Factory Method, Builder.
*   **Estruturais**: Facade, Adapter, Proxy.
*   **Comportamentais**: Command, Strategy, Observer.

---

## ✅ Funcionalidades implementadas

* ✅ **Cadastro de usuários** (nome, CPF, telefone e e-mail com validação)
* ✅ **Sistema de login seguro** com hash de senhas, bloqueio por tentativas e recuperação de senha.
* ✅ **Gerenciamento de papéis** (usuário e administrador).
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
* ✅ **Interface Gráfica (GUI)** com Tkinter para login e operações bancárias.

---

## 📚 Estrutura do Código

### 🧱 Classes e módulos principais

*   `main.py`: Ponto de entrada para a aplicação em modo console (CLI).
*   `gui/login_app.py`: Ponto de entrada para a aplicação com Interface Gráfica (GUI).
*   `models/`: Contém as classes de domínio como `Conta`, `User` e `Transacao`.
    *   `conta_factory.py`: **Factory Method** para criação de contas.
    *   `user_builder.py`: **Builder** para construção de objetos `User`.
*   `database/ger_bd.py`: **Singleton** para gerenciar a conexão e operações no banco de dados SQLite.
*   `commands.py`: **Command** para encapsular as ações do menu da CLI.
*   `services/`: Módulos que contêm a lógica de negócio.
    *   `fachada_banco.py`: **Facade** que simplifica o acesso a operações complexas do sistema.
    *   `investimento_strategies.py`: **Strategy** para diferentes tipos de investimento.
    *   `servico_autenticacao.py`: Lógica de autenticação, gerenciamento de senhas e papéis.
*   `utils/`: Utilitários e implementações de padrões.
    *   `observer.py`: **Observer** para notificar sobre eventos (ex: transações).
    *   `cambio_provider.py`: Interface (ABC) para o padrão **Adapter**.
    *   `bcb_adapter.py`: **Adapter** concreto que consome a API do Banco Central.
    *   `cambio_cache_proxy.py`: **Proxy** que adiciona cache às chamadas de câmbio.

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

*   [ ] Expandir a GUI para cobrir todas as funcionalidades do sistema.
*   [ ] Adicionar mais estratégias de investimento (FIIs, Ações).
*   [ ] Implementar um painel administrativo na GUI para gerenciamento de usuários.
*   [ ] Melhorar o tratamento de concorrência nas operações de banco de dados.

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
