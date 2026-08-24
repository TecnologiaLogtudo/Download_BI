# Changelog

## [1.0.1] - 2026-08-24

### Corrigido
- **Logs no terminal do VPS**: Implementado `FlushingStreamHandler` no `logger_config.py` direcionado para `sys.stdout` com flush imediato a cada mensagem emitida, garantindo exibição em tempo real do fluxo de execução em agendamentos/schedulers.
- **Suporte UTF-8 no Windows**: Reconfiguração automática de `sys.stdout` e `sys.stderr` para UTF-8 (`errors="replace"`), evitando `UnicodeEncodeError` ao emitir caracteres como `✓` ou `✗` em consoles do Windows.
- **Auto-inicialização de logs**: `get_logger()` agora garante que o logging seja configurado automaticamente caso o script seja invocado via schedule/cron ou executado diretamente.
