# ⚡ Nology Cashback - Desafio Técnico

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)
![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white)

Este projeto foi desenvolvido como solução para o Desafio Técnico da vaga de estágio. Trata-se de uma aplicação Full-Stack que simula o sistema de cashback de uma Fintech, aplicando regras de negócio rigorosas e armazenando o histórico de consultas por usuário (via IP).

## 📋 Regras de Negócio Implementadas

A lógica de cálculo no backend foi construída para atender estritamente aos requisitos documentados:
1. **Descontos Primeiro:** O cashback é calculado sobre o valor *líquido* da compra (após a aplicação de cupons).
2. **Cashback Base:** Definido em 5% sobre o valor líquido.
3. **Bônus VIP:** Clientes VIP recebem um bônus de 10%, calculado *sobre o valor do cashback base* (e não sobre o valor da compra).
4. **Promoção de Volume:** Se o valor líquido da compra ultrapassar R$ 500,00, o valor total do cashback (base + bônus) é **dobrado**. Esta regra é válida para todos os clientes.

## 🛠️ Arquitetura e Tecnologias

* **Backend:** Python com o micro-framework **Flask**. Escolhido por ser leve e ideal para APIs RESTful rápidas.
* **Banco de Dados:** **PostgreSQL**. O backend possui uma rotina inteligente que verifica e cria a tabela `historico_cashback` automaticamente na inicialização, caso ela não exista.
* **Frontend:** HTML5, Javascript Vanilla e **Tailwind CSS** via CDN. Design mobile-first, responsivo e com UX inspirada em aplicativos bancários modernos.
* **Comunicação:** API REST (Endpoints `/calcular` e `/historico`) com tratamento de CORS.

## 🚀 Como Executar o Projeto Localmente

### Pré-requisitos
* Python 3.x instalado.
* (Opcional) Um banco de dados PostgreSQL rodando localmente ou em nuvem. Se a variável `DATABASE_URL` não for configurada, o app rodará no modo de demonstração sem salvar o histórico.

### Passos para rodar

1. **Clone o repositório:**
   ```bash
   git clone [https://github.com/SEU_USUARIO/desafio-cashback-nology.git](https://github.com/SEU_USUARIO/desafio-cashback-nology.git)
   cd desafio-cashback-nology
