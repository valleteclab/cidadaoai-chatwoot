#!/usr/bin/env python3
"""
Script para testar a integração com a API do Chatwoot
"""
import os
import asyncio
import httpx
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

CHATWOOT_URL = os.getenv("CHATWOOT_URL", "https://chat.sisgov.app.br")
CHATWOOT_API_TOKEN = os.getenv("CHATWOOT_API_TOKEN")

async def test_chatwoot_api():
    """Testar conexão com API do Chatwoot"""
    
    if not CHATWOOT_API_TOKEN:
        print("❌ CHATWOOT_API_TOKEN não configurado!")
        return False
    
    print(f"🔗 Testando conexão com Chatwoot...")
    print(f"URL: {CHATWOOT_URL}")
    print(f"Token: {CHATWOOT_API_TOKEN[:10]}...")
    
    headers = {
        "api_access_token": CHATWOOT_API_TOKEN,
        "Content-Type": "application/json"
    }
    
    try:
        async with httpx.AsyncClient() as client:
            # Testar endpoint de contas
            print("\n1. Testando endpoint de contas...")
            print(f"URL testada: {CHATWOOT_URL}/api/v1/accounts")
            response = await client.get(f"{CHATWOOT_URL}/api/v1/accounts", headers=headers)
            
            if response.status_code == 200:
                accounts = response.json()
                print(f"✅ Contas encontradas: {len(accounts.get('payload', []))}")
                
                for account in accounts.get('payload', []):
                    print(f"   - ID: {account.get('id')}, Nome: {account.get('name')}")
                
                # Testar conversas da primeira conta
                if accounts.get('payload'):
                    account_id = accounts['payload'][0]['id']
                    print(f"\n2. Testando conversas da conta {account_id}...")
                    
                    conv_response = await client.get(
                        f"{CHATWOOT_URL}/api/v1/accounts/{account_id}/conversations",
                        headers=headers
                    )
                    
                    if conv_response.status_code == 200:
                        conversations = conv_response.json()
                        print(f"✅ Conversas encontradas: {len(conversations.get('payload', []))}")
                        
                        for conv in conversations.get('payload', [])[:3]:  # Mostrar apenas 3
                            print(f"   - ID: {conv.get('id')}, Status: {conv.get('status')}")
                            print(f"     Contato: {conv.get('meta', {}).get('sender', {}).get('name', 'N/A')}")
                    else:
                        print(f"❌ Erro ao buscar conversas: {conv_response.status_code}")
                        print(f"   Resposta: {conv_response.text}")
                
                return True
            else:
                print(f"❌ Erro na API: {response.status_code}")
                print(f"   Resposta: {response.text[:500]}...")
                
                # Tentar endpoint alternativo
                print("\n🔄 Tentando endpoint alternativo...")
                alt_response = await client.get(f"{CHATWOOT_URL}/api/v1/accounts/1", headers=headers)
                if alt_response.status_code == 200:
                    print("✅ Endpoint alternativo funcionou!")
                    return True
                
                return False
                
    except Exception as e:
        print(f"❌ Erro de conexão: {str(e)}")
        return False

async def test_webhook_endpoint():
    """Testar endpoint de webhook"""
    print("\n3. Testando endpoint de webhook...")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://localhost:8000/webhook/test",
                json={"test": "message"}
            )
            
            if response.status_code == 200:
                print("✅ Endpoint de webhook funcionando")
                return True
            else:
                print(f"❌ Erro no webhook: {response.status_code}")
                return False
                
    except Exception as e:
        print(f"❌ Erro ao testar webhook: {str(e)}")
        return False

async def main():
    """Função principal"""
    print("🚀 Testando integração com Chatwoot API\n")
    
    # Testar API do Chatwoot
    api_ok = await test_chatwoot_api()
    
    # Testar webhook local
    webhook_ok = await test_webhook_endpoint()
    
    print("\n" + "="*50)
    print("📊 RESUMO DOS TESTES:")
    print(f"   API Chatwoot: {'✅ OK' if api_ok else '❌ FALHOU'}")
    print(f"   Webhook Local: {'✅ OK' if webhook_ok else '❌ FALHOU'}")
    
    if api_ok and webhook_ok:
        print("\n🎉 Todos os testes passaram! Integração pronta.")
    else:
        print("\n⚠️  Alguns testes falharam. Verifique as configurações.")

if __name__ == "__main__":
    asyncio.run(main())
