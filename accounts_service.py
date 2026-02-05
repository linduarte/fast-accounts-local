import os
from supabase import create_client, Client
from dotenv import load_dotenv

# Load once at the start of the script
load_dotenv()

class AccountService:
    def __init__(self):
        # We fetch the fuel for our machine
        url: str | None = os.getenv("SUPABASE_URL")
        key: str | None = os.getenv("SUPABASE_KEY")
        
        # Engineering Safety Check (Type Guard)
        if url is None or key is None:
            raise ValueError("❌ Critical Error: SUPABASE_URL or KEY is missing from .env!")
        
        # Now the machine is initialized and ready to work
        self.supabase: Client = create_client(url, key)

    def get_all_accounts(self):
        # RESCUED: Matches your FastAPI GET /accounts/
        response = self.supabase.table("accounts").select("*").execute()
        return response.data

    def add_account(self, service, username, billing, payment, currency):
        # RESCUED: Matches your FastAPI POST /accounts/ logic
        data = {
            "service": service,
            "username": username,
            "recurring_billing": billing,
            "payment_method": payment,
            "currency": currency
        }
        return self.supabase.table("accounts").insert(data).execute()

    def delete_account(self, service_name):
        # RESCUED: Matches your FastAPI DELETE /accounts/{service_name}
        return self.supabase.table("accounts").delete().eq("service", service_name).execute()