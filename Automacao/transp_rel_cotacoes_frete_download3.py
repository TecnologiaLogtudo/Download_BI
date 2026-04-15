"""
Fluxo para download de cotações de frete com filtro 151.
"""

from Automacao.config_loader import carregar_mapeamento
from Automacao.logger_config import get_logger
from Automacao._download_helper import gerar_download_relatorio

logger = get_logger(__name__)


URL_COTACOES_FRETE_DOWNLOAD3_PADRAO = (
    "https://logtudo.e-login.net/versoes/versao5.0/rotinas/"
    "c.php?id=transp_rel_cotacoesFrete_formulario&menu=s&filtro=151"
)


def gerar_download_cotacoes_download3(
    page,
    url_download3: str = None,
    debug: bool = True,
) -> str:
    """
    Acessa a URL de cotações de frete com filtro 151 e realiza o download.
    
    Args:
        page: Objeto da página Playwright já autenticada
        url_download3: URL customizada (usa padrão se não fornecida)
        debug: Se True, salva screenshots em caso de erro
        
    Returns:
        str: Caminho do arquivo salvo
    """
    mapeamento = carregar_mapeamento()
    
    if url_download3 is None:
        url_download3 = mapeamento.get("urls", {}).get(
            "transp_rel_cotacoes_frete_download3",
            URL_COTACOES_FRETE_DOWNLOAD3_PADRAO,
        )
    
    return gerar_download_relatorio(
        page=page,
        url=url_download3,
        nome_operacao="DOWNLOAD 3 - Cotações Filtro 151",
        debug=debug,
        subpasta="Cancelados/",
        nome_arquivo="relatorio.xls",
    )