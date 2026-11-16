# URL Shortener

A small microservices URL shortener: a React frontend, a FastAPI shortener service, a FastAPI analytics service, Postgres (one database per service), and Redis for click events — fronted by nginx.

## Architecture

```
frontend (Vite/React) -> nginx (:80) -> shortener-service (:8000) -> postgres-shortener
                                      -> analytics-service (:8000) -> postgres-analytics
shortener-service --publishes clicks--> redis --subscribed by--> analytics-service
```

| Service | Port (host) | Purpose |
|---|---|---|
| `nginx` | 80 | Reverse proxy, routes `/api/*` to the backend services |
| `shortener-service` | 8001 | Creates short codes, redirects, publishes click events |
| `analytics-service` | 8002 | Subscribes to click events, serves click stats |
| `postgres-shortener` | internal | Stores links |
| `postgres-analytics` | internal | Stores click events |
| `redis` | internal | Pub/sub channel (`clicks`) between the two services |
| `frontend` | 5173 (dev) | React UI |

## Prerequisites

- Docker and Docker Compose
- Node.js 18+ and npm (for running the frontend outside Docker)

## Setup

### 1. Start the backend (Postgres, Redis, both services, nginx)

```bash
docker compose up -d --build
```

This brings up nginx on `http://localhost`, `shortener-service` on `:8001`, and `analytics-service` on `:8002`.

### 2. Run the frontend

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`. The dev server proxies `/api/*` requests to `http://localhost:80` (nginx), which forwards them to the backend services — so the Docker stack from step 1 must be running.

### 3. Use it

- Paste a URL and click **Shorten** to get a short link (`/api/r/<code>`).
- Visiting the short link redirects to the original URL and records a click.
- Click **Refresh stats** to see the total click count for that code.

## API reference (via nginx on `:80`)

| Method | Path | Description |
|---|---|---|
| `POST` | `/api/shorten` | Body `{ "url": "..." }` → `{ "code": "...", "short_url": "/api/r/<code>" }` |
| `GET` | `/api/r/{code}` | Redirects to the original URL and records a click |
| `GET` | `/api/stats/{code}` | Returns `{ "code": "...", "total_clicks": N }` |

Each service also exposes `GET /health`.

## Stopping

```bash
docker compose down        # stop containers
docker compose down -v     # also remove the Postgres volumes
```
