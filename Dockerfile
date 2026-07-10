FROM python:3.12-slim

WORKDIR /app

# Dependencias del sistema para mysqlclient
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Descargar HTMX
RUN mkdir -p /app/static/htmx && \
    curl -sL https://unpkg.com/htmx.org@1.9.12/dist/htmx.min.js -o /app/static/htmx/htmx.min.js

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8001
CMD ["gunicorn", "--bind", "0.0.0.0:8001", "palex_averias.wsgi:application"]

