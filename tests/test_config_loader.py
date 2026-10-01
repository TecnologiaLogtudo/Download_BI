"""
Testes unitários para o módulo Automacao.config_loader.
Verifica a precedência e resolução de URLs por variáveis de ambiente semânticas.
"""

import os
import unittest
from unittest.mock import patch

from Automacao.config_loader import carregar_mapeamento, obter_origem_mapeamento


class TestConfigLoaderURLs(unittest.TestCase):
    """Testes de carregamento de URLs via variáveis de ambiente."""

    def setUp(self):
        # Limpar variáveis de ambiente de teste antes de cada caso
        self.env_vars_to_clean = [
            "LOGTUDO_URL_LOGIN",
            "LOGTUDO_URL",
            "LOGTUDO_URL_FATURADOS",
            "LOGTUDO_URL_COTACOES_FATURADOS",
            "LOGTUDO_URL_COTACOES_FRETE",
            "LOGTUDO_URL_DOWNLOAD_1",
            "LOGTUDO_URL_NAO_FATURADOS",
            "LOGTUDO_URL_COTACOES_NAO_FATURADOS",
            "LOGTUDO_URL_COTACOES_FILTRADAS",
            "LOGTUDO_URL_DOWNLOAD_2",
            "LOGTUDO_URL_CANCELADOS",
            "LOGTUDO_URL_COTACOES_CANCELADOS",
            "LOGTUDO_URL_COTACOES_DOWNLOAD3",
            "LOGTUDO_URL_DOWNLOAD_3",
            "LOGTUDO_URL_CONHECIMENTO_FRETE",
            "LOGTUDO_URL_OCORRENCIAS",
            "LOGTUDO_URL_DOWNLOAD_4",
        ]
        self._orig_env = {}
        for var in self.env_vars_to_clean:
            if var in os.environ:
                self._orig_env[var] = os.environ.pop(var)

    def tearDown(self):
        for var in self.env_vars_to_clean:
            os.environ.pop(var, None)
        os.environ.update(self._orig_env)

    def test_url_faturados_via_env(self):
        """Verifica se LOGTUDO_URL_FATURADOS sobrescreve o valor do relatório de Faturados."""
        test_url = "https://custom.logtudo.net/relatorio_faturados"
        with patch.dict(os.environ, {"LOGTUDO_URL_FATURADOS": test_url}):
            mapeamento = carregar_mapeamento()
            self.assertEqual(
                mapeamento["urls"]["transp_rel_cotacoes_frete_formulario"],
                test_url,
            )

    def test_url_nao_faturados_via_env(self):
        """Verifica se LOGTUDO_URL_NAO_FATURADOS sobrescreve o valor do relatório de Não Faturados."""
        test_url = "https://custom.logtudo.net/relatorio_nao_faturados"
        with patch.dict(os.environ, {"LOGTUDO_URL_NAO_FATURADOS": test_url}):
            mapeamento = carregar_mapeamento()
            self.assertEqual(
                mapeamento["urls"]["transp_rel_cotacoes_frete_filtrados"],
                test_url,
            )

    def test_url_cancelados_via_env(self):
        """Verifica se LOGTUDO_URL_CANCELADOS sobrescreve o valor do relatório de Cancelados."""
        test_url = "https://custom.logtudo.net/relatorio_cancelados"
        with patch.dict(os.environ, {"LOGTUDO_URL_CANCELADOS": test_url}):
            mapeamento = carregar_mapeamento()
            self.assertEqual(
                mapeamento["urls"]["transp_rel_cotacoes_frete_download3"],
                test_url,
            )

    def test_url_conhecimento_frete_via_env(self):
        """Verifica se LOGTUDO_URL_CONHECIMENTO_FRETE sobrescreve o relatório correspondente."""
        test_url = "https://custom.logtudo.net/relatorio_conhecimento"
        with patch.dict(os.environ, {"LOGTUDO_URL_CONHECIMENTO_FRETE": test_url}):
            mapeamento = carregar_mapeamento()
            self.assertEqual(
                mapeamento["urls"]["trans_rel_conhecimento_frete"],
                test_url,
            )

    def test_url_login_via_env(self):
        """Verifica se LOGTUDO_URL_LOGIN sobrescreve a URL de login."""
        test_url = "https://auth.logtudo.net/login"
        with patch.dict(os.environ, {"LOGTUDO_URL_LOGIN": test_url}):
            mapeamento = carregar_mapeamento()
            self.assertEqual(
                mapeamento["urls"]["login"],
                test_url,
            )

    def test_aliases_fallback(self):
        """Verifica se aliases como LOGTUDO_URL_COTACOES_FRETE e LOGTUDO_URL_OCORRENCIAS funcionam."""
        test_url_faturados = "https://custom.logtudo.net/faturados_alias"
        test_url_ocorrencias = "https://custom.logtudo.net/ocorrencias_alias"
        with patch.dict(
            os.environ,
            {
                "LOGTUDO_URL_COTACOES_FRETE": test_url_faturados,
                "LOGTUDO_URL_OCORRENCIAS": test_url_ocorrencias,
            },
        ):
            mapeamento = carregar_mapeamento()
            self.assertEqual(
                mapeamento["urls"]["transp_rel_cotacoes_frete_formulario"],
                test_url_faturados,
            )
            self.assertEqual(
                mapeamento["urls"]["trans_rel_conhecimento_frete"],
                test_url_ocorrencias,
            )

    def test_empty_env_var_fallback(self):
        """Valores vazios no ambiente devem ser ignorados e usar o fallback do JSON/default."""
        with patch.dict(os.environ, {"LOGTUDO_URL_CANCELADOS": "   "}):
            mapeamento = carregar_mapeamento()
            self.assertTrue(
                len(mapeamento["urls"]["transp_rel_cotacoes_frete_download3"]) > 0
            )
            self.assertNotEqual(
                mapeamento["urls"]["transp_rel_cotacoes_frete_download3"],
                "   ",
            )

    def test_semantic_name_over_generic_alias(self):
        """Verifica se o nome semântico (ex: LOGTUDO_URL_FATURADOS) tem prioridade sobre o alias genérico."""
        url_prioritaria = "https://custom.logtudo.net/prioridade_faturados"
        url_generica = "https://custom.logtudo.net/generica_faturados"
        with patch.dict(
            os.environ,
            {
                "LOGTUDO_URL_FATURADOS": url_prioritaria,
                "LOGTUDO_URL_COTACOES_FRETE": url_generica,
            },
        ):
            mapeamento = carregar_mapeamento()
            self.assertEqual(
                mapeamento["urls"]["transp_rel_cotacoes_frete_formulario"],
                url_prioritaria,
            )

    def test_estrutura_completa_chaves(self):
        """Verifica se a estrutura final possui todas as chaves esperadas pela automação."""
        mapeamento = carregar_mapeamento()
        self.assertIn("urls", mapeamento)
        self.assertIn("selectors", mapeamento)
        self.assertIn("erros", mapeamento)

        expected_urls = [
            "login",
            "transp_rel_cotacoes_frete_formulario",
            "transp_rel_cotacoes_frete_filtrados",
            "transp_rel_cotacoes_frete_download3",
            "trans_rel_conhecimento_frete",
        ]
        for u in expected_urls:
            self.assertIn(u, mapeamento["urls"])
            self.assertTrue(mapeamento["urls"][u].startswith("http"))


if __name__ == "__main__":
    unittest.main()
