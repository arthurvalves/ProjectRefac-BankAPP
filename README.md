# 🏦 Banking Application - AV Bank

Projeto desenvolvido para a disciplina de **Projeto de Software** do curso de Engenharia de Computação da Universidade Federal de Alagoas.

## 📋 Sobre o Projeto

Este é um sistema de **gerenciamento bancário** completo, desenvolvido em Python. O sistema simula um ambiente bancário com suporte para dois tipos de usuários:

  * 👤 **Cliente** (com acesso a operações de conta)
  * 👨‍💼 **Administrador** (com privilégios de gerenciamento)

O objetivo principal foi aplicar um conjunto de **padrões de projeto** para garantir um código flexível, modular e de fácil manutenção, separando as responsabilidades do sistema.

## 🛠️ Como Executar o Projeto

1.  Clone este repositório:
    ```bash
    git clone https://github.com/arthurvalves/ProjectRefac-BankAPP.git
    ```
2.  Navegue até a pasta do projeto:
    ```bash
    cd ProjectRefac-BankAPP
    ```
3.  Instale as dependências:
    ```bash
    pip install -r requirements.txt
    ```
4.  Execute o sistema (CLI ou GUI):
    ```bash
    python main.py
    ```

## ✅ Funcionalidades Principais

  * **Gestão de Usuários**: Cadastro, login seguro (hash, bloqueio por tentativas), recuperação de senha e gerenciamento de papéis (Cliente, Admin).
  * **Operações Bancárias**: Criação de contas (corrente/poupança em BRL, USD, EUR, JPY), depósito, saque, transferência e pagamento de contas.
  * **Serviços Financeiros**: Módulo de investimentos (CDB, Tesouro Direto), câmbio de moedas com consulta a API externa e solicitação de empréstimos.
  * **Controle e Suporte**: Histórico de transações, alerta de saldo mínimo e um sistema de suporte ao cliente para registro de ocorrências.
  * **Persistência**: Todos os dados de usuários, contas e transações são salvos em um banco de dados **SQLite**.

## 📚 Padrões de Projeto Implementados

### Criacionais

  * **Singleton**: Utilizado na classe `ger_bd.py` para garantir uma única instância de conexão e gerenciamento do banco de dados em toda a aplicação.
  * **Factory Method**: Aplicado em `conta_factory.py` para desacoplar a lógica de criação dos diferentes tipos de conta (Corrente e Poupança).
  * **Builder**: Usado em `user_builder.py` para simplificar a criação de objetos `User`, permitindo uma construção passo a passo e validação de dados.

### Estruturais

  * **Facade**: Implementado em `fachada_banco.py` para prover uma interface simples e unificada para um conjunto complexo de operações do sistema (login, depósito, investimento, etc.).
  * **Adapter**: Utilizado em `bcb_adapter.py` para "traduzir" a interface da API externa do Banco Central para a interface `CambioProvider` esperada pelo nosso sistema.
  * **Proxy**: Aplicado em `cambio_cache_proxy.py` como um proxy de cache. Ele intercepta as chamadas de cotação de câmbio, retornando dados do cache se disponíveis, antes de consultar o `Adapter` (e a API externa).

### Comportamentais

  * **Command**: Usado em `commands.py` para encapsular cada ação do menu da CLI (como "Depositar", "Sacar") como um objeto, facilitando a execução e o gerenciamento do menu.
  * **Strategy**: Aplicado em `investimento_strategies.py` para permitir que o cliente escolha dinamicamente o algoritmo (a estratégia) de investimento (CDB ou Tesouro Direto).
  * **Observer**: Implementado em `observer.py` para notificar diferentes partes do sistema (como o log de transações ou o alerta de saldo) sempre que um evento ocorrer (ex: uma nova transação).

## 🛡️ Tratamento de exceções

### Onde implementei

- `utils/exceptions.py` — definição da hierarquia de exceções da aplicação (classe base `AppError` e subclasses como `ValidationError`, `InsufficientFundsError`, `ExternalAPIError`, etc.).
- `services/transfer_service.py` — validações de negócio para transferências; lança `ValidationError` e `InsufficientFundsError` quando apropriado.
- `services/pagar_service.py` — validações para pagamentos (mesma abordagem de levantar `ValidationError` / `InsufficientFundsError`).
- `utils/cambio_api.py` — uso de `wrap_exception` para encapsular erros de rede/requests em `ExternalAPIError`.
- `main.py` — pontos de captura (CLI) onde exceções são interceptadas para apresentar mensagens ao usuário e controlar fluxo.
- `services/facade.py` — ponto único de integração (facade) que reagrupa chamadas de serviços e propaga/transforma exceções quando necessário.

### A classe (trecho principal)

O projeto centraliza informações de erro em `AppError`. Exemplo (trecho de `utils/exceptions.py`):

```python
class AppError(Exception):
  def __init__(self, message: str, code: Optional[str] = None, details: Optional[Dict[str, Any]] = None,
         original_exception: Optional[Exception] = None):
    super().__init__(message)
    self.message = message
    self.code = code
    self.details = details or {}
    self.original_exception = original_exception

  def to_dict(self) -> Dict[str, Any]:
    return {
      "type": self.__class__.__name__,
      "message": self.message,
      "code": self.code,
      "details": self.details,
    }


class InsufficientFundsError(AppError):
  """Saldo insuficiente para operação financeira."""
```

### Por que implementei assim

- Centralização: ter uma hierarquia única facilita distinção entre erros de validação, autenticação, DB, APIs externas e erros de negócio.
- Informação contextual: `details` e `code` servem para logs estruturados, telemetria e respostas distintas para CLI/GUI/API.
- Encapsulamento de erros externos: `wrap_exception` preserva a exceção original e a transforma em um `AppError` compatível com o fluxo da aplicação.
- Tratamento: serviços ou camadas superiores podem capturar uma classe específica (ex.: `InsufficientFundsError`) e mensagens de usuário apropriadas.

### Como é feito o tratamento

- Exemplo de validação e lançamento de erro em `services/transfer_service.py`:

```python
from utils.exceptions import ValidationError, InsufficientFundsError

def transferir(origem, destino, valor):
  if valor <= 0:
    raise ValidationError("Valor de transferência deve ser maior que zero", code="INVALID_AMOUNT")

  if origem.saldo < valor:
    raise InsufficientFundsError("Saldo insuficiente para transferência",
                   details={"conta_origem": origem.num_conta, "valor": valor})
```

- Exemplo de wrapping de erro externo em `utils/cambio_api.py`:

```python
try:
  resposta = requests.get(url, timeout=5)
  resposta.raise_for_status()
except requests.exceptions.RequestException as e:
  raise wrap_exception(e, ExternalAPIError, message="Falha na comunicação com a API do BCB", details={"url": url})
```

- Exemplo de captura no CLI (`main.py`), onde tratamos erros para exibir mensagens claras ao usuário:

```python
try:
  if redefinir_senha_por_cpf(cpf, nova):
    ...
except (NotFoundError, ValidationError) as e:
  print('Erro ao redefinir senha:', e)
```

Nesses pontos, preferimos capturar classes específicas para manter mensagens úteis e aplicar lógicas distintas (por exemplo: não logar dados sensíveis em caso de `AuthError`).

## 📌 Exceções específicas 

- AppError (base)
  - Propósito: classe base para todas as exceções da aplicação; centraliza metadata (mensagem, código, detalhes e exceção original).
  - Quando é usada: todas as exceções customizadas estendem `AppError` para permitir tratamento uniforme e logs estruturados.
  - Campos úteis: `message`, `code` (opcional), `details` (dict), `original_exception` (exceção de baixo nível, quando houver).
  - Como tratar: capturar `AppError` quando quiser um fallback genérico ou log estruturado; use `to_dict()` para serializar.

- ValidationError
  - Propósito: erros de validação de entrada ou regras de negócio (ex.: valor inválido, formato incorreto).
  - Quando é lançada: validações em serviços (cadastro, transferências, pagamentos, etc.).
  - Exemplo de lançamento: `raise ValidationError("CPF inválido", code="INVALID_CPF")`.
  - Como tratar: capturar na camada que invoca a operação (ex.: CLI/GUI) e mostrar mensagem amigável ao usuário.

- AuthError
  - Propósito: falhas de autenticação/autorização (senha incorreta, token inválido, sem permissão).
  - Quando é lançada: durante login, verificação de permissões ou operações administrativas.
  - Observação: evitar logar informações sensíveis quando capturar `AuthError`.

- NotFoundError
  - Propósito: recurso não encontrado (conta, usuário, transação, etc.).
  - Quando é lançada: ao buscar um registro no banco e não encontrá-lo.
  - Como tratar: na API retornar 404; na CLI informar que o recurso não existe.

- DBError
  - Propósito: erros na camada de persistência (ex.: falha de conexão, query inválida).
  - Quando é lançada: exceções de SQLite/ORM são envolvidas ou traduzidas para `DBError`.
  - Como tratar: logar detalhes técnicos e retornar uma mensagem genérica ao usuário.

- TransactionError
  - Propósito: problemas em operações transacionais que devem disparar rollback.
  - Quando é lançada: falha durante um bloco transacional multi-step (ex.: transferências entre contas).
  - Como tratar: garantir rollback/compensação e notificar a camada chamadora.

- InsufficientFundsError
  - Propósito: sinaliza falta de fundos para completar operação financeira.
  - Quando é lançada: validação de saldo antes de saque/transferência/pagamento.
  - Campos úteis: `details` frequentemente contém `conta_origem` e `valor`.
  - Como tratar: informar usuário e abortar operação; em API mapear para 400/402.

- ExternalAPIError
  - Propósito: falha ao consumir APIs externas (ex.: BCB para câmbio).
  - Quando é lançada: timeout, erro de rede, status HTTP inesperado ou resposta inválida.
  - Observação: geralmente gerada via `wrap_exception` para preservar a exceção original.
  - Como tratar: retry condicionado, fallback para cache ou mensagem de indisponibilidade.

- ConcurrencyError
  - Propósito: conflito de concorrência/versão (optimistic/pessimistic locking).
  - Quando é lançada: detecção de versão divergente ao tentar persistir mudanças concorrentes.
  - Como tratar: informar ao usuário, refazer operação ou aplicar retry com backoff quando apropriado.

- FileError
  - Propósito: erros de I/O relacionados a arquivos (logs, importação/exportação de dados).
  - Quando é lançada: falha ao abrir/gravar/ler arquivos no disco.
  - Como tratar: notificar sobre problema de I/O e, se possível, oferecer recuperação/alternativa.

- RetryableError
  - Propósito: marca operações que podem ser reexecutadas com sucesso subsequente (ex.: timeout temporário).
  - Quando é lançada: condição temporária detectada (rede instável, lock curto, etc.).
  - Como tratar: implementar política de retry com backoff e limites.

- wrap_exception(exc, cls=AppError, message=None, **kwargs)
  - Propósito: função auxiliar que envolve uma exceção de baixo nível em uma instância de `AppError` (ou subclasse), preservando a `original_exception`.
  - Uso típico: transformar `requests.exceptions.RequestException` em `ExternalAPIError` mantendo o `exc` original para debug.
  
  - Exemplo:
```python
from utils.exceptions import wrap_exception, ExternalAPIError
try:
    resposta = requests.get(url, timeout=5)
    resposta.raise_for_status()
except requests.exceptions.RequestException as e:
    raise wrap_exception(e, ExternalAPIError, message="Falha na comunicação com a API do BCB", details={"url": url})
```

### Aplicação - exceção específica: InsufficientFundsError

- Propósito: sinalizar que a operação financeira não pôde ser concluída por falta de fundos.
- Campos úteis: `message` (texto), `code` (opcional, ex.: `INSUFFICIENT_FUNDS`), `details` (contendo número da conta, valor solicitado, etc.).
- Como tratar:
  - Em camadas de serviço: lançar a exceção para que a camada que chamou (facade/CLI) decida se reverte estados e qual mensagem mostrar.
  - Em CLI/GUI: capturar `InsufficientFundsError` e mostrar uma mensagem ao usuário, opcionalmente oferecendo alternativas (ex.: transferir de outra conta, solicitar crédito).
  - Em integrações/serviços externos: mapear para um código HTTP adequado (ex.: 400 Bad Request ou 402 Payment Required dependendo do contrato da API).

Exemplo de uso (resumo do fluxo):

1. Usuário solicita transferência via CLI.
2. `transfer_service.transferir` valida valor e saldo; se insuficiente, lança `InsufficientFundsError` com `details`.
3. `facade` captura a exceção e imprime: "Saldo insuficiente para transferência (Conta X)";

