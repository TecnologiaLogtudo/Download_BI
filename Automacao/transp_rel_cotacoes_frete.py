"""
Fluxo orquestrador para múltiplos downloads de cotações de frete após login.
Realiza login único e executa os 4 downloads em sequência.
"""

import os

from dotenv import load_dotenv

from Automacao.Login import realizar_login_na_pagina
from Automacao.config_loader import carregar_mapeamento
from Automacao.logger_config import get_logger
from Automacao._download_helper import gerar_download_relatorio
from Automacao.transp_rel_cotacoes_frete_filtrados import gerar_download_cotacoes_filtradas
from Automacao.transp_rel_cotacoes_frete_download3 import gerar_download_cotacoes_download3
from Automacao.transp_rel_cotacoes_frete_download4 import gerar_download_conhecimento_frete
from Conectividade.playwright_vps_connect import PlaywrightVPSClient, PlaywrightVPSConfig

logger = get_logger(__name__)


URL_COTACOES_FRETE_PADRAO = (
    "https://logtudo.e-login.net/versoes/versao5.0/rotinas/"
    "c.php?id=transp_rel_cotacoesFrete_formulario&menu=s&filtro=152"
)


def acessar_transp_rel_cotacoes_frete(
    usuario: str,
    senha: str,
    headless: bool = False,
    debug: bool = True,
) -> dict:
    """
    Executa login único e realiza 4 downloads sequenciais mantendo a sessão autenticada.
    
    Returns:
        dict: Dicionário com caminhos dos 4 arquivos baixados
    """
    mapeamento = carregar_mapeamento()
    url_cotacoes = mapeamento.get("urls", {}).get(
        "transp_rel_cotacoes_frete_formulario",
        URL_COTACOES_FRETE_PADRAO,
    )

    config = PlaywrightVPSConfig(headless=headless, timeout_ms=60000)
    arquivos_baixados = {}

    with PlaywrightVPSClient(config) as client:
        page = client.page

        # Login único no início
        logger.info("=" * 60)
        logger.info("INICIANDO AUTOMAÇÃO DE DOWNLOADS DE COTAÇÕES")
        logger.info("=" * 60)
        
        realizar_login_na_pagina(
            page=page,
            usuario=usuario,
            senha=senha,
            mapeamento=mapeamento,
            debug=debug,
        )

        # Download 1: Cotações padrão (filtro 152)
        try:
            logger.info("\n[ETAPA 1/4] Iniciando primeiro download...")
            arquivos_baixados["download_1"] = gerar_download_relatorio(
                page=page,
                url=url_cotacoes,
                nome_operacao="DOWNLOAD 1 - Cotações Padrão",
                debug=debug,
                subpasta="Faturados/",
                nome_arquivo="relatorio.xls",
            )
            print("✓ PRIMEIRO DOWNLOAD CONCLUÍDO COM SUCESSO!")
        except Exception as e:
            logger.error(f"✗ Erro no Download 1: {e}")
            raise

        # Download 2: Cotações com filtros específicos
        try:
            logger.info("\n[ETAPA 2/4] Iniciando segundo download...")
            print("Prosseguindo para o segundo download com filtros específicos...")
            arquivos_baixados["download_2"] = gerar_download_cotacoes_filtradas(
                page=page,
                debug=debug,
            )
            print("✓ SEGUNDO DOWNLOAD CONCLUÍDO COM SUCESSO!")
        except Exception as e:
            logger.error(f"✗ Erro no Download 2: {e}")
            raise

        # Download 3: Cotações filtro 151
        try:
            logger.info("\n[ETAPA 3/4] Iniciando terceiro download...")
            print("Prosseguindo para o terceiro download...")
            arquivos_baixados["download_3"] = gerar_download_cotacoes_download3(
                page=page,
                debug=debug,
            )
            print("✓ TERCEIRO DOWNLOAD CONCLUÍDO COM SUCESSO!")
        except Exception as e:
            logger.error(f"✗ Erro no Download 3: {e}")
            raise

        # Download 4: Conhecimento de fretes
        try:
            logger.info("\n[ETAPA 4/4] Iniciando quarto download...")
            print("Prosseguindo para o quarto download...")
            arquivos_baixados["download_4"] = gerar_download_conhecimento_frete(
                page=page,
                debug=debug,
            )
            print("✓ QUARTO DOWNLOAD CONCLUÍDO COM SUCESSO!")
        except Exception as e:
            logger.error(f"✗ Erro no Download 4: {e}")
            raise

    # Resumo final
    logger.info("\n" + "=" * 60)
    logger.info("AUTOMAÇÃO COMPLETA FINALIZADA COM SUCESSO!")
    logger.info("=" * 60)
    print("\n" + "=" * 60)
    print("RESUMO DOS DOWNLOADS:")
    print("=" * 60)
    for chave, caminho in arquivos_baixados.items():
        print(f"✓ {chave}: {caminho}")
    print("=" * 60)
    
    return arquivos_baixados


if __name__ == "__main__":
    load_dotenv()
    usuario = os.getenv("LOGTUDO_USER", "")
    senha = os.getenv("LOGTUDO_PASS", "")

    if not usuario or not senha:
        raise ValueError("Defina LOGTUDO_USER e LOGTUDO_PASS no arquivo .env")

    acessar_transp_rel_cotacoes_frete(usuario, senha, headless=True, debug=True)