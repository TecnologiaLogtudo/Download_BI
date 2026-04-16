import sqlite3
import uuid
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
from Automacao.config_pastas import DATA_DIR_ATIVO, DOWNLOADS_DIR_ATIVO

class DownloadMetadata:
    """
    Gerencia o rastreamento persistente de todos os downloads realizados.
    Utiliza SQLite para manter um histórico independente da existência física dos arquivos.
    """
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS downloads (
                    id TEXT PRIMARY KEY,
                    operacao TEXT,
                    url TEXT,
                    caminho_original TEXT,
                    caminho_atual TEXT,
                    nome_arquivo TEXT,
                    criado_em TEXT,
                    status TEXT
                )
            ''')
    
    def registrar_download(self, operacao: str, url: str, caminho: str) -> str:
        """Registra um novo download no banco de dados."""
        download_id = str(uuid.uuid4())
        caminho_path = Path(caminho)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                INSERT INTO downloads 
                (id, operacao, url, caminho_original, caminho_atual, nome_arquivo, criado_em, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                download_id, operacao, url, str(caminho), str(caminho), 
                caminho_path.name, datetime.now().isoformat(), 'ativo'
            ))
        
        return download_id
    
    def listar_downloads(self) -> List[Dict]:
        """Retorna lista de todos os registros de download."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute('SELECT * FROM downloads ORDER BY criado_em DESC')
            return [dict(row) for row in cursor.fetchall()]

    def resolver_caminho(self, download_id: str) -> Optional[Path]:
        """
        Tenta localizar o arquivo físico, mesmo se ele foi movido de pasta.
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                'SELECT caminho_original, caminho_atual, nome_arquivo FROM downloads WHERE id = ?',
                (download_id,)
            )
            row = cursor.fetchone()
            
        if not row:
            return None
            
        # Estratégia de busca em cascata
        candidatos = [
            Path(row[1]),  # Caminho registrado como atual
            Path(row[0]),  # Caminho original no momento do download
            DOWNLOADS_DIR_ATIVO / row[2],  # Pasta raiz de downloads + nome
        ]
        
        for candidato in candidatos:
            if candidato.exists() and candidato.is_file():
                return candidato
        
        # Procura profunda (recursiva) na pasta de downloads pelo nome exato
        for p in DOWNLOADS_DIR_ATIVO.rglob(row[2]):
            if p.is_file():
                # Atualiza o caminho atual no banco para acelerar a próxima busca
                self.atualizar_caminho(download_id, str(p))
                return p
                
        return None

    def atualizar_caminho(self, download_id: str, novo_caminho: str):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('UPDATE downloads SET caminho_atual = ? WHERE id = ?', (novo_caminho, download_id))

    def cleanup_invalidos(self) -> int:
        """Marca como 'perdido' os arquivos que não existem mais em nenhum lugar."""
        downloads = self.listar_downloads()
        count = 0
        with sqlite3.connect(self.db_path) as conn:
            for d in downloads:
                if d['status'] == 'ativo' and not self.resolver_caminho(d['id']):
                    conn.execute('UPDATE downloads SET status = ? WHERE id = ?', ('perdido', d['id']))
                    count += 1
        return count

# Instância singleton para uso em todo o projeto
metadata_manager = DownloadMetadata(DATA_DIR_ATIVO / "metadata.db")
