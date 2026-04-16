from pathlib import Path
import os
import sys
import tempfile
from typing import Optional

# Configuração de pastas
# Raiz do projeto (Download_BI/)
ROOT = Path(__file__).resolve().parent.parent  

# Pasta principal de downloads
DOWNLOADS_DIR = ROOT / "downloads"

# Fallback para pasta temporária do sistema se a principal falhar (ex: erro de permissão no volume Docker)
TEMP_DOWNLOADS_DIR = Path(tempfile.gettempdir()) / "logtudo" / "downloads"

def ensure_writable_dir(primary: Path, fallback: Path, label: str) -> Path:
    """
    Testa se a pasta é gravável, cria se necessário e usa fallback em caso de erro.
    """
    try:
        primary.mkdir(parents=True, exist_ok=True)
        # Teste real de escrita
        probe = primary / ".write_test"
        probe.write_text("ok", encoding="utf-8")
        probe.unlink(missing_ok=True)
        return primary
    except Exception as exc:
        print(f"[pastas] Sem permissão de escrita para {label} em {primary}: {exc}")
        try:
            fallback.mkdir(parents=True, exist_ok=True)
            probe = fallback / ".write_test"
            probe.write_text("ok", encoding="utf-8")
            probe.unlink(missing_ok=True)
            print(f"[pastas] Usando fallback de {label} com sucesso: {fallback}")
            return fallback
        except Exception as e2:
            # Caso extremo: falha total de escrita
            print(f"[pastas] ERRO CRÍTICO: Fallback também falhou para {label}: {e2}")
            # Tenta uma subpasta no diretório temporário padrão do OS
            os_tmp = Path(tempfile.mkdtemp(prefix=f"logtudo_{label}_"))
            print(f"[pastas] Usando diretório temporário emergencial: {os_tmp}")
            return os_tmp

# Pastas garantidas como graváveis para uso em todo o projeto
DOWNLOADS_DIR_ATIVO = ensure_writable_dir(DOWNLOADS_DIR, TEMP_DOWNLOADS_DIR, "downloads")
DATA_DIR_ATIVO = ensure_writable_dir(ROOT / "data", Path(tempfile.gettempdir()) / "logtudo" / "data", "data")
