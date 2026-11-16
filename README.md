# Fredagsbar Event System

A small event and sign-up system for a Friday bar: a **Flask REST API** with a **Streamlit** frontend, running as two containers with **Docker Compose**.

## Features
- Create, view and delete events
- Sign people up for an event and cancel sign-ups
- The frontend talks to the API over HTTP (`httpx`), so the two parts are fully separated
- API documented in [`swagger.json`](swagger.json)

## Tech stack
Python 3.14 · Flask · Streamlit · httpx · Docker / Docker Compose · uv

## API

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET    | `/events` | List all events |
| GET    | `/events/<id>` | Get one event |
| POST   | `/events` | Create an event |
| DELETE | `/events/<id>` | Delete an event |
| POST   | `/events/<id>/signups` | Sign a person up |
| DELETE | `/events/<id>/signups/<name>` | Cancel a sign-up |

## Run with Docker

```bash
docker compose up --build
```

- Frontend: http://localhost:8501
- API: http://localhost:5000 (e.g. `GET http://localhost:5000/events`)

## Run locally without Docker

```bash
uv run api.py                     # terminal 1: API on http://127.0.0.1:5000
uv run streamlit run app.py       # terminal 2: frontend on http://localhost:8501
```
