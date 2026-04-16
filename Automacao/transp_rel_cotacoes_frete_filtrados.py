"""
Fluxo para download de cotações de frete com filtros específicos (59, 126, 127).
"""

from Automacao.config_loader import carregar_mapeamento
from Automacao.logger_config import get_logger
from Automacao._download_helper import gerar_download_relatorio

logger = get_logger(__name__)


URL_COTACOES_FRETE_FILTRADOS_PADRAO = (
    "https://logtudo.e-login.net/versoes/versao5.0/rotinas/"
    "c.php?menu=s&id=transp_rel_cotacoesFrete_formulario&filtro=59&filtro=126&filtro=127"
)


def gerar_download_cotacoes_filtradas(
    page,
    url_cotacoes_filtradas: str = None,
    debug: bool = True,
) -> tuple[str, str]:
    """
    Acessa a URL de cotações de frete com filtros específicos (59, 126, 127)
    e realiza o download do relatório.
    
    Args:
        page: Objeto da página Playwright já autenticada
        url_cotacoes_filtradas: URL customizada (usa padrão se não fornecida)
        debug: Se True, salva screenshots em caso de erro
        
    Returns:
        tuple[str, str]: (Caminho completo do arquivo, ID do download)
    """
    mapeamento = carregar_mapeamento()
    
    if url_cotacoes_filtradas is None:
        url_cotacoes_filtradas = mapeamento.get("urls", {}).get(
            "transp_rel_cotacoes_frete_filtrados",
            URL_COTACOES_FRETE_FILTRADOS_PADRAO,
        )
    
    return gerar_download_relatorio(
        page=page,
        url=url_cotacoes_filtradas,
        nome_operacao="DOWNLOAD 2 - Cotações Filtradas",
        debug=debug,
        subpasta="Nao_Faturados/",
        nome_arquivo="relatorio.xls",
    )
