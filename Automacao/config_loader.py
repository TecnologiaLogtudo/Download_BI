"""
Carregador de configurações e mapeamentos para automação.
Gerencia a resolução de URLs e seletores com suporte a prioridade
por variáveis de ambiente (.env/sistema) sobre arquivos estáticos (JSON).
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, List, Tuple
from dotenv import load_dotenv

# Mapeamento de chaves de URL para variáveis de ambiente correspondentes (em ordem de prioridade)
# Suporta nomes semânticos correspondentes ao relatório baixado (ex: faturados, cancelados)
ENV_URL_MAPPINGS: Dict[str, List[str]] = {
    "login": [
        "LOGTUDO_URL_LOGIN",
        "LOGTUDO_URL",
    ],
    "transp_rel_cotacoes_frete_formulario": [
        "LOGTUDO_URL_FATURADOS",
        "LOGTUDO_URL_COTACOES_FATURADOS",
        "LOGTUDO_URL_COTACOES_FRETE",
        "LOGTUDO_URL_DOWNLOAD_1",
    ],
    "transp_rel_cotacoes_frete_filtrados": [
        "LOGTUDO_URL_NAO_FATURADOS",
        "LOGTUDO_URL_COTACOES_NAO_FATURADOS",
        "LOGTUDO_URL_COTACOES_FILTRADAS",
        "LOGTUDO_URL_DOWNLOAD_2",
    ],
    "transp_rel_cotacoes_frete_download3": [
        "LOGTUDO_URL_CANCELADOS",
        "LOGTUDO_URL_COTACOES_CANCELADOS",
        "LOGTUDO_URL_COTACOES_DOWNLOAD3",
        "LOGTUDO_URL_DOWNLOAD_3",
    ],
    "trans_rel_conhecimento_frete": [
        "LOGTUDO_URL_CONHECIMENTO_FRETE",
        "LOGTUDO_URL_OCORRENCIAS",
        "LOGTUDO_URL_DOWNLOAD_4",
    ],
}

# Fallbacks padrão caso não estejam definidos no .env nem no mapeamento.json
DEFAULTS_URLS: Dict[str, str] = {
    "login": "https://logtudo.e-login.net/",
    "transp_rel_cotacoes_frete_formulario": (
        "https://logtudo.e-login.net/versoes/versao5.0/rotinas/"
        "c.php?id=transp_rel_cotacoesFrete_formulario&menu=s&filtro=201"
    ),
    "transp_rel_cotacoes_frete_filtrados": (
        "https://logtudo.e-login.net/versoes/versao5.0/rotinas/"
        "c.php?id=transp_rel_cotacoesFrete_formulario&menu=s&filtro=202"
    ),
    "transp_rel_cotacoes_frete_download3": (
        "https://logtudo.e-login.net/versoes/versao5.0/rotinas/"
        "c.php?id=transp_rel_cotacoesFrete_formulario&menu=s&filtro=151"
    ),
    "trans_rel_conhecimento_frete": (
        "https://logtudo.e-login.net/versoes/versao5.0/rotinas/"
        "c.php?id=trans_rel_conhecimento_formulario&menu=s&filtro=167"
    ),
}

ENV_SELECTOR_MAPPINGS: Dict[str, List[str]] = {
    "campo_usuario": ["LOGTUDO_USER_SELECTOR"],
    "campo_senha": ["LOGTUDO_PASS_SELECTOR"],
    "botao_entrar": ["LOGTUDO_SUBMIT_SELECTOR"],
}

DEFAULTS_SELECTORS: Dict[str, str] = {
    "campo_usuario": "input[name='usuario']",
    "campo_senha": "input[name='senha']",
    "botao_entrar": "#botaoSubmit",
    "msg_erro_login": "p:has-text('O Usuário ou a Senha estão incorretos')",
    "botao_gerar_relatorio": "#botao_cadastrar, input[name='botao_finalizacao'], input.swbotao_download",
}

DEFAULTS_ERROS: Dict[str, str] = {
    "login_invalido": "O Usuário ou a Senha estão incorretos",
}


# Carrega variáveis do .env na inicialização do módulo se presente
load_dotenv()


def _carregar_mapeamento_com_origem(recarregar_env: bool = False) -> Tuple[Dict[str, Any], str]:
    """
    Carrega o mapeamento de URLs, seletores e erros.

    Ordem de resolução de valores por chave:
    1) Variáveis de ambiente (.env ou sistema) - prioridade máxima
    2) mapeamento.json na raiz do projeto
    3) Automacao/mapeamento.json (retrocompatibilidade)
    4) Defaults internos do sistema

    Returns:
        Tupla (mapeamento_final, origem_utilizada).
    """
    if recarregar_env:
        load_dotenv()

    base_dir = Path(__file__).resolve().parent
    root_file = base_dir.parent / "mapeamento.json"
    local_file = base_dir / "mapeamento.json"

    file_data: Dict[str, Any] = {}
    source_name = "defaults internos"

    for config_file, src in (
        (root_file, "mapeamento.json (raiz)"),
        (local_file, "Automacao/mapeamento.json"),
    ):
        if config_file.exists():
            try:
                with open(config_file, "r", encoding="utf-8") as f:
                    file_data = json.load(f)
                source_name = src
                break
            except Exception:
                pass

    # Inicia com os defaults e mescla com os dados do arquivo JSON
    urls = dict(DEFAULTS_URLS)
    if isinstance(file_data.get("urls"), dict):
        urls.update(file_data["urls"])

    selectors = dict(DEFAULTS_SELECTORS)
    if isinstance(file_data.get("selectors"), dict):
        selectors.update(file_data["selectors"])

    erros = dict(DEFAULTS_ERROS)
    if isinstance(file_data.get("erros"), dict):
        erros.update(file_data["erros"])

    # Sobrescreve URLs caso haja variáveis de ambiente definidas
    env_urls_used = []
    for key, env_vars in ENV_URL_MAPPINGS.items():
        for env_var in env_vars:
            val = os.getenv(env_var)
            if val is not None and val.strip():
                urls[key] = val.strip()
                env_urls_used.append(env_var)
                break

    # Sobrescreve seletores caso haja variáveis de ambiente definidas
    for key, env_vars in ENV_SELECTOR_MAPPINGS.items():
        for env_var in env_vars:
            val = os.getenv(env_var)
            if val is not None and val.strip():
                selectors[key] = val.strip()
                break

    if env_urls_used:
        source_name = f"{source_name} + variáveis de ambiente ({', '.join(env_urls_used)})"

    mapeamento_final = {
        "urls": urls,
        "selectors": selectors,
        "erros": erros,
    }

    return mapeamento_final, source_name


def carregar_mapeamento() -> Dict[str, Any]:
    """
    Retorna o mapeamento final para uso da automação.
    """
    mapeamento, _ = _carregar_mapeamento_com_origem()
    return mapeamento


def obter_origem_mapeamento() -> str:
    """
    Informa de qual fonte o mapeamento foi carregado.
    """
    _, origem = _carregar_mapeamento_com_origem()
    return origem
