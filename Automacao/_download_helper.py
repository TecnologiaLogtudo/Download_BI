"""
Helper genérico para realizar downloads de relatórios com Playwright.
Encapsula a lógica comum de navegação, busca de botão e download.
"""

import os
import re
from pathlib import Path

from Automacao.logger_config import get_logger

logger = get_logger(__name__)


def gerar_download_relatorio(
    page,
    url: str,
    nome_operacao: str = "Download",
    debug: bool = True,
    subpasta: str = "",
    nome_arquivo: str = None,
) -> str:
    """
    Função genérica para acessar uma URL, localizar botão "Gerar Relatório"
    e fazer download do arquivo.
    
    Args:
        page: Objeto da página Playwright já autenticada
        url: URL a acessar
        nome_operacao: Nome descritivo da operação (para logs)
        debug: Se True, salva screenshots em caso de erro        subpasta: Subpasta dentro de 'downloads' (ex: 'Faturados/')
        nome_arquivo: Nome customizado do arquivo (se None, usa o sugerido)        
    Returns:
        str: Caminho do arquivo salvo
        
    Raises:
        Exception: Se ocorrer erro na interação ou download
    """
    logger.info(f"[{nome_operacao}] Aguardando estabilização da página...")
    try:
        page.wait_for_load_state("networkidle", timeout=15000)
    except Exception:
        logger.warning(f"[{nome_operacao}] Timeout no 'networkidle', continuando...")

    logger.info(f"[{nome_operacao}] Acessando URL: {url}")
    page.goto(url, wait_until="load")

    logger.info(f"[{nome_operacao}] Localizando botão 'Gerar Relatório'...")
    botao_gerar = page.get_by_role("button", name=re.compile(r"gerar relatório", re.IGNORECASE))

    try:
        # Garante que o botão está anexado ao DOM
        botao_gerar.wait_for(state="attached", timeout=30000)

        # Scroll para garantir visibilidade
        logger.info(f"[{nome_operacao}] Fazendo scroll até o botão...")
        botao_gerar.scroll_into_view_if_needed()

        # Espera ficar visível e habilitado
        botao_gerar.wait_for(state="visible", timeout=10000)

        logger.info(f"[{nome_operacao}] Iniciando captura do download e clicando no botão...")
        logger.info(f"[{nome_operacao}] Aguardando download (pode levar alguns minutos para arquivos grandes)...")
        with page.expect_download(timeout=600000) as download_info:
            botao_gerar.click()

        download = download_info.value
        filename = nome_arquivo if nome_arquivo else download.suggested_filename
        
        # Cria a pasta downloads com subpasta se especificada
        base_download_dir = os.getenv("DOWNLOAD_DIR", str(Path(__file__).parent.parent / "downloads"))
        base_path = base_download_dir
        if subpasta:
            base_path = os.path.join(base_download_dir, subpasta.rstrip("/"))
        
        os.makedirs(base_path, exist_ok=True)
        save_path = os.path.join(base_path, filename)
        
        # Salva o arquivo permanentemente
        download.save_as(save_path)
        
        logger.info(f"[{nome_operacao}] ✓ Download concluído e salvo em: {save_path}")
        
        return save_path

    except Exception as e:
        logger.error(f"[{nome_operacao}] ✗ Erro na interação com o botão ou download: {e}")
        if debug:
            screenshot_path = f"erro_{nome_operacao.lower().replace(' ', '_')}.png"
            page.screenshot(path=screenshot_path)
            logger.info(f"[{nome_operacao}] Screenshot de erro salva em: {screenshot_path}")
        raise