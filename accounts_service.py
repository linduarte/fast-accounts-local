"""Accounts service for Neon/PostgreSQL-backed financial data."""

import os

import os
from dotenv import load_dotenv
from psycopg.rows import dict_row
import psycopg

# Garante o carregamento do ambiente na leitura do módulo
load_dotenv()


class AccountsService:
    """Service class for managing bank account data layers."""

    def __init__(self):
        # Em vez de fixar uma string imutável na inicialização,
        # usamos uma propriedade dinâmica para buscar sempre direto do ambiente atualizado
        self._connection_string = None

    @property
    def connection_string(self) -> str:
        """Busca a string de conexão e diagnostica o valor real lido pelo Python."""
        url = os.environ.get("DATABASE_URL")
        
        # Esse print vai nos mostrar exatamente o que está chegando aqui
        print(f"\n[DIAGNÓSTICO] O Python leu a DATABASE_URL como: '{url}'\n")

        if not url:
            raise ValueError("ERRO CRÍTICO: DATABASE_URL está vazia!")
            
        return url

    def _get_connection(self):
        """Creates and returns a new connection to the PostgreSQL backend."""
        # Agora o self.connection_string vai rodar o método dinâmico acima
        return psycopg.connect(self.connection_string, row_factory=dict_row)

        
    def get_financial_summary(self):
        """Return recurring and non-recurring financial totals by currency.

        Optimized to perform a single grouped query instead of 4 separate calls.
        """
        # Estrutura inicial padrão para garantir consistência mesmo se o banco estiver vazio
        summary = {
            "BRL": {"monthly": 0.0, "annual": 0.0},
            "USD": {"monthly": 0.0, "annual": 0.0},
        }

        query = """
            SELECT currency, is_recurring, COALESCE(SUM(amount), 0) as total
            FROM accounts
            WHERE currency IN ('BRL', 'USD')
            GROUP BY currency, is_recurring;
        """

        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query)
                results = cur.fetchall()

        # Mapeia o resultado agrupado direto na estrutura esperada pela sua interface
        for row in results:
            currency = row["currency"]
            # is_recurring True mapeia para 'monthly', False mapeia para 'annual'
            period_key = "monthly" if row["is_recurring"] else "annual"
            summary[currency][period_key] = float(row["total"])

        return summary

    def save_entry(self, amount, currency, service, description, username, recurring):
        """Insert a new financial log and return the created record."""
        query = """
            INSERT INTO accounts (amount, currency, service, description, username, is_recurring)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING *;
        """
        parsed_amount = self.parse_brazilian_number(amount)

        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    query,
                    (
                        parsed_amount,
                        currency,
                        service,
                        description,
                        username,
                        recurring,
                    ),
                )
                inserted_row = cur.fetchone()
                conn.commit()
                return inserted_row

    def search_entries(self, query):
        """Search records via partial and case-insensitive matching on service or description."""
        sql_query = """
            SELECT * FROM accounts
            WHERE service ILIKE %s OR description ILIKE %s
            ORDER BY created_at DESC;
        """
        search_term = f"%{query}%"

        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(sql_query, (search_term, search_term))
                return cur.fetchall()


# Create the instance
accounts_service = AccountsService()
