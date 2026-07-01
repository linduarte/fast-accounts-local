# fast-accounts-local

Este projeto consiste em um serviço de gerenciamento e análise de dados financeiros (`AccountsService`). Recentemente atualizado, o sistema migrou de uma arquitetura baseada em Supabase para um banco de dados **PostgreSQL sempre ativo (Always-On) hospedado na Neon.tech**, eliminando gargalos de inatividade e congelamento no plano gratuito.

A aplicação foi projetada para garantir consistência de dados em tempo real, permitindo que múltiplos clientes (como computadores locais e dispositivos móveis) acessem e sincronizem exatamente as mesmas informações financeiras na nuvem.

## 🚀 Tecnologias Utilizadas

* **Python 3**
* **Neon.tech** (PostgreSQL Serverless com Connection Pooling ativo)
* **Psycopg 3** (`psycopg[binary]`) — Driver moderno e de alta performance para PostgreSQL
* **uv** — Gerenciador de pacotes e ambientes virtuais ultrarrápido

## 🛠️ Arquitetura e Otimizações

Durante a refatoração, o serviço foi otimizado para cenários de uso em nuvem:

1. **Single-Roundtrip Analytics:** O método `get_financial_summary` foi reestruturado para executar uma única consulta agrupada (`GROUP BY`) diretamente no motor do PostgreSQL. Isso reduz de 4 para 1 o número de requisições de rede, minimizando a latência na interface do usuário.
2. **Gerenciamento Seguro de Conexões:** Uso estrito de Context Managers (`with`) para abertura e fechamento automatizado de conexões TCP, evitando vazamentos de recursos (*connection leaks*).
3. **Segurança nativa contra SQL Injection:** Parametrização total das consultas SQL (`%s`).

## 📋 Estrutura da Tabela no Banco de Dados

A tabela `accounts` na Neon.tech está estruturada da seguinte forma:

```sql
CREATE TABLE accounts (
    id SERIAL PRIMARY KEY,
    amount NUMERIC(15, 2) NOT NULL,
    currency VARCHAR(10) NOT NULL,
    service VARCHAR(255) NOT NULL,
    description TEXT,
    username VARCHAR(100),
    is_recurring BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

```

🔧 Configuração do Ambiente Local
1. Requisitos do Sistema
Certifique-se de ter o uv instalado globalmente no seu sistema (Windows/Linux).

2. Variáveis de Ambiente (.env)
Crie ou altere o seu arquivo .env na raiz do projeto com a Connection String fornecida pelo painel da Neon (utilizando obrigatoriamente o endpoint de Pooling):

```Python
DATABASE_URL="postgresql://usuario:senha@ep-nome-do-projeto-pooler.region.neon.tech/neondb?sslmode=require"
```
3. Instalação de Dependências com uv
Para sincronizar ou instalar o ambiente virtual isolado, utilize o uv:


```Powershell
# Limpa o ambiente antigo e instala as novas dependências
uv pip install "psycopg[binary]" python-dotenv
```

💻 Como Executar
A classe AccountsService gerencia automaticamente o ciclo de vida do banco. Para rodar o script ou a aplicação integrada através do ambiente virtual gerenciado pelo uv:

```Powershell
uv run accounts_service.py
```

