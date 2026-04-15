from typing import Any, Dict, Optional

def verificar_erro_login(page: Any, mapeamento: Dict[str, Any]) -> Optional[str]:
    """
    Verifica se existe uma mensagem de erro de login na página.
    
    Args:
        page: Instância da página Playwright.
        mapeamento: Dicionário de mapeamento com os seletores.
        
    Returns:
        String com a mensagem de erro se encontrada, None caso contrário.
    """
    seletor_erro = mapeamento["selectors"].get("msg_erro_login")
    if not seletor_erro:
        return None

    try:
        # Tenta encontrar o elemento de erro com um timeout curto
        elemento_erro = page.query_selector(seletor_erro)
        if elemento_erro:
            texto_erro = elemento_erro.inner_text()
            return texto_erro.strip()
    except Exception:
        pass
    
    return None
