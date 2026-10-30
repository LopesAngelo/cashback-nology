# Nology Cashback

Aplicação web full-stack para simular o cálculo de cashback de uma fintech. O projeto foi desenvolvido como desafio técnico e utiliza Python, Flask, PostgreSQL, HTML, JavaScript e Tailwind CSS.

## Funcionalidades

- Cálculo de cashback sobre o valor líquido da compra.
- Cashback base de 5%.
- Bônus VIP de 10% sobre o cashback base.
- Cashback dobrado quando o valor líquido da compra é superior a R$ 500,00.
- Registro e consulta do histórico de simulações.
- Interface responsiva para realizar simulações.

## Regras de negócio

A aplicação executa as regras nesta ordem:

1. Aplica o desconto sobre o valor bruto da compra.
2. Calcula 5% de cashback sobre o valor líquido.
3. Para clientes VIP, acrescenta 10% sobre o cashback base.
4. Quando o valor líquido é superior a R$ 500,00, dobra o cashback total.

Exemplos:

| Valor líquido | Tipo | Cashback |
|---:|---|---:|
| R$ 200,00 | COMUM | R$ 10,00 |
| R$ 200,00 | VIP | R$ 11,00 |
| R$ 500,00 | COMUM | R$ 25,00 |
| R$ 501,00 | COMUM | R$ 50,10 |
| R$ 501,00 | VIP | R$ 55,11 |

Os valores monetários são calculados com `Decimal` e arredondamento comercial para duas casas decimais.

## Tecnologias

- **Backend:** Python e Flask.
- **Banco de dados:** PostgreSQL com psycopg2.
- **Frontend:** HTML5, JavaScript e Tailwind CSS.
- **API:** endpoints HTTP/JSON.
- **Testes:** pytest.

## Estrutura do projeto

```text
cashback-nology/
├── .github/workflows/tests.yml
├── tests/test_cashback.py
├── app.py
├── index.html
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

## Como executar localmente

### 1. Pré-requisitos

- Python 3.10 ou superior.
- PostgreSQL (opcional para testar apenas o cálculo; necessário para persistir o histórico).

### 2. Clonar o repositório

```bash
git clone https://github.com/LopesAngelo/cashback-nology.git
cd cashback-nology
```

### 3. Criar e ativar um ambiente virtual

Windows PowerShell:

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
```

Linux/macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 4. Instalar dependências

```bash
pip install -r requirements.txt
```

### 5. Configurar o banco de dados (opcional)

Crie um banco PostgreSQL e defina a variável de ambiente `DATABASE_URL`.

Windows PowerShell:

```powershell
$env:DATABASE_URL="postgresql://usuario:senha@localhost:5432/nology_cashback"
$env:CORS_ORIGINS="http://127.0.0.1:5500,http://localhost:5500"
```

Linux/macOS:

```bash
export DATABASE_URL="postgresql://usuario:senha@localhost:5432/nology_cashback"
export CORS_ORIGINS="http://127.0.0.1:5500,http://localhost:5500"
```

A tabela e o índice de histórico são criados automaticamente quando a aplicação inicia. O código também adiciona a coluna `client_id` a uma tabela criada pela versão anterior.

Sem `DATABASE_URL`, a API ainda calcula o cashback, mas não persiste o histórico. O endpoint de histórico retorna HTTP 503 nessa situação.

### 6. Iniciar o backend

```bash
python app.py
```

A API ficará disponível em `http://localhost:5000`.

### 7. Abrir o frontend

Abra `index.html` com uma extensão de servidor local, como Live Server (porta 5500). Para trabalhar localmente, altere a constante `URL_API` no início do script para `http://localhost:5000`.

No deploy, configure `CORS_ORIGINS` no ambiente do backend com a origem exata do site que hospeda o frontend. Não inclua caminhos, apenas esquema, domínio e porta, quando houver.

## Endpoints da API

### `POST /calcular`

Calcula o cashback e tenta salvar a simulação.

Cabeçalho obrigatório:

```http
X-Client-ID: <64 caracteres hexadecimais>
Content-Type: application/json
```

Exemplo de corpo:

```json
{
  "valor": 600.00,
  "desconto": 10,
  "tipo": "VIP"
}
```

Exemplo de resposta:

```json
{
  "valor_liquido": "540.00",
  "cashback": "59.40",
  "persistido": true,
  "aviso": null
}
```

Validações aplicadas no backend:

- Valor da compra maior que zero e dentro do limite suportado pelo banco.
- Desconto entre 0% e 100%.
- Tipo de cliente igual a `COMUM` ou `VIP`.
- JSON válido e identificador do navegador válido.

### `GET /historico`

Retorna até as 100 simulações mais recentes associadas ao identificador enviado no cabeçalho `X-Client-ID`.

### `GET /health`

Retorna o estado básico da aplicação e informa se `DATABASE_URL` foi configurada.

## Identificação do histórico

O frontend gera um identificador aleatório de 256 bits e o mantém no `localStorage` do navegador. A API usa esse identificador para separar os históricos, em vez de usar o endereço IP.

**Limitação importante:** esse mecanismo identifica uma instalação do navegador, não uma pessoa autenticada. Não substitui cadastro, login ou autorização de usuários. Limpar os dados do navegador gera um novo identificador, e o histórico anterior deixa de aparecer nesse navegador. Não armazene informações sensíveis nesse protótipo.

## Testes automatizados

Execute:

```bash
pytest -q
```

Os testes cobrem as regras de cálculo, limites de desconto e valor, validação dos dados da API e comportamento sem banco configurado.

## Configurações de deploy

Configure no serviço de backend:

- `DATABASE_URL`: string de conexão PostgreSQL.
- `CORS_ORIGINS`: origem do frontend. Exemplo: `https://seu-site.example`.

O valor padrão de `CORS_ORIGINS` é `*` para facilitar a execução local. Em produção, configure as origens permitidas explicitamente.

## Próximas evoluções

- Autenticação real de usuários.
- Migrações de banco versionadas.
- Limitação de requisições (rate limiting).
- Paginação do histórico.
- Pipeline de integração contínua.
- Testes de integração com PostgreSQL.

## Autor

Angelo Lopes — [GitHub](https://github.com/LopesAngelo)
