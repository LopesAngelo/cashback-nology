from contextlib import contextmanager
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
import os
import re

from flask import Flask, jsonify, request
from flask_cors import CORS
import psycopg2

app = Flask(__name__)

DATABASE_URL = os.getenv("DATABASE_URL")
CORS_ORIGINS = [
    origin.strip()
    for origin in os.getenv("CORS_ORIGINS", "*").split(",")
    if origin.strip()
]

CORS(
    app,
    resources={r"/*": {"origins": CORS_ORIGINS}},
    allow_headers=["Content-Type", "X-Client-ID"],
    methods=["GET", "POST", "OPTIONS"],
)

CENTAVO = Decimal("0.01")
MAX_VALOR = Decimal("99999999.99")  # Limite de DECIMAL(10, 2) no PostgreSQL.
LIMITE_PROMOCAO = Decimal("500.00")
CLIENT_ID_RE = re.compile(r"^[a-f0-9]{64}$")


def decimalizar(valor, campo):
    """Converte uma entrada em Decimal sem aceitar booleanos ou valores não finitos."""
    if valor is None or isinstance(valor, bool):
        raise ValueError(f"O campo '{campo}' deve ser um número válido.")

    try:
        numero = Decimal(str(valor).strip())
    except (InvalidOperation, ValueError, TypeError, AttributeError):
        raise ValueError(f"O campo '{campo}' deve ser um número válido.")

    if not numero.is_finite():
        raise ValueError(f"O campo '{campo}' deve ser um número finito.")

    return numero


def calcular_valores_cashback(valor_bruto, desconto_percentual, eh_vip):
    """Retorna o valor líquido da compra e o cashback, ambos em centavos."""
    valor = decimalizar(valor_bruto, "valor")
    desconto = decimalizar(desconto_percentual, "desconto")

    if valor <= 0:
        raise ValueError("O valor da compra deve ser maior que zero.")
    if valor > MAX_VALOR:
        raise ValueError("O valor da compra excede o limite permitido.")
    if desconto < 0 or desconto > 100:
        raise ValueError("O desconto deve estar entre 0% e 100%.")

    valor = valor.quantize(CENTAVO, rounding=ROUND_HALF_UP)
    if valor <= 0:
        raise ValueError("O valor da compra deve ser de pelo menos R$ 0,01.")

    valor_liquido = (
        valor * (Decimal("1") - (desconto / Decimal("100")))
    ).quantize(CENTAVO, rounding=ROUND_HALF_UP)

    cashback = valor_liquido * Decimal("0.05")
    if eh_vip:
        cashback *= Decimal("1.10")
    if valor_liquido > LIMITE_PROMOCAO:
        cashback *= Decimal("2")

    cashback = cashback.quantize(CENTAVO, rounding=ROUND_HALF_UP)
    return valor_liquido, cashback


def calcular_nology_cashback(valor_bruto, desconto_percentual, eh_vip):
    """Calcula o cashback segundo as regras do desafio."""
    _, cashback = calcular_valores_cashback(
        valor_bruto,
        desconto_percentual,
        eh_vip,
    )
    return cashback


def obter_client_id():
    """Lê o identificador aleatório persistido pelo frontend para este navegador."""
    client_id = request.headers.get("X-Client-ID", "").strip().lower()
    if not CLIENT_ID_RE.fullmatch(client_id):
        return None
    return client_id


@contextmanager
def obter_conexao():
    """Abre uma conexão e garante commit/rollback e fechamento."""
    if not DATABASE_URL:
        raise RuntimeError("DATABASE_URL não foi configurada.")

    conexao = psycopg2.connect(DATABASE_URL, connect_timeout=5)
    try:
        with conexao:
            yield conexao
    finally:
        conexao.close()


def criar_tabela():
    """Cria a tabela e aplica a migração do identificador do navegador."""
    if not DATABASE_URL:
        app.logger.info(
            "DATABASE_URL não configurada. O cálculo funciona sem histórico persistido."
        )
        return

    try:
        with obter_conexao() as conexao:
            with conexao.cursor() as cursor:
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS historico_cashback (
                        id SERIAL PRIMARY KEY,
                        client_id VARCHAR(64),
                        tipo_cliente VARCHAR(10) NOT NULL,
                        valor_compra DECIMAL(10, 2) NOT NULL,
                        valor_cashback DECIMAL(10, 2) NOT NULL,
                        data_consulta TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                    """
                )
                # Migração compatível com a tabela antiga, que identificava pelo IP.
                cursor.execute(
                    """
                    ALTER TABLE historico_cashback
                    ADD COLUMN IF NOT EXISTS client_id VARCHAR(64);
                    """
                )
                cursor.execute(
                    """
                    CREATE INDEX IF NOT EXISTS idx_historico_cashback_client_id
                    ON historico_cashback (client_id, id DESC);
                    """
                )
        app.logger.info("Tabela e índice de histórico verificados.")
    except Exception:
        app.logger.exception("Não foi possível preparar o banco de dados.")


def salvar_historico(client_id, tipo, valor_liquido, cashback):
    with obter_conexao() as conexao:
        with conexao.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO historico_cashback
                    (client_id, tipo_cliente, valor_compra, valor_cashback)
                VALUES (%s, %s, %s, %s);
                """,
                (client_id, tipo, valor_liquido, cashback),
            )


@app.get("/health")
def health():
    return jsonify(
        {
            "status": "ok",
            "database_configurada": bool(DATABASE_URL),
        }
    )


@app.post("/calcular")
def calcular():
    dados = request.get_json(silent=True)
    if not isinstance(dados, dict):
        return jsonify({"erro": "Envie um objeto JSON válido."}), 400

    client_id = obter_client_id()
    if not client_id:
        return jsonify({"erro": "Identificador do navegador inválido ou ausente."}), 400

    tipo = dados.get("tipo", "COMUM")
    if not isinstance(tipo, str):
        return jsonify({"erro": "O tipo de cliente deve ser COMUM ou VIP."}), 400

    tipo = tipo.strip().upper()
    if tipo not in {"COMUM", "VIP"}:
        return jsonify({"erro": "O tipo de cliente deve ser COMUM ou VIP."}), 400

    try:
        desconto_informado = dados.get("desconto", 0)
        valor_liquido, cashback = calcular_valores_cashback(
            dados.get("valor"),
            desconto_informado,
            tipo == "VIP",
        )
    except ValueError as erro:
        return jsonify({"erro": str(erro)}), 400

    persistido = False
    aviso = None

    if DATABASE_URL:
        try:
            salvar_historico(client_id, tipo, valor_liquido, cashback)
            persistido = True
        except Exception:
            app.logger.exception("Falha ao salvar o cálculo no histórico.")
            aviso = "O cálculo foi realizado, mas não foi possível salvar o histórico."
    else:
        aviso = "Banco de dados não configurado: o cálculo não foi salvo no histórico."

    return jsonify(
        {
            "valor_liquido": str(valor_liquido),
            "cashback": str(cashback),
            "persistido": persistido,
            "aviso": aviso,
        }
    )


@app.get("/historico")
def historico():
    client_id = obter_client_id()
    if not client_id:
        return jsonify({"erro": "Identificador do navegador inválido ou ausente."}), 400

    if not DATABASE_URL:
        return jsonify({"erro": "Histórico indisponível: banco de dados não configurado."}), 503

    try:
        with obter_conexao() as conexao:
            with conexao.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT tipo_cliente, valor_compra, valor_cashback, data_consulta
                    FROM historico_cashback
                    WHERE client_id = %s
                    ORDER BY id DESC
                    LIMIT 100;
                    """,
                    (client_id,),
                )
                linhas = cursor.fetchall()

        resultado = [
            {
                "tipo": linha[0],
                "valor": str(linha[1]),
                "cashback": str(linha[2]),
                "data": linha[3].isoformat() if linha[3] else None,
            }
            for linha in linhas
        ]
        return jsonify(resultado)
    except Exception:
        app.logger.exception("Falha ao consultar o histórico.")
        return jsonify({"erro": "Não foi possível consultar o histórico agora."}), 503


# Cria/migra a tabela ao iniciar o processo, inclusive com Gunicorn/WSGI.
criar_tabela()


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.getenv("PORT", "5000")),
        debug=False,
    )
