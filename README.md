# Nology Cashback

[![Testes automatizados](https://github.com/LopesAngelo/cashback-nology/actions/workflows/tests.yml/badge.svg?branch=main)](https://github.com/LopesAngelo/cashback-nology/actions/workflows/tests.yml)

Aplicação web full-stack para simulação de cashback, desenvolvida com Python, Flask, PostgreSQL, JavaScript e HTML. O projeto implementa regras de negócio, API REST, persistência de dados e testes automatizados com integração contínua.

## Demonstração online

**[Acessar Nology Cashback](https://nology-cashback-frontend.onrender.com)**

## Funcionalidades

- Simulação de cashback para clientes comuns e VIP.
- Aplicação de descontos sobre o valor bruto da compra.
- Cálculo financeiro com `Decimal` e arredondamento comercial.
- Cashback diferenciado para clientes VIP.
- Cashback dobrado para compras com valor líquido superior a R$ 500,00.
- Histórico de simulações armazenado no PostgreSQL.
- Identificação de histórico por navegador.
- Interface responsiva.
- Validação de dados no frontend e backend.
- Tratamento de erros da API.

## Regras de negócio

O cálculo segue estas regras:

1. Aplica o desconto informado sobre o valor bruto.
2. Calcula 5% de cashback sobre o valor líquido.
3. Clientes VIP recebem um adicional de 10% sobre o cashback base.
4. Compras com valor líquido superior a R$ 500,00 recebem cashback dobrado.

| Valor líquido | Cliente | Cashback |
|---:|---|---:|
| R$ 200,00 | Comum | R$ 10,00 |
| R$ 200,00 | VIP | R$ 11,00 |
| R$ 500,00 | Comum | R$ 25,00 |
| R$ 501,00 | Comum | R$ 50,10 |
| R$ 600,00 | VIP | R$ 66,00 |

## Tecnologias utilizadas

**Backend**
- Python
- Flask
- Flask-CORS
- Gunicorn

**Banco de dados**
- PostgreSQL
- psycopg2

**Frontend**
- HTML5
- JavaScript
- Tailwind CSS

**Qualidade e automação**
- pytest
- Git e GitHub
- GitHub Actions
- Integração contínua (CI)

**Deploy**
- Render
- Neon PostgreSQL

## Arquitetura

O projeto utiliza uma arquitetura separada em frontend, backend e banco de dados.

- Frontend: interface responsável pela interação com o usuário.
- Backend: API Flask responsável pelas validações e regras de negócio.
- PostgreSQL: armazenamento persistente do histórico.
- GitHub Actions: execução automática dos testes a cada atualização do repositório.

## Endpoints da API

| Método | Endpoint | Descrição |
|---|---|---|
| GET | `/health` | Verifica o estado básico da aplicação e a configuração do banco |
| POST | `/calcular` | Calcula o cashback e tenta registrar a simulação |
| GET | `/historico` | Consulta as simulações do navegador |

As rotas de cálculo e histórico utilizam o cabeçalho `X-Client-ID` para identificar o navegador.

## Como executar localmente

### 1. Clonar o repositório

```bash
git clone https://github.com/LopesAngelo/cashback-nology.git
cd cashback-nology
```

### 2. Criar ambiente virtual

Windows:

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
```

Linux/macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Instalar dependências

```bash
pip install -r requirements.txt
```

### 4. Configurar variáveis de ambiente

Configure a variável `DATABASE_URL` com a string de conexão do PostgreSQL.

Exemplo no PowerShell:

```powershell
$env:DATABASE_URL="postgresql://usuario:senha@localhost:5432/nology_cashback"
$env:CORS_ORIGINS="http://127.0.0.1:5500,http://localhost:5500"
```

### 5. Executar o backend

```bash
python app.py
```

A API ficará disponível em:

```text
http://localhost:5000
```

### 6. Executar o frontend

Abra o arquivo `index.html` usando uma extensão de servidor local, como Live Server.

Durante o desenvolvimento local, configure a constante `URL_API` no JavaScript para:

```javascript
const URL_API = "http://localhost:5000";
```

Sem `DATABASE_URL`, o cálculo ainda pode funcionar, mas o histórico não será persistido.

## Testes automatizados

O projeto utiliza pytest para verificar as regras de negócio, validações da API e comportamentos sem banco configurado.

Execute:

```bash
python -m pytest -q
```

Os testes são executados automaticamente pelo GitHub Actions em atualizações da branch `main` e em pull requests.

## Variáveis de ambiente

| Variável | Finalidade |
|---|---|
| `DATABASE_URL` | Conexão com o PostgreSQL |
| `CORS_ORIGINS` | Origens autorizadas a consumir a API |
| `PORT` | Porta de execução do backend |

Não inclua credenciais ou senhas no repositório.

## Observações técnicas

O histórico utiliza um identificador aleatório armazenado no `localStorage` do navegador. Esse mecanismo não representa autenticação real e não substitui cadastro, login ou autorização de usuários.

O projeto é uma demonstração técnica e pode ser evoluído para uso em produção com autenticação, autorização, limitação de requisições e migrações de banco versionadas.

## Autor

**Angelo Lopes**

Estudante de Engenharia de Software, interessado em desenvolvimento de software e construção de aplicações web.

- [GitHub](https://github.com/LopesAngelo)
- [Repositório Nology Cashback](https://github.com/LopesAngelo/cashback-nology)
- [Demonstração online](https://nology-cashback-frontend.onrender.com)
