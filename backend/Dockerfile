FROM python:3.11-slim

WORKDIR /app

# Instala dependencias del sistema
RUN apt-get update && apt-get install -y libmysqlclient-dev build-essential && rm -rf /var/lib/apt/lists/*

# Copia dependencias Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia el resto del proyecto
COPY . .

# Prepara Gunicorn
RUN chmod +x start_gunicorn.sh
EXPOSE 8000
CMD ["./start_gunicorn.sh"]