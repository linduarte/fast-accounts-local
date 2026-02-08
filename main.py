from nicegui import ui
from accounts_service import accounts_service

def format_currency(value, currency):
    if currency == 'BRL':
        return f"R$ {value:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
    return f"$ {value:,.2f}"

@ui.page('/')
def index():
    # --- Theme State ---
    dark = ui.dark_mode()

    def refresh_stats():
        try:
            stats = accounts_service.get_financial_summary()
            m_brl.set_text(f"Monthly: {format_currency(stats['BRL']['monthly'], 'BRL')}")
            a_brl.set_text(f"Annual: {format_currency(stats['BRL']['annual'], 'BRL')}")
            m_usd.set_text(f"Monthly: {format_currency(stats['USD']['monthly'], 'USD')}")
            a_usd.set_text(f"Annual: {format_currency(stats['USD']['annual'], 'USD')}")
            cloud_status.set_text('Cloud: Online')
            cloud_status.classes('text-green-500', remove='text-red-500')
        except Exception as e:
            cloud_status.set_text('Cloud: Offline')
            cloud_status.classes('text-red-500', remove='text-green-500')
            ui.notify(f"Connection Error: {e}", color='negative')

    # --- Header Bar (Status & Theme) ---
    with ui.row().classes('w-full justify-between items-center mb-4 p-2'):
        with ui.row().classes('items-center gap-2'):
            ui.icon('cloud').classes('text-2xl')
            cloud_status = ui.label('Checking...').classes('font-bold')
        
        with ui.row().classes('items-center gap-4'):
            ui.button(icon='light_mode', on_click=dark.disable).props('flat round')
            ui.button(icon='dark_mode', on_click=dark.enable).props('flat round')

    ui.label("Charles Duarte's Accounts").classes('text-h4 mb-4')

    # --- Totals Dashboard ---
    with ui.row().classes('w-full gap-4 mb-8'):
        with ui.card().classes('bg-blue-100 dark:bg-blue-900 p-4 flex-1'):
            ui.label('🇧🇷 BRL Totals').classes('text-bold text-lg')
            m_brl = ui.label('Monthly: R$ 0,00')
            a_brl = ui.label('Annual: R$ 0,00')
        with ui.card().classes('bg-green-100 dark:bg-green-900 p-4 flex-1'):
            ui.label('🇺🇸 USD Totals').classes('text-bold text-lg')
            m_usd = ui.label('Monthly: $ 0.00')
            a_usd = ui.label('Annual: $ 0.00')

    # --- Entry Form ---
    with ui.card().classes('w-full p-6 shadow-lg'):
        ui.label('Add New Financial Record').classes('text-xl font-bold mb-4')
        
        with ui.row().classes('w-full gap-4'):
            service_in = ui.input(label='Service').classes('flex-grow')
            user_in = ui.input(label='Username/Account').classes('flex-grow')
            recurring_in = ui.checkbox('Recurring Billing')

        with ui.row().classes('w-full items-start gap-4 mt-2'):
            amount_in = ui.input(label='Amount', placeholder='0,00').classes('w-40')
            curr_in = ui.select(['BRL', 'USD'], value='BRL', label='Currency').classes('w-32')
            desc_in = ui.input(label='Description').classes('flex-grow')
        
        async def handle_save():
            if not amount_in.value or not service_in.value:
                ui.notify("Error: Amount and Service are required", color='negative')
                return
            
            try:
                accounts_service.save_entry(
                    amount_in.value, curr_in.value, service_in.value, 
                    user_in.value, recurring_in.value, desc_in.value
                )
                ui.notify(f"Saved {service_in.value}", color='positive')
                amount_in.value = ''
                service_in.value = ''
                user_in.value = ''
                desc_in.value = ''
                recurring_in.value = False
                refresh_stats()
            except Exception:
                ui.notify("Failed to save to Cloud", color='negative')

        ui.button('Save to Supabase', on_click=handle_save).classes('w-full mt-6')

    refresh_stats()

ui.run(port=8086, title="Fast Accounts Local")