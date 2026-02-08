from nicegui import ui
from accounts_service import accounts_service

# --- 1. Helper Functions ---
def format_currency(value, currency):
    """Formats numbers to localized Brazilian or US styles."""
    if currency == 'BRL':
        return f"R$ {value:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
    return f"$ {value:,.2f}"

@ui.page('/')
def index():
    # --- 2. State & Data Handling ---
    dark = ui.dark_mode()
    all_rows = []  # Local cache for searching

    def refresh_all():
        """Top-level refresh for stats and the table list."""
        nonlocal all_rows
        try:
            # Update Dashboard Totals
            stats = accounts_service.get_financial_summary()
            m_brl.set_text(f"Monthly: {format_currency(stats['BRL']['monthly'], 'BRL')}")
            a_brl.set_text(f"Annual: {format_currency(stats['BRL']['annual'], 'BRL')}")
            m_usd.set_text(f"Monthly: {format_currency(stats['USD']['monthly'], 'USD')}")
            a_usd.set_text(f"Annual: {format_currency(stats['USD']['annual'], 'USD')}")
            
            # Update Cloud Status
            cloud_status.set_text('Cloud: Online')
            cloud_status.classes('text-green-500', remove='text-red-500')
            
            # Update Search Grid
            all_rows = accounts_service.fetch_all_records()
            update_grid_filter()
        except Exception as e:
            cloud_status.set_text('Cloud: Offline')
            cloud_status.classes('text-red-500', remove='text-green-500')
            ui.notify(f"Sync Error: {e}", color='negative')

    def update_grid_filter():
        """Filters the AgGrid rows based on search input."""
        search_val = search_input.value.lower()
        filtered = [
            row for row in all_rows 
            if search_val in row.get('service', '').lower() 
            or search_val in row.get('description', '').lower()
        ]
        grid.options['rowData'] = filtered
        grid.update()

    # --- 3. UI: Header Bar ---
    with ui.row().classes('w-full justify-between items-center mb-4 p-2'):
        with ui.row().classes('items-center gap-2'):
            ui.icon('cloud').classes('text-2xl')
            cloud_status = ui.label('Connecting...').classes('font-bold')
        
        with ui.row().classes('items-center gap-2'):
            ui.button(icon='light_mode', on_click=dark.disable).props('flat round')
            ui.button(icon='dark_mode', on_click=dark.enable).props('flat round')

    ui.label("Charles Duarte's Accounts").classes('text-h4 mb-4')

    # --- 4. UI: Dashboard Cards ---
    with ui.row().classes('w-full gap-4 mb-6'):
        with ui.card().classes('bg-blue-100 dark:bg-blue-900 p-4 flex-1 shadow-sm'):
            ui.label('🇧🇷 BRL Overview').classes('text-bold text-lg')
            m_brl = ui.label('Monthly: R$ 0,00')
            a_brl = ui.label('Annual: R$ 0,00')
        
        with ui.card().classes('bg-green-100 dark:bg-green-900 p-4 flex-1 shadow-sm'):
            ui.label('🇺🇸 USD Overview').classes('text-bold text-lg')
            m_usd = ui.label('Monthly: $ 0.00')
            a_usd = ui.label('Annual: $ 0.00')

    # --- 5. UI: Search and Table ---
    with ui.card().classes('w-full mb-6 p-4'):
        with ui.row().classes('w-full items-center gap-4'):
            search_input = ui.input(label='Filter Service or Details', on_change=update_grid_filter) \
                .props('outlined icon=search').classes('flex-grow')
            ui.button(icon='refresh', on_click=refresh_all).props('flat color=primary')

        grid = ui.aggrid({
            'columnDefs': [
                {'headerName': 'Service', 'field': 'service', 'sortable': True},
                {'headerName': 'Amount', 'field': 'amount', 'width': 100},
                {'headerName': 'Currency', 'field': 'currency', 'width': 90},
                {'headerName': 'User', 'field': 'username', 'width': 120},
                {'headerName': 'Date', 'field': 'created_at', 'width': 150},
                {'headerName': 'Recurr.', 'field': 'recurring_billing', 'width': 90},
            ],
            'rowData': [],
            'pagination': True,
            'paginationPageSize': 5
        }).classes('w-full h-64 mt-2')

    # --- 6. UI: Entry Form ---
    with ui.card().classes('w-full p-6 shadow-lg'):
        ui.label('Add New Record').classes('text-xl font-bold mb-4')
        
        with ui.row().classes('w-full gap-4'):
            service_in = ui.input(label='Service Name').classes('flex-grow')
            user_in = ui.input(label='Username/Account').classes('flex-grow')
            recurr_in = ui.checkbox('Recurring')

        with ui.row().classes('w-full items-start gap-4 mt-2'):
            amount_in = ui.input(label='Amount (0,00)').classes('w-40')
            curr_in = ui.select(['BRL', 'USD'], value='BRL', label='Currency').classes('w-32')
            desc_in = ui.input(label='Notes').classes('flex-grow')
        
        async def handle_save():
            if not amount_in.value or not service_in.value:
                ui.notify("Error: Amount and Service are required", color='negative')
                return
            
            try:
                accounts_service.save_entry(
                    amount_in.value, curr_in.value, service_in.value, 
                    user_in.value, recurr_in.value, desc_in.value
                )
                ui.notify(f"Successfully saved {service_in.value}!", color='positive')
                
                # Clear Form
                amount_in.value = ''
                service_in.value = ''
                user_in.value = ''
                desc_in.value = ''
                recurr_in.value = False
                
                # Global Refresh
                refresh_all()
            except Exception as e:
                ui.notify(f"Cloud Save Failed: {e}", color='negative')

        ui.button('Save to Supabase', on_click=handle_save).classes('w-full mt-6 text-lg')

    # Initial page load data fetch
    refresh_all()

ui.run(port=8086, title="Fast Accounts Local", reload=True)