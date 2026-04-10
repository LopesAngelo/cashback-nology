from flask import Flask, request, jsonify
from flask_cors import CORS
import psycopg2
import os

app = Flask(__name__)
CORS(app)

# Configuração do Banco de Dados (variável que o Render vai fornecer)
DATABASE_URL = os.getenv('DATABASE_URL')

def obter_conexao():
    return psycopg2.connect(DATABASE_URL)

# --- Cria a tabela automaticamente caso não exista ---
def criar_tabela():
    try:
        # Se estiver rodando local sem a variável, avisa no terminal
        if not DATABASE_URL:
            print("DATABASE_URL não configurada ainda. Ignorando criação de tabela.")
            return
            
        conn = obter_conexao()
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS historico_cashback (
                id SERIAL PRIMARY KEY,
                ip_usuario VARCHAR(45),
                tipo_cliente VARCHAR(10),
                valor_compra DECIMAL(10,2),
                valor_cashback DECIMAL(10,2),
                data_consulta TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        conn.commit()
        cur.close()
        conn.close()
        print("✅ Tabela verificada/criada com sucesso no banco de dados!")
    except Exception as e:
        print(f"❌ Erro ao criar/verificar a tabela: {e}")

# Executa a verificação da tabela assim que o sistema iniciar
criar_tabela()

# -------------------------------------------------------------------
# Lógica de Negócio - Nology Cashback
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

    # Chamamos a função de regra de negócio para fazer o cálculo pesado
    total_cashback = calcular_nology_cashback(valor, desconto, eh_vip)
    
    # Calcula o valor líquido novamente apenas para salvar no histórico
    valor_liquido = valor * (1 - (desconto / 100))

    # Tenta salvar no Banco de Dados
    try:
        conn = obter_conexao()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO historico_cashback (ip_usuario, tipo_cliente, valor_compra, valor_cashback) VALUES (%s, %s, %s, %s)",
            (ip, dados.get('tipo'), valor_liquido, total_cashback)
        )
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Erro ao salvar no banco: {e}")
        # Mesmo se houver erro no banco, retornamos o valor para o app não travar

    return jsonify({"cashback": total_cashback})

@app.route('/historico', methods=['GET'])
def historico():
    ip = request.remote_addr
    try:
        conn = obter_conexao()
        cur = conn.cursor()
        cur.execute("SELECT tipo_cliente, valor_compra, valor_cashback FROM historico_cashback WHERE ip_usuario = %s ORDER BY id DESC", (ip,))
        linhas = cur.fetchall()
        cur.close()
        conn.close()
        
        # Formata os dados para enviar para o Frontend
        resultado = [{"tipo": l[0], "valor": float(l[1]), "cashback": float(l[2])} for l in linhas]
        return jsonify(resultado)
    except Exception as e:
        print(f"Erro ao buscar histórico: {e}")
        return jsonify([]) # Retorna lista vazia se der erro, mantendo o app limpo

if __name__ == "__main__":
    app.run()
