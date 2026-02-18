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

---

This message received from Supabase make this below process to avoid "Pausing"

Hi there,


To optimize cloud resources, we automatically pause free-tier projects after 7 days of inactivity.

Your project fast accounts project (ID: jtgzslsfnmzjthgiyjpp) from your organization linduarte has been paused.

You can unpause your project from the dashboard within 90 days. After this period, the project cannot be restored, but your data will remain available for download. View documentation for details.

To prevent future automatic pausing, upgrade to Pro from your billing settings.

## 💤 Preventing Project Pausing (Keep-Alive System)

The Supabase Free Tier automatically pauses projects after 7 days of inactivity. To ensure the application remains always-on, a "Heartbeat" system has been implemented.

### 🛠️ Components

1.  **`keep_alive.py`**: A lightweight script that performs a minimal query to the database to reset the activity timer.
2.  **`keep_alive.bat`**: A Windows batch file to trigger the script within the `uv` environment.
3.  **Windows Task Scheduler**: Automates the heartbeat execution.

### ⚙️ Automation Setup

To keep your project active indefinitely, follow these steps:

1.  **Create the Batch File**: Ensure `keep_alive.bat` points to your project directory:
    ```batch
    @echo off
    cd /d "C:\YOUR_PROJECT_PATH\fast-accounts-local"
    uv run keep_alive.py
    ```
2.  **Configure Task Scheduler**:
    * **Trigger**: Weekly (e.g., every Monday at 10:00 AM).
    * **Action**: Start a program.
    * **Program/script**: Path to your `keep_alive.bat`.
    * **Setting**: Enable "Run task as soon as possible after a scheduled start is missed" to ensure it runs even if the PC was off during the scheduled time.



### 🔍 Connection Debugging
If the script returns `[Errno 11001] getaddrinfo failed`, your project is likely already paused. Log in to the Supabase Dashboard and click **Restore** before running the heartbeat script again.
