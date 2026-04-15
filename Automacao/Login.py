import os
import time
from typing import Any, Dict

from dotenv import load_dotenv

from Conectividade.playwright_vps_connect import PlaywrightVPSConfig, PlaywrightVPSClient
from Automacao.config_loader import carregar_mapeamento, obter_origem_mapeamento
from Automacao.identificador_erros import verificar_erro_login
from Automacao.logger_config import get_logger

logger = get_logger(__name__)


def realizar_login_na_pagina(
    page: Any,
    usuario: str,
    senha: str,
    mapeamento: Dict[str, Any] | None = None,
    debug: bool = True,
) -> None:
    """
    Executa o login usando uma página Playwright já inicializada com lógica de tentativa dupla.

    Args:
        page: Instância da página Playwright em uso.
        usuario: Usuário para login.
        senha: Senha para login.
        mapeamento: Configuração carregada (opcional).
        debug: Se True, exibe mais informações de debug.
    """
    config_login = mapeamento or carregar_mapeamento()
    url_login = config_login["urls"]["login"]
    sel_usuario = config_login["selectors"]["campo_usuario"]
    sel_senha = config_login["selectors"]["campo_senha"]
    sel_entrar = config_login["selectors"]["botao_entrar"]

    if debug:
        origem = obter_origem_mapeamento()
        logger.info("Configuração carregada de: %s", origem)

    def tentar_login(tentativa):
        logger.info("Tentativa %s de login...", tentativa)
        logger.info("Acessando a URL de login...")
        page.goto(url_login, wait_until="domcontentloaded")
        
        logger.info("Aguardando página carregar completamente...")
        time.sleep(2)

        page.wait_for_selector(sel_usuario, timeout=10000)
        page.locator(sel_usuario).fill(usuario)
        page.locator(sel_senha).fill(senha)
        
        logger.info("Clicando no botão Entrar...")
        page.locator(sel_entrar).click()

        logger.info("Aguardando navegação ou erro...")
        time.sleep(3) # Tempo para processar e mostrar erro se houver

        erro = verificar_erro_login(page, config_login)
        if erro:
            logger.warning("Erro de login detectado na tentativa %s: %s", tentativa, erro)
            return False, erro
            
        logger.info("Tentativa %s concluída (sem erro imediato).", tentativa)
        return True, None

    # Primeira tentativa
    sucesso, motivo = tentar_login(1)
    
    if not sucesso:
        print("Re-tentando login pela segunda vez...")
        sucesso, motivo = tentar_login(2)
        
        if not sucesso:
            log_msg = f"FALHA CRÍTICA NO LOGIN: Após duas tentativas, o login falhou pelo motivo: {motivo}"
            print(f"LOG: {log_msg}")
            raise Exception(log_msg)

    print("Aguardando navegação final...")
    try:
        page.wait_for_load_state("load", timeout=15000)
    except Exception:
        print("  ⚠ Timeout no 'load', continuando mesmo assim...")

    time.sleep(2)
    print("✓ Login concluído com sucesso!")


def realizar_login(usuario: str, senha: str, headless: bool = False, debug: bool = True) -> None:
    """
    Executa o login no Logtudo.
    
    Args:
        usuario: Usuário para login
        senha: Senha para login
        headless: Se True, executa sem exibir a janela do navegador
        debug: Se True, exibe mais informações de debug
    """
    mapeamento = carregar_mapeamento()

    config = PlaywrightVPSConfig(headless=headless, timeout_ms=60000)

    with PlaywrightVPSClient(config) as client:
        page = client.page

        try:
            realizar_login_na_pagina(
                page=page,
                usuario=usuario,
                senha=senha,
                mapeamento=mapeamento,
                debug=debug,
            )
        except Exception as e:
            logger.exception("Erro durante login")
            raise


if __name__ == "__main__":
    load_dotenv()
    usuario = os.getenv("LOGTUDO_USER", "ATUALIZARBI")
    senha = os.getenv("LOGTUDO_PASS", "sua_senha_aqui")
    # Desativar headless e ativar debug por padrão ao executar diretamente
    realizar_login(usuario, senha, headless=False, debug=True)
