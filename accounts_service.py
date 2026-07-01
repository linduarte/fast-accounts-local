"""Accounts service for Neon/PostgreSQL-backed financial data."""

import os

import psycopg
from dotenv import load_dotenv
from psycopg.rows import dict_row

load_dotenv()


class AccountsService:
    """Service to interact with the accounts PostgreSQL table."""

    def __init__(self):
        # String de conexão padrão do Postgres/Neon vinda do ambiente
        self.connection_string = os.environ.get("DATABASE_URL") or ""

    def _get_connection(self):
        """Helper connection context manager with dictionary row output."""
        if not self.connection_string:
            raise ValueError("DATABASE_URL environment variable is missing.")
       # Conexão direta e limpa usando Psycopg 3
        return psycopg.connect(self.connection_string, row_factory=dict_row)
    def parse_brazilian_number(self, value):
        """Parse a Brazilian-formatted number string into a float."""
        if isinstance(value, str):
            # Converts "1.585,43" to 1585.43
            clean_value = value.replace(".", "").replace(",", ".")
            return float(clean_value)
        return float(value)

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
