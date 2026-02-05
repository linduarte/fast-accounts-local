# import os
from datetime import datetime
from nicegui import ui
from accounts_service import AccountService

# --- 1. INITIALIZATION ---
try:
    service = AccountService()
except Exception as e:
    # Critical failure if we can't even load the service
    print(f"Initialization Error: {e}")

# --- 2. STATE MANAGEMENT ---
# We use a dictionary to keep track of UI elements we need to update
state = {
    'search_query': '',
    'accounts': []
}

# --- 3. LOGIC & ACTIONS ---
def copy_to_clipboard(text: str):
    """Copies text to the Windows clipboard and notifies the user."""
    ui.run_javascript(f'navigator.clipboard.writeText("{text}")')
    ui.notify(f'Copied: {text}', color='info', icon='content_copy')

def toggle_dark_mode(dark_mode_instance):
    """Toggles between light and dark themes."""
    dark_mode_instance.toggle()
    ui.notify('Theme Switched', pos='bottom-right')



async def check_connection(icon, label, time_label):
    """Heartbeat monitor for cloud connectivity."""
    try:
        service.supabase.table("accounts").select("id").limit(1).execute()
        icon.set_name('cloud_done')
        icon.props('color=green')
        label.set_text('Connected')
        time_label.set_text(f"Sync: {datetime.now().strftime('%H:%M:%S')}")
    except Exception:
        icon.set_name('cloud_off')
        icon.props('color=red')
        label.set_text('Offline')

def load_data(container):
    """Fetch data from cloud and filter based on search input."""
    container.clear()
    state['accounts'] = service.get_all_accounts()
    
    # Filter logic
    filtered = [
        acc for acc in state['accounts'] 
        if state['search_query'].lower() in acc['service'].lower()
    ]

    with container:
        if not filtered:
            ui.label('No matching accounts found.').classes('italic text-slate-400 mx-auto')
            return
            
        for item in filtered:
            with ui.card().classes('w-full mb-3 border-l-4 border-blue-500 shadow-sm'):
                with ui.row().classes('w-full items-center justify-between'):
                    with ui.column():
                        with ui.row().classes('items-center gap-2'):
                            ui.label(item['service']).classes('text-lg font-bold')
                            ui.button(icon='content_copy', on_click=lambda i=item['service']: copy_to_clipboard(i)).props('flat dense size=sm')
                
                        with ui.row().classes('items-center gap-2'):
                            ui.label(item['username']).classes('text-sm text-slate-500')
                            ui.button(icon='content_copy', on_click=lambda i=item['username']: copy_to_clipboard(i)).props('flat dense size=sm color=grey')

async def delete_item(name, container):
    """Delete and refresh."""
    service.delete_account(name)
    ui.notify(f'Deleted {name}', type='info')
    load_data(container)

async def save_new_account(srv, usr, bill, pay, curr, container):
    """Validation and upload."""
    if not srv.value or not usr.value:
        ui.notify('Service and Username are required!', type='warning')
        return
    
    try:
        service.add_account(srv.value, usr.value, bill.value, pay.value, curr.value)
        ui.notify(f'✅ {srv.value} saved!', type='positive')
        srv.value = usr.value = pay.value = '' # Clear inputs
        load_data(container)
    except Exception as e:
        ui.notify(f'Save failed: {e}', type='negative')

# --- 4. UI LAYOUT ---

@ui.page('/')
def main_page():
    # Header Indicators
    status_icon = ui.icon('cloud_off', color='red').classes('text-2xl')
    status_label = ui.label('Offline').classes('text-[10px] text-slate-400')
    sync_time_label = ui.label('Sync: --:--').classes('text-[10px] text-slate-500')

    # Create the dark mode manager at the start of main_page
    dark = ui.dark_mode()

    with ui.header().classes('bg-slate-800 items-center justify-between px-4'):
        with ui.row().classes('items-center gap-3'):
            ui.label('FastAccounts Pro').classes('text-white text-xl font-bold')
            # Account Counter Badge
            ui.badge('', color='orange').bind_text_from(state, 'accounts', backward=lambda x: f"{len(x)} Accounts")
    
        with ui.row().classes('items-center gap-4'):
            # Dark Mode Toggle
            ui.button(icon='dark_mode', on_click=lambda: toggle_dark_mode(dark)).props('flat color=white')
        
            with ui.column().classes('items-center gap-0'):
                status_icon
                status_label
                sync_time_label
            ui.button(icon='refresh', on_click=lambda: load_data(results_container)).props('flat color=white')

    # Search Bar & Input Card
    with ui.column().classes('w-full max-w-2xl mx-auto mt-6 p-2'):
        
        # Search Box
        search = ui.input(placeholder='🔍 Search services...', on_change=lambda e: update_search(e.value))
        search.classes('w-full mb-4').props('rounded outlined')

        def update_search(val):
            state['search_query'] = val
            load_data(results_container)

        # Input Form
        with ui.card().classes('w-full p-6 shadow-md mb-8'):
            ui.label('Add New Record').classes('text-h6 mb-2')
            with ui.grid(columns=2).classes('w-full'):
                srv = ui.input('Service Name')
                usr = ui.input('Username')
                bill = ui.select(['Monthly', 'Yearly', 'One-time'], label='Billing', value='Monthly')
                pay = ui.input('Payment Method')
                curr = ui.select(['BRL', 'USD', 'EUR'], label='Currency', value='BRL')
            
            ui.button('Save to Supabase', 
                      on_click=lambda: save_new_account(srv, usr, bill, pay, curr, results_container)).classes('w-full mt-4')

        # Results Area
        ui.label('Stored Accounts').classes('text-h6 mb-2')
        results_container = ui.column().classes('w-full pb-10')

    # Start Heartbeat & Initial Load
    ui.timer(10.0, lambda: check_connection(status_icon, status_label, sync_time_label))
    load_data(results_container)

# Run
ui.run(native=True, title="FastAccounts Pro", window_size=(600, 850))