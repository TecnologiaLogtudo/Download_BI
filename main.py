#!/usr/bin/env python3
"""
Script principal para automação de Download de BI do Logtudo.

Este script orquestra o processo de login, download e processamento de relatórios.
Certifique-se de ter um arquivo .env configurado com as credenciais.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Adicionar o diretório raiz ao path para imports locais
sys.path.insert(0, str(Path(__file__).parent))

from Automacao.logger_config import configure_logging, get_logger
from Automacao.transp_rel_cotacoes_frete import acessar_transp_rel_cotacoes_frete


def main():
    """Função principal que executa a automação."""
    
    # Carregar variáveis de ambiente do arquivo .env
    load_dotenv()
    configure_logging()
    logger = get_logger(__name__)
    
    # Obter credenciais do ambiente
    usuario = os.getenv("LOGTUDO_USER")
    senha = os.getenv("LOGTUDO_PASS")
    
    if not usuario or not senha:
        logger.error("Erro: Credenciais não configuradas!")
        logger.error("Configure seu arquivo .env com LOGTUDO_USER e LOGTUDO_PASS")
        sys.exit(1)
    
    # Obter configurações opcionais
    headless = os.getenv("HEADLESS", "true").lower() == "true"
    debug = os.getenv("DEBUG", "true").lower() == "true"
    
    logger.info("Iniciando automação Logtudo")
    logger.info("Usuário: %s", usuario)
    logger.info("Modo headless: %s", headless)
    logger.info("Debug ativo: %s", debug)
    
    try:
        # Etapa 1: Login + navegação para cotações de frete
        logger.info("Etapa 1: Realizando login e acessando cotações de frete...")
        acessar_transp_rel_cotacoes_frete(usuario, senha, headless=headless, debug=debug)
        logger.info("Fluxo de login e navegação concluído com sucesso")
        logger.info("Automação concluída com sucesso")
        
    except Exception as e:
        logger.exception("Erro durante execução")
        sys.exit(1)


if __name__ == "__main__":
    main()
