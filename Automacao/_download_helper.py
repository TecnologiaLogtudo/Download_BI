"""
Helper genérico para realizar downloads de relatórios com Playwright.
Encapsula a lógica comum de navegação, busca de botão e download.
"""

import calendar
import os
import re
import time
from datetime import datetime
from pathlib import Path

from Automacao.logger_config import get_logger
from Automacao.config_pastas import DOWNLOADS_DIR_ATIVO
from Automacao.metadata_manager import metadata_manager

logger = get_logger(__name__)


def obter_intervalo_mes_atual() -> tuple[str, str]:
    now = datetime.now()
    primeiro_dia = f"01/{now.month:02d}/{now.year}"
    hoje = now.strftime("%d/%m/%Y")
    return primeiro_dia, hoje


def gerar_download_relatorio(
    page,
    url: str,
    nome_operacao: str = "Download",
    debug: bool = True,
    subpasta: str = "",
    nome_arquivo: str = None,
    timeout_resposta: int = 120,
    preencher_datas: bool = False,
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
        timeout_resposta: Tempo limite em segundos aguardando resposta do servidor (padrão 120s)
        preencher_datas: Se True, preenche automaticamente os filtros de data com o mês atual
        
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
    time.sleep(2)

    logger.info(f"[{nome_operacao}] Localizando botão 'Gerar Relatório'...")
    botao_gerar = page.locator("#botao_cadastrar, input[name='botao_finalizacao'], input.swbotao_download, input[name='btPlanilha'], input[value*='Planilha']").first

    try:
        # Garante que o botão está anexado ao DOM
        botao_gerar.wait_for(state="attached", timeout=30000)

        # Scroll para garantir visibilidade
        logger.info(f"[{nome_operacao}] Fazendo scroll até o botão...")
        botao_gerar.scroll_into_view_if_needed()

        # Espera ficar visível e habilitado
        botao_gerar.wait_for(state="visible", timeout=10000)

        # Preencher filtros de data do mês atual automaticamente apenas se solicitado
        if preencher_datas:
            dt_ini, dt_fim = obter_intervalo_mes_atual()
            logger.info(f"[{nome_operacao}] Preenchendo datas do mês atual ({dt_ini} até {dt_fim})...")
            try:
                page.evaluate(
                    f"""() => {{
                        const dtIni = document.querySelector("input[name='dados_dtInicio']");
                        const dtFim = document.querySelector("input[name='dados_dtFim']");
                        const valIni = document.querySelector("input[name='dados_validade_de']");
                        const valFim = document.querySelector("input[name='dados_validade_ate']");
                        
                        if (dtIni) dtIni.value = '{dt_ini}';
                        if (dtFim) dtFim.value = '{dt_fim}';
                        if (valIni) valIni.value = '{dt_ini}';
                        if (valFim) valFim.value = '{dt_fim}';
                    }}"""
                )
            except Exception as e_dt:
                logger.warning(f"[{nome_operacao}] Não foi possível aplicar datas automáticas: {e_dt}")

        try:
            page.evaluate(
                """() => {
                    if (window.SWSM && typeof SWSM.adicionaTodos === 'function') {
                        try { SWSM.adicionaTodos('dados_talao'); } catch (e) {}
                    }
                }"""
            )
        except Exception:
            pass

        # Tratar alertas JS na página (ex: "Nenhum registro encontrado")
        def tratar_dialogo(dialog):
            msg = dialog.message
            logger.warning(f"[{nome_operacao}] Alerta JS detectado: '{msg}'. Aceitando...")
            try:
                dialog.accept()
            except Exception as err:
                logger.warning(f"[{nome_operacao}] Não foi possível aceitar diálogo: {err}")

        page.on("dialog", tratar_dialogo)

        captured_pages = []
        page.context.on("page", lambda p: captured_pages.append(p))

        logger.info(f"[{nome_operacao}] Clicando no botão 'Gerar Relatório' e aguardando download...")
        download = None
        
        try:
            with page.expect_download(timeout=timeout_resposta * 1000) as download_info:
                botao_gerar.click()
            download = download_info.value
            logger.info(f"[{nome_operacao}] ✓ Download capturado diretamente com sucesso!")
        except Exception as err_exp:
            logger.warning(f"[{nome_operacao}] expect_download direto expirou/não capturou ({err_exp}). Verificando se abas de relatórios foram abertas...")
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
            else:
                raise TimeoutError(
                    f"[{nome_operacao}] Nenhum download ou nova página de relatório foi gerada em {timeout_resposta}s após clicar em 'Gerar Relatório'."
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
            try:
                debug_dir = DOWNLOADS_DIR_ATIVO / "debug"
                debug_dir.mkdir(parents=True, exist_ok=True)
                nome_sanitizado = nome_operacao.lower().replace(' ', '_').replace('/', '_')
                screenshot_path = debug_dir / f"erro_{nome_sanitizado}.png"
                page.screenshot(path=str(screenshot_path))
                logger.info(f"[{nome_operacao}] Screenshot de erro salva em: {screenshot_path}")
            except Exception as ss_err:
                logger.warning(f"[{nome_operacao}] Não foi possível salvar screenshot: {ss_err}")
        raise
