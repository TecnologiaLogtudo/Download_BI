from typing import List, Dict
from Automacao.metadata_manager import metadata_manager

class RecoveryManager:
    """
    Interface para gerenciar a recuperação e integridade dos arquivos baixados.
    """
    @staticmethod
    def listar_downloads_ativos() -> List[Dict]:
        """Lista todos os downloads registrados no banco de metadados."""
        return metadata_manager.listar_downloads()
    
    @staticmethod
    def verificar_integridade() -> Dict[str, List[str]]:
        """
        Analisa todos os registros e verifica quais arquivos ainda existem fisicamente.
        Utiliza a inteligência do metadata_manager para encontrar arquivos movidos.
        """
        downloads = metadata_manager.listar_downloads()
        
        existentes = []
        perdidos = []
        
        for d in downloads:
            # Tenta encontrar o arquivo físico
            caminho = metadata_manager.resolver_caminho(d['id'])
            if caminho and caminho.exists():
                existentes.append(f"{d['operacao']} ({caminho.name})")
            else:
                perdidos.append(d['operacao'])
        
        return {
            'existentes': existentes,
            'perdidos': perdidos
        }
    
    @staticmethod
    def cleanup_arquivos_perdidos() -> int:
        """
        Sincroniza o banco de dados com a realidade do disco,
        marcando como 'perdido' os arquivos que não foram encontrados.
        """
        return metadata_manager.cleanup_invalidos()

    @staticmethod
    def obter_caminho_seguro(download_id: str) -> str:
        """
        Retorna o caminho atualizado do arquivo, garantindo que o chamador
        tenha o local correto mesmo após movimentações.
        """
        path = metadata_manager.resolver_caminho(download_id)
        return str(path) if path else ""
