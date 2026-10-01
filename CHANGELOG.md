# Changelog
 
## [1.1.0] - 2026-10-01
 
### Adicionado
- **Configuração de URLs via Variáveis de Ambiente**: Suporte completo a URLs de relatórios através de variáveis no `.env` e ambiente do sistema com nomes semânticos correspondentes ao relatório baixado (`LOGTUDO_URL_FATURADOS`, `LOGTUDO_URL_NAO_FATURADOS`, `LOGTUDO_URL_CANCELADOS`, `LOGTUDO_URL_CONHECIMENTO_FRETE`, `LOGTUDO_URL_LOGIN`) além de aliases retrocompatíveis.
- **Inversão de Prioridade no `config_loader.py`**: Variáveis de ambiente agora possuem prioridade máxima sobre o `mapeamento.json` e fallbacks padrão.
- **Arquivo `.env.example`**: Modelo documentado com todas as variáveis suportadas.
- **Suíte de Testes Automatizados**: Criados testes unitários em `tests/test_config_loader.py` para validar a resolução e precedência de variáveis de ambiente.
 
## [1.0.1] - 2026-08-24

### Corrigido
- **Logs no terminal do VPS**: Implementado `FlushingStreamHandler` no `logger_config.py` direcionado para `sys.stdout` com flush imediato a cada mensagem emitida, garantindo exibição em tempo real do fluxo de execução em agendamentos/schedulers.
- **Suporte UTF-8 no Windows**: Reconfiguração automática de `sys.stdout` e `sys.stderr` para UTF-8 (`errors="replace"`), evitando `UnicodeEncodeError` ao emitir caracteres como `✓` ou `✗` em consoles do Windows.
- **Auto-inicialização de logs**: `get_logger()` agora garante que o logging seja configurado automaticamente caso o script seja invocado via schedule/cron ou executado diretamente.
