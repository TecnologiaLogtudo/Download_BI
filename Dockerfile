# Base de build para projetos Python + Playwright em VPS
FROM mcr.microsoft.com/playwright/python:v1.58.0-noble

WORKDIR /app

# Dependencias Python
# Usando o requirements.txt da raiz se existir, ou o específico da conectividade
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# Garante binarios do Chromium
RUN playwright install chromium

# Copie seu projeto
COPY . /app

# Permissoes para usuario nao-root (pwuser ja existe na imagem base)
RUN mkdir -p /app/data /app/downloads && chown -R pwuser:pwuser /app
USER pwuser

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PLAYWRIGHT_HEADLESS=true

# Porta exposta para o Coolify (Proxy reverso)
EXPOSE 8000

# Healthcheck básico usando o server http
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/ || exit 1

# Comando para manter um serviço rodando e servir arquivos se necessário
CMD ["python", "-m", "http.server", "8000"]
