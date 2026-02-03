# Elastic Newsroom Infrastructure

A B2B platform that transforms freelance journalism from an ad-hoc, trust-based process into programmable infrastructure.

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Python 3.11+ (for local development)

### Setup

1. Copy the environment file:
   ```bash
   cp .env.example .env
   ```

2. Start the database services:
   ```bash
   make up-db
   ```

3. Build and start all services:
   ```bash
   make build
   make up
   ```

4. Run database migrations:
   ```bash
   make migrate
   ```

5. Access the API documentation:
   - Identity Service: http://localhost:8001/docs

## Project Structure

```
elastic-newsroom/
├── docker-compose.yml      # Docker orchestration
├── .env.example            # Environment variables template
├── Makefile                # Common commands
├── services/
│   ├── identity/           # User auth & profiles
│   ├── discovery/          # Talent search (Phase 1.4)
│   ├── pitch/              # Pitch management (Phase 2)
│   ├── payment/            # Payment processing (Phase 2)
│   └── ml/                 # ML scoring service (Phase 3)
├── shared/
│   ├── db/                 # Database utilities
│   ├── auth/               # JWT utilities
│   ├── logging/            # Logging configuration
│   └── errors/             # Error handling
├── migrations/             # Global Alembic migrations
└── scripts/                # Utility scripts
```

## Services

### Identity Service (Port 8001)

User authentication and profile management.

**Endpoints:**
- `POST /api/v1/auth/register` - Create user account
- `POST /api/v1/auth/login` - Get JWT tokens
- `POST /api/v1/auth/refresh` - Refresh access token
- `GET /api/v1/users/me` - Get current user
- `PATCH /api/v1/users/me` - Update profile
- `GET /api/v1/freelancers/{id}` - Get freelancer profile
- `PATCH /api/v1/freelancers/me` - Update freelancer profile
- `POST /api/v1/freelancers/me/availability` - Set availability
- `POST /api/v1/newsrooms` - Create newsroom
- `GET /api/v1/newsrooms/{id}` - Get newsroom
- `POST /api/v1/newsrooms/{id}/members` - Add member

## Development

### Running Locally

```bash
# Start only databases
make up-db

# Run identity service locally
cd services/identity
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8001
```

### Running Tests

```bash
make test
```

### Database Migrations

```bash
# Create a new migration
docker-compose exec identity alembic revision --autogenerate -m "description"

# Apply migrations
make migrate

# Rollback last migration
docker-compose exec identity alembic downgrade -1
```

## API Authentication

All protected endpoints require JWT authentication via the `Authorization` header:

```
Authorization: Bearer <access_token>
```

Access tokens expire after 15 minutes. Use the refresh token to get new tokens.

## Configuration

Environment variables (see `.env.example`):

| Variable | Description | Default |
|----------|-------------|---------|
| `POSTGRES_DB` | Database name | `elastic_newsroom` |
| `POSTGRES_USER` | Database user | `newsroom_user` |
| `POSTGRES_PASSWORD` | Database password | `changeme_in_production` |
| `JWT_SECRET_KEY` | JWT signing key | (change in production) |
| `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` | Access token expiry | `15` |
| `JWT_REFRESH_TOKEN_EXPIRE_DAYS` | Refresh token expiry | `7` |

## License

Confidential - Internal Use Only
