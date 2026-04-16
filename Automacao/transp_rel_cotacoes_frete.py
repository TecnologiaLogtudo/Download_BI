"""
Fluxo orquestrador para múltiplos downloads de cotações de frete após login.
Realiza login único e executa os 4 downloads em sequência com persistência robusta.
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
from Automacao.recovery_manager import RecoveryManager
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
    Executa login único e realiza 4 downloads sequenciais com rastreamento por metadados.
    
    Returns:
        dict: Resumo dos downloads realizados e status de integridade
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

        logger.info("=" * 60)
        logger.info("INICIANDO AUTOMAÇÃO DE DOWNLOADS COM PERSISTÊNCIA ROBUSTA")
        logger.info("=" * 60)
        
        realizar_login_na_pagina(
            page=page,
            usuario=usuario,
            senha=senha,
            mapeamento=mapeamento,
            debug=debug,
        )

        # Download 1: Cotações padrão
        try:
            logger.info("\n[ETAPA 1/4] DOWNLOAD 1 - Cotações Padrão")
            caminho, d_id = gerar_download_relatorio(
                page=page,
                url=url_cotacoes,
                nome_operacao="DOWNLOAD 1",
                debug=debug,
                subpasta="Faturados/",
                nome_arquivo="relatorio.xls",
            )
            arquivos_baixados["download_1"] = {"caminho": caminho, "id": d_id}
            print(f"✓ DOWNLOAD 1 OK [ID: {d_id}]")
        except Exception as e:
            logger.error(f"✗ Erro no Download 1: {e}")
            raise

        # Download 2: Cotações com filtros específicos
        try:
            logger.info("\n[ETAPA 2/4] DOWNLOAD 2 - Cotações Filtradas")
            caminho, d_id = gerar_download_cotacoes_filtradas(page=page, debug=debug)
            arquivos_baixados["download_2"] = {"caminho": caminho, "id": d_id}
            print(f"✓ DOWNLOAD 2 OK [ID: {d_id}]")
        except Exception as e:
            logger.error(f"✗ Erro no Download 2: {e}")
            raise

        # Download 3: Cotações filtro 151
        try:
            logger.info("\n[ETAPA 3/4] DOWNLOAD 3 - Cotações Filtro 151")
            caminho, d_id = gerar_download_cotacoes_download3(page=page, debug=debug)
            arquivos_baixados["download_3"] = {"caminho": caminho, "id": d_id}
            print(f"✓ DOWNLOAD 3 OK [ID: {d_id}]")
        except Exception as e:
            logger.error(f"✗ Erro no Download 3: {e}")
            raise

        # Download 4: Conhecimento de fretes
        try:
            logger.info("\n[ETAPA 4/4] DOWNLOAD 4 - Conhecimento Frete")
            caminho, d_id = gerar_download_conhecimento_frete(page=page, debug=debug)
            arquivos_baixados["download_4"] = {"caminho": caminho, "id": d_id}
            print(f"✓ DOWNLOAD 4 OK [ID: {d_id}]")
        except Exception as e:
            logger.error(f"✗ Erro no Download 4: {e}")
            raise

        # Verificação final de integridade física dos arquivos
        logger.info("\n" + "-" * 30)
        logger.info("REALIZANDO VERIFICAÇÃO DE INTEGRIDADE...")
        integridade = RecoveryManager.verificar_integridade()
        
        logger.info(f"Arquivos confirmados no disco: {len(integridade['existentes'])}")
        if integridade['perdidos']:
            logger.warning(f"Arquivos não localizados: {len(integridade['perdidos'])}")
            for p in integridade['perdidos']:
                logger.warning(f"  - {p}")

    logger.info("\n" + "=" * 60)
    logger.info("AUTOMAÇÃO FINALIZADA COM SUCESSO!")
    logger.info("=" * 60)
    
    return arquivos_baixados


if __name__ == "__main__":
    load_dotenv()
    usuario = os.getenv("LOGTUDO_USER", "")
    senha = os.getenv("LOGTUDO_PASS", "")

    if not usuario or not senha:
        raise ValueError("Defina LOGTUDO_USER e LOGTUDO_PASS no arquivo .env")

    acessar_transp_rel_cotacoes_frete(usuario, senha, headless=False, debug=True)
