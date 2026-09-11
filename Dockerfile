# Usa uma imagem oficial leve do Python (equivalente ao dotnet runtime-deps)
FROM python:3.10-slim

# Define o diretório de trabalho dentro do container
WORKDIR /app

# Copia o arquivo de dependências primeiro (para aproveitar o cache do Docker)
COPY requirements.txt .

# Instala as dependências (incluindo o driver do postgres e o uvicorn)
RUN pip install --no-cache-dir -r requirements.txt

# Copia o restante do código fonte
COPY . .

# Expõe a porta 8000
EXPOSE 8000

# Comando para rodar a aplicação quando o container subir
# --host 0.0.0.0 é CRUCIAL no Docker para aceitar conexões externas
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]