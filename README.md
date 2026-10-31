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

Docker provides Node.js, Python with backend dependencies, and PostgreSQL. No frontend application or packages are included. Frontend and backend containers stay idle until you run commands manually. No application code or health endpoint is required to start the environment.

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

Local `front/` and `back/` directories are mounted into the containers. Set up your frontend project and dependencies when you are ready. Rebuild the backend image after changing its requirements.

When you are ready, run your application manually inside the corresponding container. Servers must listen on `0.0.0.0`: frontend port `4200` maps to `localhost:8080` (configurable with `APP_PORT`), and backend port `5000` maps to `localhost:5001`. These addresses do not serve an application until you start one.

PostgreSQL starts automatically and is accessible from the backend at `db:5432`. Each developer keeps their own `.env`; database credentials are initialized only when the database volume is first created.
