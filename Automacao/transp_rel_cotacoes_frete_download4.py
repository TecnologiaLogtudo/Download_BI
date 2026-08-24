"""
Fluxo para download de conhecimento de fretes (Download 4).
Utiliza popup window e o frame topo para capturar a planilha gerada.
"""

import os
import re
import time
from pathlib import Path
from datetime import datetime

from Automacao.config_loader import carregar_mapeamento
from Automacao.logger_config import get_logger
from Automacao.config_pastas import DOWNLOADS_DIR_ATIVO
from Automacao.metadata_manager import metadata_manager

logger = get_logger(__name__)

URL_CONHECIMENTO_FRETE_PADRAO = (
    "https://logtudo.e-login.net/versoes/versao5.0/rotinas/"
    "c.php?id=trans_rel_conhecimento_formulario&menu=s&filtro=167"
)


def obter_intervalo_mes_atual() -> tuple[str, str]:
    now = datetime.now()
    primeiro_dia = f"01/{now.month:02d}/{now.year}"
    hoje = now.strftime("%d/%m/%Y")
    return primeiro_dia, hoje


def gerar_download_conhecimento_frete(
    page,
    url_conhecimento: str = None,
    debug: bool = True,
) -> tuple[str, str]:
    """
    Acessa a URL de conhecimento de fretes, abre popup do relatório e faz o download.
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
    time.sleep(2)

    logger.info("[DOWNLOAD 4 - Conhecimento Frete] Localizando botão 'Gerar Relatório'...")
    botao_gerar = page.locator("#botao_cadastrar, input[name='botao_finalizacao'], input.swbotao_download, input[value*='Relatório']").first
    botao_gerar.wait_for(state="attached", timeout=30000)
    botao_gerar.scroll_into_view_if_needed()
    botao_gerar.wait_for(state="visible", timeout=10000)

    logger.info("[DOWNLOAD 4 - Conhecimento Frete] Clicando no botão 'Gerar Relatório' e aguardando popup...")

    try:
        with page.expect_popup(timeout=60000) as popup_info:
            botao_gerar.click()

        page1 = popup_info.value
        logger.info("[DOWNLOAD 4 - Conhecimento Frete] Nova janela do relatório detectada! Aguardando carregamento...")
        page1.wait_for_load_state("networkidle", timeout=30000)

        logger.info("[DOWNLOAD 4 - Conhecimento Frete] Baixando planilha via frame topo...")
        with page1.expect_download(timeout=60000) as download_info:
            try:
                page1.locator('frame[name="topo"]').content_frame.locator("a").nth(3).click(timeout=15000)
            except Exception:
                page1.locator('frame[name="topo"]').content_frame.locator('img[alt*="excel"], img[title*="excel"], img[src*="excel"]').first.click(timeout=15000)

        download = download_info.value
        logger.info(f"[DOWNLOAD 4 - Conhecimento Frete] ✓ Download capturado com sucesso: {download.suggested_filename}")

        filename = download.suggested_filename or "Conhecimento_Frete.xls"
        filename = re.sub(r"^.*Detalhado", "Padrao_Detalhado", filename, flags=re.IGNORECASE)

        base_path = DOWNLOADS_DIR_ATIVO / "PASTA_BI_OCORRENCIAS"
        base_path.mkdir(parents=True, exist_ok=True)
        save_path = base_path / filename

        download.save_as(str(save_path))

        download_id = metadata_manager.registrar_download(
            operacao="DOWNLOAD 4 - Conhecimento Frete",
            url=page1.url,
            caminho=str(save_path)
        )

        logger.info(f"[DOWNLOAD 4 - Conhecimento Frete] ✓ Download concluído e registrado [ID: {download_id}]")

        try:
            page1.close()
        except Exception:
            pass

        return str(save_path), download_id

    except Exception as e:
        logger.error(f"[DOWNLOAD 4 - Conhecimento Frete] ✗ Erro no Download 4: {e}")
        if debug:
            try:
                debug_dir = DOWNLOADS_DIR_ATIVO / "debug"
                debug_dir.mkdir(parents=True, exist_ok=True)
                page.screenshot(path=str(debug_dir / "erro_download_4.png"))
            except Exception:
                pass
        raise
