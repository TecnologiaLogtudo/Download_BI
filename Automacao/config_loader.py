"""
Carregador de configurações e mapeamentos para automação.
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, Tuple


def _mapeamento_base() -> Dict[str, Any]:
    """Retorna o fallback final baseado em variáveis de ambiente."""
    return {
        "urls": {
            "login": os.getenv("LOGTUDO_URL", "https://www.logtudo.com.br/login"),
            "transp_rel_cotacoes_frete_formulario": os.getenv(
                "LOGTUDO_URL_COTACOES_FRETE",
                "https://logtudo.e-login.net/versoes/versao5.0/rotinas/"
                "c.php?id=transp_rel_cotacoesFrete_formulario&menu=s&filtro=152",
            ),
        },
        "selectors": {
            "campo_usuario": os.getenv("LOGTUDO_USER_SELECTOR", "input[name='usuario']"),
            "campo_senha": os.getenv("LOGTUDO_PASS_SELECTOR", "input[name='senha']"),
            "botao_entrar": os.getenv("LOGTUDO_SUBMIT_SELECTOR", "button[type='submit']"),
        },
    }


def _merge_mapeamento(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    """
    Mescla somente seções conhecidas para permitir fallback por chave.
    """
    merged = {
        "urls": dict(base.get("urls", {})),
        "selectors": dict(base.get("selectors", {})),
    }
    for section in ("urls", "selectors"):
        if isinstance(override.get(section), dict):
            merged[section].update(override[section])
    return merged


def _carregar_mapeamento_com_origem() -> Tuple[Dict[str, Any], str]:
    """
    Carrega o mapeamento de URLs e seletores.

    Ordem de resolução:
    1) mapeamento.json na raiz do projeto
    2) Automacao/mapeamento.json (retrocompatibilidade)
    3) fallback por variáveis de ambiente/defaults

    Returns:
        Tupla (mapeamento_final, origem_utilizada).
    """
    base_dir = Path(__file__).resolve().parent
    root_file = base_dir.parent / "mapeamento.json"
    local_file = base_dir / "mapeamento.json"
    base = _mapeamento_base()

    for config_file, source_name in (
        (root_file, "mapeamento.json (raiz)"),
        (local_file, "Automacao/mapeamento.json"),
    ):
        if config_file.exists():
            with open(config_file, "r", encoding="utf-8") as f:
                loaded = json.load(f)
            return _merge_mapeamento(base, loaded), source_name

    return base, "fallback (.env/defaults)"


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
