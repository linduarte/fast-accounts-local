import os
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

class AccountsService:
    def __init__(self):
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")
        if not url or not key:
            raise ValueError("❌ Missing Supabase credentials in .env")
        self.supabase: Client = create_client(url, key)

    def parse_brazilian_number(self, value_str: str) -> float:
        """Converts '1.250,50' into 1250.50 for the database."""
        if not value_str:
            return 0.0
        clean_value = value_str.replace('.', '').replace(',', '.')
        try:
            return float(clean_value)
        except ValueError:
            return 0.0

    def save_entry(self, amount_str, currency, service, username, recurring, description):
        """Saves the complete record with all 6 categories to Supabase."""
        amount = self.parse_brazilian_number(amount_str)
        data = {
            "amount": amount,
            "currency": currency,
            "service": service,
            "username": username,
            "recurring_billing": recurring,
            "description": description
        }
        return self.supabase.table("accounts").insert(data).execute()

    def get_financial_summary(self):
        """Calculates Monthly/Annual totals for BRL and USD."""
        response = self.supabase.table("accounts").select("amount, currency, created_at").execute()
        data = response.data

        now = datetime.now()
        stats = {
            "BRL": {"monthly": 0.0, "annual": 0.0},
            "USD": {"monthly": 0.0, "annual": 0.0}
        }

        for entry in data:
            dt = datetime.fromisoformat(entry['created_at'].replace('Z', '+00:00'))
            amount = float(entry['amount'])
            curr = entry['currency']

            if dt.year == now.year:
                stats[curr]["annual"] += amount
                if dt.month == now.month:
                    stats[curr]["monthly"] += amount

        return stats

accounts_service = AccountsService()