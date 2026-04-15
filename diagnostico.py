#!/usr/bin/env python3
"""
Script de diagnóstico para verificar conectividade e status do servidor Logtudo.
"""

import sys
import socket
import time
from pathlib import Path
from urllib.parse import urlparse

sys.path.insert(0, str(Path(__file__).parent))

from Automacao.config_loader import carregar_mapeamento


def testar_conectividade_dns(hostname: str) -> bool:
    """Testa se o hostname pode ser resolvido."""
    try:
        print(f"🔍 Testando DNS para: {hostname}")
        ip = socket.gethostbyname(hostname)
        print(f"   ✅ DNS resolvido: {hostname} → {ip}")
        return True
    except socket.gaierror as e:
        print(f"   ❌ Erro ao resolver DNS: {e}")
        return False


def testar_conectividade_socket(hostname: str, porta: int = 443) -> bool:
    """Testa conexão TCP/SSL."""
    try:
        print(f"🔍 Testando conexão TCP para: {hostname}:{porta}")
        socket.create_connection((hostname, porta), timeout=5)
        print(f"   ✅ Conexão TCP bem sucedida")
        return True
    except (socket.timeout, socket.error) as e:
        print(f"   ❌ Erro na conexão: {e}")
        return False


def testar_com_playwright(url: str) -> None:
    """Testa acesso à URL com Playwright."""
    try:
        from Conectividade.playwright_vps_connect import PlaywrightVPSClient, PlaywrightVPSConfig
        
        print(f"🔍 Testando com Playwright: {url}")
        config = PlaywrightVPSConfig(headless=True, timeout_ms=15000)
        
        with PlaywrightVPSClient(config) as client:
            print("   📄 Acessando URL...")
            response = client.page.goto(url, wait_until="domcontentloaded")
            
            if response:
                status = response.status
                print(f"   Status HTTP: {status}")
                
                if status == 503:
                    print(f"   ⚠️  Servidor retornou 503 - Service Unavailable")
                    print(f"      O servidor pode estar offline ou bloqueando requisições automatizadas")
                elif status == 200:
                    print(f"   ✅ Página carregada com sucesso!")
                else:
                    print(f"   ⚠️  Status inesperado: {status}")
            else:
                print(f"   ❌ Resposta vazia")
                
    except Exception as e:
        print(f"   ❌ Erro ao acessar com Playwright: {e}")


def main():
    """Executa diagnóstico completo."""
    
    print("=" * 70)
    print("🔧 DIAGNÓSTICO - Conectividade Logtudo")
    print("=" * 70)
    
    # Carregar configuração
    mapeamento = carregar_mapeamento()
    url_login = mapeamento["urls"]["login"]
    
    print(f"\n📍 URL alvo: {url_login}\n")
    
    # Parse URL
    parsed = urlparse(url_login)
    hostname = parsed.hostname
    porta = parsed.port or 443
    
    print(f"   Hostname: {hostname}")
    print(f"   Porta: {porta}")
    print()
    
    # Teste 1: DNS
    print("📝 TESTE 1: Resolução DNS")
    print("-" * 70)
    dns_ok = testar_conectividade_dns(hostname)
    print()
    
    if not dns_ok:
        print("❌ Falha na resolução DNS. Possível problema:")
        print("   - Servidor DNS não respondendo")
        print("   - Sem conexão com internet")
        print("   - Hostname incorreto")
        return
    
    # Teste 2: Socket
    print("📝 TESTE 2: Conectividade TCP/SSL")
    print("-" * 70)
    socket_ok = testar_conectividade_socket(hostname, porta)
    print()
    
    if not socket_ok:
        print("❌ Falha na conexão. Possível problema:")
        print("   - Servidor offline")
        print("   - Firewall bloqueando")
        print("   - Problema de rota de rede")
        return
    
    # Teste 3: HTTP com Playwright
    print("📝 TESTE 3: Acesso HTTP/HTTPS com Playwright")
    print("-" * 70)
    testar_com_playwright(url_login)
    print()
    
    print("=" * 70)
    print("\n🔹 Interpretação do erro 503:")
    print("   • Código 503 = Service Unavailable")
    print("   • Possíveis causas:")
    print("     1. Servidor realmente offline (manutenção)")
    print("     2. Bloqueio anti-bot (detecção de Playwright)")
    print("     3. Rate limiting")
    print("     4. Firewall/proxy corporativo")
    print()
    print("🔹 Soluções:")
    print("   • Tente acessar manualmente: " + url_login)
    print("   • Aguarde alguns minutos e tente novamente")
    print("   • Verifique se a URL está correta em mapeamento.json")
    print("   • Configure VPN/proxy se necessário")
    print("   • Contate o suporte do Logtudo")
    print()


if __name__ == "__main__":
    main()
