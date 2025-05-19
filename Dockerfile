# Imagem base com Python
FROM python:3.10-slim

# Evita prompts interativos
ENV DEBIAN_FRONTEND=noninteractive

# Instala ffmpeg e dependências
RUN apt-get update && \
    apt-get install -y ffmpeg && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Cria diretório da aplicação
WORKDIR /app

# Copia os arquivos do projeto
COPY . /app

# Instala dependências do projeto
RUN pip install --no-cache-dir -r requirements.txt

# Expõe a porta da API
EXPOSE 8100

# Comando para iniciar a aplicação
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
