import os
# from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

class AccountsService:
    def __init__(self):
        url = os.environ.get("SUPABASE_URL") or ""
        key = os.environ.get("SUPABASE_KEY") or ""
        self.supabase: Client = create_client(url, key)

    def parse_brazilian_number(self, value):
        if isinstance(value, str):
            # Converts "1.585,43" to 1585.43
            clean_value = value.replace('.', '').replace(',', '.')
            return float(clean_value)
        return float(value)

    def get_financial_summary(self):
        def fetch_sum(recurring_status, curr):
            # We tell Supabase: "Give me records where currency matches AND is_recurring is True/False"
            res = self.supabase.table("accounts") \
                .select("amount") \
                .eq("currency", curr) \
                .eq("is_recurring", recurring_status) \
                .execute()

            # Calculate the sum
            return sum(item['amount'] for item in res.data)

        return {
            'BRL': {
                'monthly': fetch_sum(True, 'BRL'),  # Recurring only
                'annual': fetch_sum(False, 'BRL')   # Non-recurring only
            },
            'USD': {
                'monthly': fetch_sum(True, 'USD'),  # Recurring only
                'annual': fetch_sum(False, 'USD')   # Non-recurring only
            }
        }

    def save_entry(self, amount, currency, service, description, username, recurring):
        data = {
            "amount": self.parse_brazilian_number(amount),
            "currency": currency,
            "service": service,
            "description": description,
            "username": username,
            "is_recurring": recurring
        }
        return self.supabase.table("accounts").insert(data).execute()

    def search_entries(self, query):
        """THIS WAS MISSING: The search method for Supabase"""
        return self.supabase.table("accounts") \
            .select("*") \
            .or_(f"service.ilike.%{query}%,description.ilike.%{query}%") \
            .order("created_at", desc=True) \
            .execute()

# Create the instance
accounts_service = AccountsService()