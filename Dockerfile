# Officielt Python-image (slim = mindre)
FROM python:3.14-slim

# Sæt working directory
WORKDIR /app

# Installér uv, som vi også bruger lokalt
RUN pip install uv

# Kopiér afhængighedsfilerne først (for layer caching)
COPY pyproject.toml uv.lock ./

# Installér afhængigheder fra uv.lock
RUN uv sync --locked

# Kopiér resten af koden (.dockerignore holder .venv ude)
COPY . .

# Dokumentér portene: 5000 = API, 8501 = Streamlit
EXPOSE 5000 8501

# Start API'en som standard - frontend-servicen i docker-compose.yml overskriver denne kommando
CMD ["uv", "run", "api.py"]
