# Fredagsbarens event-system

Flask API (`api.py`) og Streamlit-frontend (`app.py`), der taler sammen via `httpx`.

## Kør med Docker

```bash
docker compose up --build
```

- Frontend: http://localhost:8501
- API: http://localhost:5000 (fx `GET http://localhost:5000/events` i Postman)

## Kør lokalt uden Docker

```bash
uv run api.py                     # terminal 1: API'en på http://127.0.0.1:5000
uv run streamlit run app.py       # terminal 2: frontenden på http://localhost:8501
```
