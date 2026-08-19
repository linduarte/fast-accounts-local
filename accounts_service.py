"""Accounts service for Neon/PostgreSQL-backed financial data."""

import os

import psycopg
from dotenv import load_dotenv
from psycopg.rows import dict_row

# Garante o carregamento do ambiente na leitura do módulo
load_dotenv()


class AccountsService:
    """Service class for managing bank account data layers."""

    def __init__(self) -> None:
        self._connection_string = None

    @property
    def connection_string(self) -> str:
        """Busca a string de conexão diretamente do ambiente de forma segura."""
        url = os.environ.get("DATABASE_URL")

        if not url:
            raise ValueError("ERRO CRÍTICO: DATABASE_URL está vazia no arquivo .env!")

        return url

    def _get_connection(self):
        """Creates and returns a new connection to the PostgreSQL backend."""
        return psycopg.connect(self.connection_string, row_factory=dict_row)

    def get_financial_summary(self) -> dict:
        """Return recurring and projected annual financial totals by currency."""
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

        for row in results:
            currency = row["currency"]
            total = float(row["total"])

            if currency not in summary:
                continue

            if row["is_recurring"]:
                # Soma o valor no mensal e projeta o ciclo de 12 meses no ano
                summary[currency]["monthly"] += total
                summary[currency]["annual"] += total * 12
            else:
                # Cobranças avulsas/anuais entram diretamente no total anual
                summary[currency]["annual"] += total

        return summary

    def save_entry(
        self,
        amount: str | float | int,
        currency: str,
        service: str,
        description: str,
        username: str,
        recurring: bool,
    ) -> dict:
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

    def parse_brazilian_number(self, value: str | float | int) -> float:
        """Parse a Brazilian-formatted number (e.g. '1.234,56') into a float.

        Accepts numeric types or strings. Returns float.
        """
        if value is None:
            raise ValueError("amount cannot be None")

        if isinstance(value, (int, float)):
            return float(value)

        s = str(value).strip()
        s = s.replace(".", "").replace(",", ".")

        try:
            return float(s)
        except ValueError as exc:
            raise ValueError(
                f"Unable to parse Brazilian number from: {value}"
            ) from exc

    def search_entries(self, query: str) -> list[dict]:
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


# Singleton instance
accounts_service = AccountsService()