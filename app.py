from flask import Flask, request, jsonify
from flask_cors import CORS
import psycopg2
import os

app = Flask(__name__)
CORS(app)

# Configuração do Banco de Dados
DATABASE_URL = os.getenv('DATABASE_URL')

def obter_conexao():
    return psycopg2.connect(DATABASE_URL)

# -------------------------------------------------------------------
# AQUI ENTRA O SEU CÓDIGO (Lógica de Negócio)
# -------------------------------------------------------------------
def calcular_nology_cashback(valor_bruto, desconto_percentual, eh_vip):
    # Regra Doc 1: Cashback calculado sobre o valor FINAL (após descontos)
    valor_liquido = valor_bruto * (1 - (desconto_percentual / 100))
    
    # Regra Doc 1: Cashback base é 5%
    cashback_base = valor_liquido * 0.05
    
    # Regra Doc 3: Primeiro calcular cashback base, DEPOIS o bônus VIP (10% sobre o base)
    bonus_vip = 0
    if eh_vip:
        bonus_vip = cashback_base * 0.10
    
    cashback_total = cashback_base + bonus_vip
    
    # Regra Doc 2: Compras > R$ 500 ganham o DOBRO. Vale para todos (inclusive VIPs).
    if valor_liquido > 500:
        cashback_total *= 2
        
    return round(cashback_total, 2)
# -------------------------------------------------------------------

@app.route('/calcular', methods=['POST'])
def calcular():
    dados = request.json
    valor = float(dados.get('valor', 0))
    desconto = float(dados.get('desconto', 0))
    eh_vip = dados.get('tipo', 'COMUM') == 'VIP'
    ip = request.remote_addr # Identifica o usuário pelo IP

    # Chamamos a SUA função aqui para fazer o cálculo pesado!
    total = calcular_nology_cashback(valor, desconto, eh_vip)
    
    # Calcula o valor líquido novamente apenas para salvar no histórico
    valor_liquido = valor * (1 - (desconto / 100))

    # Registro no Banco de Dados
    conn = obter_conexao()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO historico_cashback (ip_usuario, tipo_cliente, valor_compra, valor_cashback) VALUES (%s, %s, %s, %s)",
        (ip, dados.get('tipo'), valor_liquido, total)
    )
    conn.commit()
    cur.close()
    conn.close()

    return jsonify({"cashback": total})

@app.route('/historico', methods=['GET'])
def historico():
    ip = request.remote_addr
    conn = obter_conexao()
    cur = conn.cursor()
    cur.execute("SELECT tipo_cliente, valor_compra, valor_cashback FROM historico_cashback WHERE ip_usuario = %s ORDER BY id DESC", (ip,))
    linhas = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify([{"tipo": l[0], "valor": float(l[1]), "cashback": float(l[2])} for l in linhas])

if __name__ == "__main__":
    app.run()