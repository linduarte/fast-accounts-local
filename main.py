from nicegui import ui
from accounts_service import accounts_service

class FinanceApp:
    def __init__(self):
        self.m_brl = None
        self.a_brl = None
        self.m_usd = None
        self.a_usd = None
        self.service_input = None
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
            ui.notify(f"Cloud Offline: {e}", color='negative')

    async def handle_save(self):
        s_val = self.service_input.value
        a_val = self.amount_input.value
        c_val = self.currency_input.value
        d_val = self.desc_input.value
        r_val = self.recurring_check.value

        if not s_val or not a_val:
            ui.notify('Service and Amount are required!', color='negative')
            return

        try:
            # Username is handled here, hidden from the UI
            accounts_service.save_entry(
                amount=a_val,
                currency=c_val,
                service=s_val,
                description=d_val,
                username="Charles Duarte", 
                recurring=r_val
            )
            ui.notify(f"✅ Synced: {s_val}", color='positive')
            
            self.service_input.value = ''
            self.amount_input.value = ''
            self.desc_input.value = ''
            self.refresh_dashboard()
            self.service_input.run_method('focus')
            
        except Exception as e:
            ui.notify(f"Sync Failed: {e}", color='negative')

    def build_ui(self):
        with ui.column().classes('w-full max-w-4xl mx-auto p-4'):
            with ui.row().classes('w-full items-center justify-between mb-4'):
                ui.label("Fast Accounts Local").classes('text-h4 text-grey-8')
                with ui.row().classes('items-center gap-2'):
                    ui.label('Cloud Status').classes('text-grey-6 text-xs uppercase tracking-wider')
                    self.cloud_status = ui.icon('cloud', size='md').classes('text-grey-400')

            # --- Dashboard ---
            with ui.row().classes('w-full gap-4 mb-8'):
                with ui.card().classes('bg-blue-50 p-4 flex-1 shadow border-l-4 border-blue-400'):
                    ui.label('🇧🇷 BRL TOTALS').classes('text-bold text-blue-800')
                    self.m_brl = ui.label('--')
                    self.a_brl = ui.label('--')

                with ui.card().classes('bg-green-50 p-4 flex-1 shadow border-l-4 border-green-400'):
                    ui.label('🇺🇸 USD TOTALS').classes('text-bold text-green-800')
                    self.m_usd = ui.label('--')
                    self.a_usd = ui.label('--')

            # --- Form ---
            with ui.card().classes('w-full p-6 shadow-lg'):
                with ui.row().classes('w-full gap-4'):
                    self.service_input = ui.input(label='Service').classes('flex-grow')
                    self.amount_input = ui.input(label='Amount').classes('w-32')
                    self.currency_input = ui.select(['BRL', 'USD'], value='BRL', label='Currency').classes('w-24')

                self.desc_input = ui.input(label='Description/Notes').classes('w-full mt-2')
                
                with ui.row().classes('w-full items-center justify-between mt-6'):
                    self.recurring_check = ui.checkbox('Recurring')
                    ui.button('SAVE TO SUPABASE', on_click=self.handle_save).classes('px-10 bg-slate-800 text-white')

            self.refresh_dashboard()

app = FinanceApp()
ui.page('/')(app.build_ui)
ui.run(port=8087, title="Fast Accounts 2026", reload=False)