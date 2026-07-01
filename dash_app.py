"""Financial analytics dashboard built with Python Dash and Plotly."""

import os

import pandas as pd
import plotly.express as px  # type: ignore[import]
import psycopg
from dash import Dash, dcc, html
from dotenv import load_dotenv

load_dotenv()


def load_dash_data():
    """Busca os dados da Neon e entrega um DataFrame pronto para os gráficos do Dash."""
    conn_string = os.environ.get("DATABASE_URL") or ""

    query = "SELECT amount, currency, service, description, is_recurring, created_at FROM accounts;"

    # Abrimos a conexão e usamos o método .cursor() para obter as linhas nativas,
    # eliminando o aviso de compatibilidade do Pandas
    with psycopg.connect(conn_string) as conn:
        with conn.cursor() as cur:
            cur.execute(query)
            rows = cur.fetchall()
            # Se o cursor retornar descrição dos campos, pegamos as colunas dinamicamente
            colnames = [desc[0] for desc in cur.description] if cur.description else []
            df = pd.DataFrame(rows, columns=colnames)

    if not df.empty and "created_at" in df.columns:
        df["created_at"] = pd.to_datetime(df["created_at"])
    return df


# 1. Inicializa o aplicativo Dash
app = Dash(__name__, title="Industrial Financial BI")

try:
    # 2. Carrega os dados da Neon via Pandas
    df_accounts = load_dash_data()

    # 3. Monta um gráfico interativo expresso
    if not df_accounts.empty:
        fig_services = px.bar(
            df_accounts,
            x="service",
            y="amount",
            color="currency",
            barmode="group",
            title="Distribuição de Custos por Serviço",
        )
    else:
        fig_services = px.scatter(title="Nenhum dado encontrado no banco.")

except (psycopg.Error, OSError) as e:
    df_accounts = pd.DataFrame()
    fig_services = px.scatter(title=f"Erro ao conectar ao banco: {e}")

# 4. Define o layout visual que será renderizado na página web
app.layout = html.Div(
    style={"fontFamily": "sans-serif", "padding": "20px"},
    children=[
        html.H1("Dashboard Financeiro Avançado", style={"color": "#1e293b"}),
        html.P("Análise analítica de lançamentos em tempo real (Neon/Postgres)."),
        html.Hr(),
        # Container do Gráfico do Plotly
        dcc.Graph(id="graph-services", figure=fig_services),
    ],
)

# 5. Inicializa o servidor web local com o método atualizado
if __name__ == "__main__":
    # Substituído app.run_server por app.run para compatibilidade total
    app.run(debug=True, port=8050)
