# Usar uma imagem base oficial do Python
FROM python:3.9-slim

# Definir o diretório de trabalho dentro do contêiner
WORKDIR /app

# Copiar o arquivo de dependências
COPY requirements.txt .

# Instalar as dependências
RUN pip install --no-cache-dir -r requirements.txt

# Copiar o código da aplicação para o diretório de trabalho
COPY ./proxy_service ./proxy_service

# Expor a porta que a aplicação vai rodar
EXPOSE 8000

# Comando para iniciar a aplicação quando o contêiner for executado
CMD ["python", "proxy_service/main.py"]
