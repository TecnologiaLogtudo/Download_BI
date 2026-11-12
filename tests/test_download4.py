"""
Testes unitários para o módulo Automacao.transp_rel_cotacoes_frete_download4.
"""

import unittest
from unittest.mock import MagicMock, patch
from pathlib import Path

from Automacao.transp_rel_cotacoes_frete_download4 import gerar_download_conhecimento_frete


class TestTranspRelCotacoesFreteDownload4(unittest.TestCase):
    """Testa a geração de download de conhecimento de frete."""

    @patch("Automacao.transp_rel_cotacoes_frete_download4.metadata_manager")
    @patch("Automacao.transp_rel_cotacoes_frete_download4.time.sleep")
    def test_gerar_download_conhecimento_frete_sucesso(self, mock_sleep, mock_meta):
        mock_meta.registrar_download.return_value = "meta-123"

        mock_page = MagicMock()
        mock_popup = MagicMock()
        mock_popup.url = "https://logtudo.e-login.net/relatorio"

        mock_download = MagicMock()
        mock_download.suggested_filename = "Relatorio_Detalhado.xls"

        # Simular context manager expect_popup
        popup_cm = MagicMock()
        popup_cm.value = mock_popup
        mock_page.expect_popup.return_value.__enter__.return_value = popup_cm

        # Simular context manager expect_download
        download_cm = MagicMock()
        download_cm.value = mock_download
        mock_popup.expect_download.return_value.__enter__.return_value = download_cm

        caminho, d_id = gerar_download_conhecimento_frete(
            page=mock_page,
            url_conhecimento="https://logtudo.e-login.net/test",
            debug=False,
        )

        # Verifica se o wait_for_load_state do popup utilizou 'load'
        mock_popup.wait_for_load_state.assert_called_with("load", timeout=15000)
        self.assertEqual(d_id, "meta-123")
        self.assertTrue(caminho.endswith("Padrao_Detalhado.xls"))


if __name__ == "__main__":
    unittest.main()
