# Usa una versión específica de Python (3.9 es más estable para Django)
FROM python:3.12-slim-bullseye

# Establece el directorio de trabajo
WORKDIR /app

# Variables de entorno
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Instala dependencias del sistema
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copia e instala dependencias de Python primero (para cachear)
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copia el proyecto
COPY . .

# Da permisos de ejecución al script de inicio
RUN chmod +x /app/start.sh

# Usa el script como entrypoint
ENTRYPOINT ["/app/start.sh"]