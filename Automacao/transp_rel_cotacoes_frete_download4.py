"""
Fluxo para download de conhecimento de fretes.
Este módulo tem lógica especial pois abre uma nova página após gerar relatório.
"""

import os
import re
import time

from Automacao.config_loader import carregar_mapeamento

from Automacao.logger_config import get_logger

logger = get_logger(__name__)


URL_CONHECIMENTO_FRETE_PADRAO = (
    "https://logtudo.e-login.net/versoes/versao5.0/rotinas/"
    "c.php?id=trans_rel_conhecimento_formulario&menu=s&filtro=167"
)

URL_RELATORIO_CARREGA = (
    "https://logtudo.e-login.net/versoes/versao5.0/relatorios/carrega_relatorio2.php"
)


def gerar_download_conhecimento_frete(
    page,
    url_conhecimento: str = None,
    debug: bool = True,
) -> str:
    """
    Acessa a URL de conhecimento de fretes, gera relatório (abre nova página)
    e realiza o download do arquivo Excel.
    
    Args:
        page: Objeto da página Playwright já autenticada
        url_conhecimento: URL customizada (usa padrão se não fornecida)
        debug: Se True, salva screenshots em caso de erro
        
    Returns:
        str: Caminho do arquivo salvo
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

        # Verifica se estamos na URL esperada
        current_url = new_page.url
        logger.info(f"[DOWNLOAD 4 - Conhecimento Frete] URL atual: {current_url}")

        # O botão de Excel está dentro de um Iframe
        logger.info("[DOWNLOAD 4 - Conhecimento Frete] Procurando botão de Excel dentro dos Iframes...")
        
        # Estratégia robusta: Procurar o frame que contém a imagem de download
        # O seletor da imagem pode variar (acentos, maiúsculas), por isso usamos seletores múltiplos e parciais
        seletores_excel = [
            'img[alt*="Excel"]',
            'img[title*="Excel"]',
            'img[alt*="excel"]',
            'img[title*="excel"]',
            'a:has(img[alt*="excel"])',
            'a:has(img[title*="excel"])'
        ]
        
        # Tenta encontrar o frame correto com retentativas
        frame_download = None
        for tentativa in range(5):
            logger.info(f"[DOWNLOAD 4 - Conhecimento Frete] Tentativa {tentativa + 1} de localizar frame...")
            
            for frame in new_page.frames:
                try:
                    for seletor in seletores_excel:
                        if frame.locator(seletor).count() > 0:
                            frame_download = frame
                            seletor_excel = seletor
                            logger.info(f"[DOWNLOAD 4 - Conhecimento Frete] Frame encontrado: {frame.name or frame.url}")
                            logger.info(f"[DOWNLOAD 4 - Conhecimento Frete] Seletor bem-sucedido: {seletor}")
                            break
                    if frame_download: break
                except:
                    continue
            
            if frame_download:
                break
            
            time.sleep(2) # Aguarda frames carregarem/estabilizarem

        if not frame_download:
            # Fallback para o primeiro iframe se nada for encontrado dinamicamente
            logger.info("[DOWNLOAD 4 - Conhecimento Frete] Nenhum frame encontrado dinamicamente, tentando frame_locator('iframe').first")
            frame_download = new_page.frame_locator('iframe').first
            seletor_excel = 'img[alt*="excel"], img[alt*="Excel"], [title*="excel"]'

        logger.info("[DOWNLOAD 4 - Conhecimento Frete] Clicando no ícone Excel...")
        try:
            # Aumentado timeout para 10 minutos para suportar geração de arquivos grandes
            with new_page.expect_download(timeout=600000) as download_info:
                # Tenta clicar com o seletor identificado ou fallback robusto
                try:
                    frame_download.locator(seletor_excel).first.click(timeout=15000)
                except Exception as e:
                    logger.warning(f"[DOWNLOAD 4 - Conhecimento Frete] Falha no clique primário, tentando clicar por texto/alt genérico: {e}")
                    # Tenta um clique mais genérico como última alternativa
                    frame_download.locator('img[alt*="xcel"], [title*="xcel"]').first.click(timeout=15000)
        except Exception as e:
            logger.error(f"[DOWNLOAD 4 - Conhecimento Frete] Erro ao iniciar download: {e}")
            raise

        download = download_info.value
        filename = download.suggested_filename or "Conhecimento_Frete.xls"
        
        # Cria a pasta downloads com subpasta específica
        base_path = os.path.join("downloads", "PASTA BI - OCORRENCIAS")
        os.makedirs(base_path, exist_ok=True)
        save_path = os.path.join(base_path, filename)
        # Salva o arquivo permanentemente
        download.save_as(save_path)

        logger.info(f"[DOWNLOAD 4 - Conhecimento Frete] ✓ Download concluído e salvo em: {save_path}")

        return save_path

    except Exception as e:
        logger.error(f"[DOWNLOAD 4 - Conhecimento Frete] ✗ Erro na interação: {e}")
        if debug:
            screenshot_path = "erro_download4_relatorio.png"
            page.screenshot(path=screenshot_path)
            logger.info(f"[DOWNLOAD 4 - Conhecimento Frete] Screenshot de erro salva em: {screenshot_path}")
        raise