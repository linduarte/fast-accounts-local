🧾 Fast Accounts Local
Lead Engineer: Charles Duarte

Status: Local Production

🚀 Overview
Fast Accounts Local is a specialized desktop application designed for the rapid management and processing of accounting data. Built with Python and NiceGUI, it leverages a local-first architecture to ensure that sensitive financial data remains processed on the local machine without exposure to external cloud databases.



# 🏦 Fast-Accounts-Local v1.2

A streamlined financial dashboard built with **Python**, **NiceGUI**, and **Supabase**. This application allows for quick tracking of recurring expenses versus one-off investments with a cloud-synced backend.

## 🚀 Key Features

* **Smart Totals:** Automatically separates your finances into two distinct buckets:
  * **Monthly (Fixed):** Sum of all services marked as **Recurring**.
  * **Annual (Variable):** Sum of all entries **not** marked as recurring.
* **Search Resource:** High-speed search bar with "Click-to-Edit" functionality to quickly update existing service values.
* **Cloud Sync:** Real-time synchronization with Supabase for data persistence.
* **Dual Currency:** Native support for **BRL (R$)** and **USD ($)** with Brazilian number formatting (comma decimal).

## 🛠️ Tech Stack

* **Frontend:** [NiceGUI](https://nicegui.io/) (Python-based UI framework)
* **Backend:** [Supabase](https://supabase.com/) (PostgreSQL & API)
* **Environment:** [uv](https://github.com/astral-sh/uv) (Fast Python package manager)

## 📋## 🏃 How to Run

To launch the application, open your terminal in the project folder and run:

```env
uv run main.py
```

The app will be available at `http://localhost:8087`.

📂 Project Structure

- `main.py`: The UI layer and application state. Handles rendering and user interaction.

- `accounts_service.py`: The logic layer. Manages data formatting, Supabase queries, and financial calculations.

- `.env`: Sensitive credentials (ignored by git).

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
        url = os.environ.get("SUPABASE_URL") or ""
        key = os.environ.get("SUPABASE_KEY") or ""
        self.supabase: Client = create_client(url, key)
... code continue
```

### 🛠️ 2. The Main UI (`main.py`)

Your UI now simply "asks" the service for data, keeping the file clean and focused on the user experience.

```python
from accounts_service import accounts_service
from nicegui import ui


class FinanceApp:
    def __init__(self):
        self.m_brl = None
        self.a_brl = None
        self.m_usd = None
        self.a_usd = None
        self.servic... code continuee_input = None
        self.amount_input = None
        self.currency_input = None
        self.desc_input = None
        self.recurring_check = None
        self.cloud_status = None

    def format_display(self, value, currency):
        if currency == 'BRL':
            return f"R$ {value:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
        return f"$ {value:,.2f}"

    def refresh_dashboard(self):
        try:
            stats = accounts_service.get_financial_summary()
            self.m_brl.set_text(f"Monthly: {self.format_display(stats['BRL']['monthly'], 'BRL')}")
            self.a_brl.set_text(f"Annual: {self.format_display(stats['BRL']['annual'], 'BRL')}")
            self.m_usd.set_text(f"Monthly: {self.format_display(stats['USD']['monthly'], 'USD')}")
            self.a_usd.set_text(f"Annual: {self.format_display(stats['USD']['annual'], 'USD')}")
            
            # Corrected icon update logic
            self.cloud_status.props('name=cloud') 
            self.cloud_status.classes(replace='text-green-500')
        except Exception as e:
            self.cloud_status.props('name=cloud_off')
            self.cloud_status.classes(replace='text-red-500')
            ui.notify(f"Clo... code continued Offline: {e}", color='negative')
... code continue
```

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
