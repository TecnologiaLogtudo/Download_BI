"""
Fluxo para download de conhecimento de fretes.
Este módulo tem lógica especial pois abre uma nova página após gerar relatório.
"""

import os
import re
import time
from pathlib import Path

from Automacao.config_loader import carregar_mapeamento
from Automacao.logger_config import get_logger
from Automacao.config_pastas import DOWNLOADS_DIR_ATIVO
from Automacao.metadata_manager import metadata_manager

logger = get_logger(__name__)


URL_CONHECIMENTO_FRETE_PADRAO = (
    "https://logtudo.e-login.net/versoes/versao5.0/rotinas/"
    "c.php?id=trans_rel_conhecimento_formulario&menu=s&filtro=167"
)


def gerar_download_conhecimento_frete(
    page,
    url_conhecimento: str = None,
    debug: bool = True,
) -> tuple[str, str]:
    """
    Acessa a URL de conhecimento de fretes, gera relatório (abre nova página)
    e realiza o download do arquivo Excel.
    
    Args:
        page: Objeto da página Playwright já autenticada
        url_conhecimento: URL customizada (usa padrão se não fornecida)
        debug: Se True, salva screenshots em caso de erro
        
    Returns:
        tuple[str, str]: (Caminho completo do arquivo, ID do download)
    """
    mapeamento = carregar_mapeamento()
    
    if url_conhecimento is None:
        url_conhecimento = mapeamento.get("urls", {}).get(
            "trans_rel_conhecimento_frete",
            URL_CONHECIMENTO_FRETE_PADRAO,
        )

    logger.info("[DOWNLOAD 4 - Conhecimento Frete] Aguardando estabilização da página...")
    try:
        page.wait_for_load_state("networkidle", timeout=15000)
    except Exception:
        logger.warning("[DOWNLOAD 4 - Conhecimento Frete] Timeout no 'networkidle', continuando...")

    logger.info(f"[DOWNLOAD 4 - Conhecimento Frete] Acessando URL: {url_conhecimento}")
    page.goto(url_conhecimento, wait_until="load")

    logger.info("[DOWNLOAD 4 - Conhecimento Frete] Localizando botão 'Gerar Relatório'...")
    botao_gerar = page.get_by_role("button", name=re.compile(r"gerar relatório", re.IGNORECASE))

    try:
        # Garante que o botão está anexado ao DOM
        botao_gerar.wait_for(state="attached", timeout=30000)

        # Scroll para garantir visibilidade
        logger.info("[DOWNLOAD 4 - Conhecimento Frete] Fazendo scroll até o botão...")
        botao_gerar.scroll_into_view_if_needed()

        # Espera ficar visível e habilitado
        botao_gerar.wait_for(state="visible", timeout=10000)

        logger.info("[DOWNLOAD 4 - Conhecimento Frete] Clicando no botão 'Gerar Relatório'...")
        logger.info("[DOWNLOAD 4 - Conhecimento Frete] Aguardando nova página/aba abrir...")

        # Clica no botão e aguarda nova página
        with page.context.expect_page() as new_page_info:
            botao_gerar.click()

        new_page = new_page_info.value
        logger.info("[DOWNLOAD 4 - Conhecimento Frete] Nova página detectada!")

        # Espera a página carregar completamente
        logger.info("[DOWNLOAD 4 - Conhecimento Frete] Aguardando carregamento da página do relatório...")
        new_page.wait_for_load_state("networkidle", timeout=30000)

        # O botão de Excel está dentro de um Iframe
        logger.info("[DOWNLOAD 4 - Conhecimento Frete] Procurando botão de Excel dentro dos Iframes...")
        
        # Estratégia robusta: Procurar o frame que contém a imagem de download
        seletores_excel = [
            'img[alt*="Excel"]',
            'img[title*="Excel"]',
            'img[alt*="excel"]',
            'img[title*="excel"]',
            'a:has(img[alt*="excel"])',
            'a:has(img[title*="excel"])'
        ]
        
        frame_download = None
        seletor_excel = ""
        
        for tentativa in range(5):
            for frame in new_page.frames:
                try:
                    for seletor in seletores_excel:
                        if frame.locator(seletor).count() > 0:
                            frame_download = frame
                            seletor_excel = seletor
                            break
                    if frame_download: break
                except:
                    continue
            if frame_download: break
            time.sleep(2)

        if not frame_download:
            logger.info("[DOWNLOAD 4 - Conhecimento Frete] Usando fallback para frame locator...")
            frame_download = new_page.frame_locator('iframe').first
            seletor_excel = 'img[alt*="excel"], img[alt*="Excel"]'

        logger.info("[DOWNLOAD 4 - Conhecimento Frete] Clicando no ícone Excel...")
        try:
            with new_page.expect_download(timeout=600000) as download_info:
                try:
                    frame_download.locator(seletor_excel).first.click(timeout=15000)
                except:
                    frame_download.locator('img[alt*="xcel"]').first.click(timeout=15000)
        except Exception as e:
            logger.error(f"[DOWNLOAD 4 - Conhecimento Frete] Erro ao iniciar download: {e}")
            raise

        download = download_info.value
        filename = download.suggested_filename or "Conhecimento_Frete.xls"
        
        # Sanitiza nome do arquivo se necessário (Requisito: Padrão Detalhado -> Padrao_detalhado)
        filename = filename.replace("Padrão Detalhado", "Padrao_detalhado")
        
        # Define pasta final robusta
        base_path = DOWNLOADS_DIR_ATIVO / "PASTA_BI_OCORRENCIAS"
        base_path.mkdir(parents=True, exist_ok=True)
        save_path = base_path / filename
        
        # Salva o arquivo permanentemente
        download.save_as(str(save_path))
        
        # Registra no sistema de metadados
        download_id = metadata_manager.registrar_download(
            operacao="DOWNLOAD 4 - Conhecimento Frete",
            url=new_page.url,
            caminho=str(save_path)
        )
        
        logger.info(f"[DOWNLOAD 4 - Conhecimento Frete] ✓ Download concluído e registrado [ID: {download_id}]")
        
        # Fecha a aba do relatório para limpar memória
        new_page.close()

        return str(save_path), download_id

    except Exception as e:
        logger.error(f"[DOWNLOAD 4 - Conhecimento Frete] ✗ Erro na interação: {e}")
        if debug:
            screenshot_path = "erro_download4_relatorio.png"
            page.screenshot(path=screenshot_path)
        raise
