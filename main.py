from accounts_service import accounts_service
from nicegui import ui


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
    # --- INSERT AFTER handle_save ---
    async def handle_search(self):
        query = self.search_input.value
        if not query:
            ui.notify("Type something to search!", color='warning')
            return
        
        try:
            # This "if" statement is for the editor's benefit.
            # It proves to VS Code that accounts_service IS the right class.
            from accounts_service import AccountsService, accounts_service
            
            if isinstance(accounts_service, AccountsService):
                results = accounts_service.search_entries(query) # type: ignore


            
            self.results_container.clear()
            
            with self.results_container:
                if not results.data:
                    ui.label("No results found.").classes('text-grey italic p-4')
                else:
                    ui.label('Click to load into form:').classes('text-xs text-blue-500 mb-2')
                    for row in results.data:
                        # This creates a clickable result that calls load_for_edit
                        with ui.button(on_click=lambda r=row: self.load_for_edit(r)).classes('w-full p-2 mb-2 bg-white text-black normal-case items-start border shadow-sm'):
                            with ui.row().classes('w-full items-center justify-between no-wrap'):
                                ui.label(row['created_at'][:10]).classes('text-xs text-grey-500')
                                ui.label(row['service']).classes('font-bold flex-grow text-left px-4')
                                ui.label(self.format_display(row['amount'], row['currency']))
        except Exception as e:
            ui.notify(f"Search error: {e}", color='negative')

    def load_for_edit(self, data):
        """Fills the form fields with data from a search result."""
        self.service_input.value = data['service']
        # Convert float back to string with comma for Brazilian format
        self.amount_input.value = str(data['amount']).replace('.', ',')
        self.currency_input.value = data['currency']
        self.desc_input.value = data['description'] or ''
        self.recurring_check.value = data['is_recurring']
        
        ui.notify(f"Loaded {data['service']}", color='info')
        self.amount_input.run_method('focus')            

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
                
                with ui.row().classes('w-full gap-2 mt-4'):
                    self.search_input = ui.input(label='Search', on_change=lambda: ui.timer(0.3, self.handle_search, once=True)).classes('flex-grow')
                    ui.button('SEARCH', on_click=self.handle_search).classes('px-6 bg-blue-600 text-white')
                
                self.results_container = ui.column().classes('w-full mt-2')
                
                with ui.row().classes('w-full items-center justify-between mt-6'):
                    self.recurring_check = ui.checkbox('Recurring')
                    ui.button('SAVE TO SUPABASE', on_click=self.handle_save).classes('px-10 bg-slate-800 text-white')

            self.refresh_dashboard()

app = FinanceApp()
ui.page('/')(app.build_ui)
ui.run(port=8087, title="Fast Accounts 2026", reload=False)