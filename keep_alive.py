import os
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client

# Carrega as credenciais do seu arquivo .env atual
load_dotenv()

def poke_supabase():
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")
    
    if not url or not key:
        print(f"[{datetime.now()}] Erro: Variáveis de ambiente SUPABASE_URL e SUPABASE_KEY não configuradas")
        return
    
    try:
        supabase = create_client(url, key)
        # Uma consulta mínima: apenas verifica se há algo na tabela
        # Isso conta como atividade oficial para o Supabase
        supabase.table("accounts").select("id").limit(1).execute()
        
        print(f"[{datetime.now()}] Sucesso: Supabase 'cutucado' com sucesso!")
    except Exception as e:
        print(f"[{datetime.now()}] Erro ao manter o projeto vivo: {e}")

if __name__ == "__main__":
    poke_supabase()