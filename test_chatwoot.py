import httpx
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

CHATWOOT_URL = os.getenv("CHATWOOT_URL", "https://chat.sisgov.app.br")
CHATWOOT_API_TOKEN = os.getenv("CHATWOOT_API_TOKEN")

print(f"🔧 Testando API do Chatwoot:")
print(f"URL: {CHATWOOT_URL}")
print(f"Token: {CHATWOOT_API_TOKEN[:5]}...{CHATWOOT_API_TOKEN[-5:]}")

# Testar API
headers = {
    "api_access_token": CHATWOOT_API_TOKEN,
    "Content-Type": "application/json"
}

# Testar endpoint de perfil
print("\n1. Testando /api/v1/profile")
response = httpx.get(f"{CHATWOOT_URL}/api/v1/profile", headers=headers)
print(f"Status: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    print(f"Accounts: {[acc.get('id') for acc in data.get('accounts', [])]}")
else:
    print(f"Error: {response.text}")

# Testar endpoint de contas
print("\n2. Testando /api/v1/accounts")
response = httpx.get(f"{CHATWOOT_URL}/api/v1/accounts", headers=headers)
print(f"Status: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    print(f"Data: {data}")
else:
    print(f"Error: {response.text}")

# Testar endpoint de conversas
print("\n3. Testando /api/v1/accounts/1/conversations")
response = httpx.get(f"{CHATWOOT_URL}/api/v1/accounts/1/conversations", headers=headers)
print(f"Status: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    print(f"Data: {data}")
else:
    print(f"Error: {response.text}")
