# 🚀 Automação Logtudo - Download BI

Sistema de automação para login e download de relatórios do Logtudo usando Playwright.

## 📋 Requisitos

- Python 3.8+
- Playwright
- python-dotenv

## 🔧 Configuração

### 1. Criar ambiente virtual (opcional mas recomendado)

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux/Mac
source .venv/bin/activate
```

### 2. Instalar dependências

```bash
pip install -r requirements.txt
```

### 3. Configurar credenciais

1. Copie o arquivo `.env.example` para `.env`:
```bash
copy .env.example .env
```

2. Edite o arquivo `.env` com suas credenciais:
```
LOGTUDO_USER=seu_usuario
LOGTUDO_PASS=sua_senha
```

### 4. Instalar browsers do Playwright (primeira execução)

```bash
playwright install
```

## 🚀 Execução

### Rodar a automação completa

```bash
python main.py
```

### Rodar apenas o login

```bash
python Automacao/Login.py
```

## 📁 Estrutura do Projeto

```
Download_BI/
├── main.py                          # Script principal de orquestração
├── requirements.txt                 # Dependências do projeto
├── .env.example                     # Exemplo de variáveis de ambiente
├── .env                             # Credenciais (NÃO COMMITAR)
├── mapeamento.json                  # Configuração de URLs e seletores
│
├── Automacao/                       # Módulo de automação
│   ├── __init__.py
│   ├── config_loader.py            # Carrega configurações
│   └── Login.py                    # Função de login
│
└── Conectividade/                   # Módulo de conectividade
    ├── __init__.py
    ├── playwright_vps_connect.py   # Cliente Playwright
    └── requirements-playwright-vps.txt
```

## ⚙️ Variáveis de Ambiente

| Variável | Descrição | Padrão |
|----------|-----------|--------|
| `LOGTUDO_USER` | Usuário para login | - |
| `LOGTUDO_PASS` | Senha para login | - |
| `HEADLESS` | Executar sem exibir navegador | `true` |
| `DEBUG` | Ativar mensagens de debug | `true` |
| `LOGTUDO_URL` | URL de login (fallback quando não houver JSON) | `https://www.logtudo.com.br/login` |

### Precedência de configuração (URL e seletores)

O carregamento segue esta ordem:

1. `mapeamento.json` na raiz do projeto (`./mapeamento.json`)
2. `Automacao/mapeamento.json` (retrocompatibilidade)
3. Variáveis `LOGTUDO_*` do `.env`
4. Defaults internos do sistema

## 🔒 Segurança

⚠️ **IMPORTANTE**: 
- **Nunca** commitar o arquivo `.env` com credenciais reais
- Adicione `.env` ao `.gitignore`
- Use senhas de aplicação/API quando disponível
- Considere usar um gerenciador de secrets em produção

## 🐛 Debug

Para executar em modo debug (com navegador visível):

```bash
# Editar .env
HEADLESS=false
DEBUG=true

# Ou rodar diretamente
python -c "from Automacao.Login import realizar_login; realizar_login('user', 'pass', headless=False, debug=True)"
```

## 📝 Logs e Screenshots

Quando há erros, o sistema pode gerar screenshots em:
- `debug_screenshot.png`

## 🛠️ Troubleshooting

### Erro: "Credenciais não configuradas"
- Verifique se o arquivo `.env` existe
- Confirme que contém `LOGTUDO_USER` e `LOGTUDO_PASS`

### Erro: "Campo de usuário não encontrado"
- Verifique o seletor em `mapeamento.json`
- Ative debug para ver screenshots
- Confirme que a URL está correta

### Erro: "timeout"
- Pode ser problema de conexão
- Tente aumentar `timeout_ms` em `Conectividade/playwright_vps_connect.py`
- Execute com `HEADLESS=false` para ver o que está acontecendo

## 📚 Referências

- [Playwright Documentation](https://playwright.dev/python/)
- [python-dotenv](https://github.com/thronberger/python-dotenv)

## 📧 Contato

Para suporte, procure o desenvolvedor responsável.
