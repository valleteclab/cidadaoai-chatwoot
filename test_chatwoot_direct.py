#!/usr/bin/env python3
"""
Script para testar API do Chatwoot diretamente
"""
import os
import httpx
import json

# Configurações
CHATWOOT_URL = "https://chat.sisgov.app.br"
CHATWOOT_API_TOKEN = "3kcYkVZPwDnRrCgVnLdFgtKY"

async def test_chatwoot_api():
    """Testar API do Chatwoot diretamente"""
    print("🚀 Testando API do Chatwoot diretamente")
    print(f"URL: {CHATWOOT_URL}")
    print(f"Token: {CHATWOOT_API_TOKEN[:10]}...")
    
    headers = {
        "api_access_token": CHATWOOT_API_TOKEN,
        "Content-Type": "application/json"
    }
    
    try:
        async with httpx.AsyncClient() as client:
            # Testar endpoint de conversas
            url = f"{CHATWOOT_URL}/api/v1/accounts/1/conversations"
            print(f"\n📡 Testando: {url}")
            
            response = await client.get(url, headers=headers)
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Sucesso! Dados recebidos:")
                print(f"   Meta: {data.get('data', {}).get('meta', {})}")
                
                payload = data.get('data', {}).get('payload', [])
                print(f"   Conversas encontradas: {len(payload)}")
                
                if payload:
                    print(f"\n📋 Primeira conversa:")
                    conv = payload[0]
                    print(f"   ID: {conv.get('id')}")
                    print(f"   Status: {conv.get('status')}")
                    print(f"   Canal: {conv.get('channel')}")
                    print(f"   Contato: {conv.get('meta', {}).get('sender', {}).get('name', 'N/A')}")
                    print(f"   Telefone: {conv.get('meta', {}).get('sender', {}).get('phone_number', 'N/A')}")
                    
                    messages = conv.get('messages', [])
                    print(f"   Mensagens: {len(messages)}")
                    
                    if messages:
                        last_msg = messages[-1]
                        print(f"   Última mensagem: {last_msg.get('content', 'N/A')}")
                        print(f"   Tipo: {last_msg.get('message_type', 'N/A')} (0=incoming, 1=outgoing)")
                else:
                    print("   ❌ Nenhuma conversa encontrada")
                    
                return data
            else:
                print(f"❌ Erro: {response.status_code}")
                print(f"   Resposta: {response.text[:500]}...")
                return None
                
    except Exception as e:
        print(f"❌ Erro de conexão: {str(e)}")
        return None

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_chatwoot_api())
