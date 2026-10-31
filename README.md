1. Project Outline
- Timeline: Considering 4–6 weeks
- Goals: Implement the project, including bonus features
         Aim to build it ourselves while learning about web development
- Design theme: A big challenge....
- Initial planning Figma link: https://hope-item-44221151.figma.site

2. Plan
- Meet weekly to review code and plan for the following week

3. Infrastructure
- Set up the infrastructure using Docker Compose.

4. Stack
- Frontend: Angular / TypeScript
- Backend: Flask / Python
- Infrastructure: Docker Compose
- Database: PostgreSQL

## Docker development environment

Docker provides Node.js, Python with backend dependencies, and PostgreSQL. The front container starts a temporary HTTP server using Node.js built-in modules and responds with plain text `ok`. No Angular project or frontend packages are included. Flask starts automatically. Both servers have HTTP healthchecks.

```sh
# First-time setup: copy the template and set a local DB password.
cp .env.example .env
docker compose up --build -d

# Open a shell in either development container.
docker compose exec front sh
docker compose exec back sh

# Stop the environment (database data is preserved).
docker compose down
```

Local `front/` and `back/` directories are mounted into the containers. The temporary Node.js server only checks the environment; replace its Dockerfile command when the frontend project is ready. Rebuild after changing Dockerfiles or backend requirements.

The backend listens on `0.0.0.0:5000` inside Docker and is available at `http://localhost:5001/health` on your computer. Python code changes trigger an automatic reload. After changing the Dockerfile or requirements, run `docker compose up --build -d back`. View server logs with `docker compose logs -f back`.

The frontend listens on `0.0.0.0:4200`, mapped to `http://localhost:8080` (configurable with `APP_PORT`). The response is plain text `ok`. Run `docker compose ps` to check server health.

PostgreSQL starts automatically and is accessible from the backend at `db:5432`. Each developer keeps their own `.env`; database credentials are initialized only when the database volume is first created.
