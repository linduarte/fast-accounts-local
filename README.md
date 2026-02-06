📄 README.md (fast-accounts-local)
🧾 Fast Accounts Local
High-Speed Financial Data Management for CNPJs & NFS-e

Lead Engineer: Charles Duarte

Status: Local Production

🚀 Overview
Fast Accounts Local is a specialized desktop application designed for the rapid management and processing of accounting data. Built with Python and NiceGUI, it leverages a local-first architecture to ensure that sensitive financial data remains processed on the local machine without exposure to external cloud databases.

📂 Project Structure

```plaintext
fast-accounts-local/
├── main.py               # UI (NiceGUI) and Entry Point
├── accounts_service.py   # Business Logic & Supabase CRUD
├── .env                  # (Hidden) Your Supabase Keys
├── .gitignore            # Security Gatekeeper
└── pyproject.toml        # Dependencies (uv)
```

🛠️ 1. The Service Layer (accounts_service.py)
Instead of putting database calls in your UI, you now centralize them here. This makes your code much easier to test and reuse.

```python
import os
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

    def fetch_accounts(self):
        """Example: Get all records from your table."""
        return self.supabase.table("accounts").select("*").execute()

    def add_entry(self, data: dict):
        """Example: Insert a new financial record."""
        return self.supabase.table("accounts").insert(data).execute()

# Create a single instance to be used by the app
accounts_service = AccountsService()
```

### 🛠️ 2. The Main UI (`main.py`)

Your UI now simply "asks" the service for data, keeping the file clean and focused on the user experience.

```python
from nicegui import ui
from accounts_service import accounts_service

@ui.page('/')
def index():
    ui.label("Charles Duarte's Fast Accounts").classes('text-h4')
    
    async def load_data():
        try:
            response = accounts_service.fetch_accounts()
            ui.notify(f"Loaded {len(response.data)} records")
            # Render your table/cards here...
        except Exception as e:
            ui.notify(f"Error: {e}", color='negative')

    ui.button('Sync with Supabase', on_click=load_data)

ui.run(port=8086) # Using 8086 to avoid conflict with Git Guardian
```

### 🛠️ 3. The Security Guard (`.gitignore`)

Since we deleted the `data` folder, we want to make sure no other artifacts sneak into your GitHub repo.

```plaintext
# Python / UV
.venv/
__pycache__/

# Security (CRITICAL)
.env

# Supabase Local Settings
supabase/
.temp/
```

### 🧠 Why this is a "Belo Horizonte Engineering" Win:

- **Decoupling:** If you ever decide to switch from Supabase to another database, you only change `accounts_service.py`. The rest of your app remains untouched.

- **Security:** Your `.env` holds the keys, and your `.gitignore` hides the `.env`.

- **Simplicity:** No more `data` folder means no more messy CSV exports. Your "Single Source of Truth" is now in the cloud.

**Charles, since we're using Supabase now, would you like me to help you draft the SQL command to create your first 'accounts' table with the correct columns for CNPJ and NFS-e?**
