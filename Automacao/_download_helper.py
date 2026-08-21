"""
Helper genérico para realizar downloads de relatórios com Playwright.
Encapsula a lógica comum de navegação, busca de botão e download.
"""

import os
import re
from pathlib import Path

from Automacao.logger_config import get_logger
from Automacao.config_pastas import DOWNLOADS_DIR_ATIVO
from Automacao.metadata_manager import metadata_manager

logger = get_logger(__name__)


def gerar_download_relatorio(
    page,
    url: str,
    nome_operacao: str = "Download",
    debug: bool = True,
    subpasta: str = "",
    nome_arquivo: str = None,
) -> tuple[str, str]:
    """
    Função genérica para acessar uma URL, localizar botão "Gerar Relatório"
    e fazer download do arquivo.
    
    Args:
        page: Objeto da página Playwright já autenticada
        url: URL a acessar
        nome_operacao: Nome descritivo da operação (para logs)
        debug: Se True, salva screenshots em caso de erro
        subpasta: Subpasta dentro de 'downloads' (ex: 'Faturados/')
        nome_arquivo: Nome customizado do arquivo
        
    Returns:
        tuple[str, str]: (Caminho completo do arquivo, ID do download no metadados)
        
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

        # Tratar alertas JS na página (ex: "Nenhum registro encontrado")
        def tratar_dialogo(dialog):
            logger.warning(f"[{nome_operacao}] Alerta JS detectado: '{dialog.message}'. Aceitando...")
            try:
                dialog.accept()
            except Exception as err:
                logger.warning(f"[{nome_operacao}] Não foi possível aceitar diálogo: {err}")

        page.on("dialog", tratar_dialogo)

        captured_pages = []
        captured_downloads = []

        def on_page(p):
            logger.info(f"[{nome_operacao}] Nova aba/janela detectada!")
            captured_pages.append(p)

        def on_download(d):
            logger.info(f"[{nome_operacao}] Download direto detectado!")
            captured_downloads.append(d)

        # Registrar listeners temporários
        page.context.on("page", on_page)
        page.on("download", on_download)

        logger.info(f"[{nome_operacao}] Clicando no botão 'Gerar Relatório'...")
        botao_gerar.click()

        logger.info(f"[{nome_operacao}] Aguardando resposta do servidor (download direto ou abertura de nova página)...")
        
        # Aguarda até 30s por uma resposta do clique (nova página ou download direto)
        start_time = time.time()
        while time.time() - start_time < 30:
            if captured_pages or captured_downloads:
                break
            time.sleep(0.5)

        # Remover listeners temporários
        try:
            page.context.remove_listener("page", on_page)
        except Exception:
            pass
        try:
            page.remove_listener("download", on_download)
        except Exception:
            pass

        download = None

        if captured_pages:
            nova_pagina = captured_pages[0]
            nova_pagina.on("dialog", tratar_dialogo)
            logger.info(f"[{nome_operacao}] Aguardando carregamento da página do relatório...")
            try:
                nova_pagina.wait_for_load_state("networkidle", timeout=30000)
            except Exception:
                logger.warning(f"[{nome_operacao}] Timeout no 'networkidle' da nova página, continuando...")

            logger.info(f"[{nome_operacao}] Procurando botão de exportação Excel nos Iframes...")
            seletores_excel = [
                'img[alt*="Excel"]',
                'img[title*="Excel"]',
                'img[alt*="excel"]',
                'img[title*="excel"]',
                'a:has(img[alt*="excel"])',
                'a:has(img[title*="excel"])',
                'a:has(img[alt*="Excel"])',
                'a:has(img[title*="Excel"])',
            ]

            frame_download = None
            seletor_excel = ""

            for tentativa in range(5):
                for frame in nova_pagina.frames:
                    try:
                        for seletor in seletores_excel:
                            if frame.locator(seletor).count() > 0:
                                frame_download = frame
                                seletor_excel = seletor
                                break
                        if frame_download:
                            break
                    except Exception:
                        continue
                if frame_download:
                    break
                time.sleep(2)

            if not frame_download:
                logger.info(f"[{nome_operacao}] Usando fallback para frame locator...")
                frame_download = nova_pagina.frame_locator("iframe").first
                seletor_excel = 'img[alt*="excel"], img[alt*="Excel"]'

            logger.info(f"[{nome_operacao}] Clicando no ícone Excel para gerar o download...")
            with nova_pagina.expect_download(timeout=600000) as download_info:
                try:
                    frame_download.locator(seletor_excel).first.click(timeout=15000)
                except Exception:
                    frame_download.locator('img[alt*="xcel"]').first.click(timeout=15000)

            download = download_info.value
            try:
                nova_pagina.close()
            except Exception:
                pass

        elif captured_downloads:
            download = captured_downloads[0]
        else:
            raise TimeoutError(
                f"[{nome_operacao}] Nenhum download ou nova página de relatório foi gerada em 30s após clicar em 'Gerar Relatório'."
            )

        filename = nome_arquivo if nome_arquivo else (download.suggested_filename if download else "relatorio.xls")
        
        # Define pasta final usando o sistema de persistência robusto
        base_path = DOWNLOADS_DIR_ATIVO
        if subpasta:
            base_path = DOWNLOADS_DIR_ATIVO / subpasta.strip("/")
        
        base_path.mkdir(parents=True, exist_ok=True)
        save_path = base_path / filename
        
        # Salva o arquivo permanentemente
        download.save_as(str(save_path))
        
        # Registra no sistema de metadados
        download_id = metadata_manager.registrar_download(
            operacao=nome_operacao,
            url=url,
            caminho=str(save_path)
        )
        
        logger.info(f"[{nome_operacao}] ✓ Download concluído e registrado [ID: {download_id}]")
        logger.info(f"[{nome_operacao}] Caminho: {save_path}")
        
        return str(save_path), download_id

    except Exception as e:
        logger.error(f"[{nome_operacao}] ✗ Erro na interação com o botão ou download: {e}")
        if debug:
            screenshot_path = f"erro_{nome_operacao.lower().replace(' ', '_')}.png"
            try:
                page.screenshot(path=screenshot_path)
                logger.info(f"[{nome_operacao}] Screenshot de erro salva em: {screenshot_path}")
            except Exception:
                pass
        raise
