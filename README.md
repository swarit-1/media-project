# Elastic Newsroom

A B2B platform that transforms freelance journalism from an ad-hoc, trust-based process into programmable infrastructure. Elastic Newsroom connects newsrooms with vetted freelance journalists through structured pitch workflows, smart discovery, ML-powered matching, and integrated payments.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Frontend (Next.js)                       │
│                        localhost:3000                            │
└──────┬──────────┬──────────┬──────────┬──────────┬──────────────┘
       │          │          │          │          │
       ▼          ▼          ▼          ▼          ▼
┌──────────┐┌──────────┐┌──────────┐┌──────────┐┌──────────┐
│ Identity ││Discovery ││  Pitch   ││ Payment  ││    ML    │
│  :8001   ││  :8002   ││  :8003   ││  :8004   ││  :8005   │
└────┬─────┘└────┬─────┘└────┬─────┘└────┬─────┘└────┬─────┘
     │           │           │           │           │
     ▼           ▼           ▼           ▼           ▼
┌─────────────────────────────────────────────────────────────┐
│              PostgreSQL (pgvector) :5432                     │
│              Redis :6379                                     │
└─────────────────────────────────────────────────────────────┘
```

## Tech Stack

### Backend
- **Runtime**: Python 3.11+, FastAPI
- **Database**: PostgreSQL 15 with pgvector extension
- **Cache**: Redis 7
- **ORM**: SQLAlchemy 2.0 (async), Alembic migrations
- **Auth**: JWT (access + refresh tokens)
- **ML**: sentence-transformers (all-MiniLM-L6-v2)
- **Payments**: Stripe integration
- **Infrastructure**: Docker Compose

### Frontend
- **Framework**: Next.js 16.1.6 (App Router)
- **Language**: TypeScript 5
- **UI**: React 19, Tailwind CSS v4, shadcn/ui (radix-ui primitives)
- **State**: Zustand (auth), React Query (server state)
- **Forms**: react-hook-form + Zod validation
- **Icons**: lucide-react

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Node.js 18+ and npm (for frontend)
- Python 3.11+ (for local backend development)

### 1. Clone and configure

```bash
git clone <repository-url>
cd elastic-newsroom
cp .env.example .env
```

Edit `.env` with your configuration (defaults work for local development).

### 2. Start backend services

```bash
# Build all Docker images
make build

# Start all services (postgres, redis, and all 5 microservices)
make up

# Run database migrations
make migrate
```

### 3. Start the frontend

```bash
cd frontend
npm install
npm run dev
```

### 4. Access the application

| Service | URL |
|---------|-----|
| **Frontend** | http://localhost:3000 |
| **Identity API docs** | http://localhost:8001/docs |
| **Discovery API docs** | http://localhost:8002/docs |
| **Pitch API docs** | http://localhost:8003/docs |
| **Payment API docs** | http://localhost:8004/docs |
| **ML API docs** | http://localhost:8005/docs |

## Project Structure

```
elastic-newsroom/
├── docker-compose.yml          # Docker orchestration (7 containers)
├── .env.example                # Environment variables template
├── Makefile                    # Development commands
├── frontend/                   # Next.js frontend application
│   ├── src/
│   │   ├── app/
│   │   │   ├── (auth)/         # Auth pages (login, register, forgot-password)
│   │   │   ├── (dashboard)/    # Protected dashboard pages
│   │   │   │   ├── page.tsx            # Dashboard home with KPIs
│   │   │   │   ├── discovery/          # Freelancer search & discovery
│   │   │   │   ├── pitches/            # Pitch windows & submissions
│   │   │   │   │   └── [id]/           # Pitch window detail
│   │   │   │   ├── assignments/        # Assignment management
│   │   │   │   │   └── [id]/           # Assignment detail
│   │   │   │   ├── payments/           # Payment tracking
│   │   │   │   ├── squads/             # Team management
│   │   │   │   ├── portfolio/          # Freelancer portfolio
│   │   │   │   └── settings/           # User settings
│   │   │   ├── layout.tsx      # Root layout
│   │   │   └── globals.css     # Design tokens & theme
│   │   ├── components/
│   │   │   ├── ui/             # shadcn/ui primitives
│   │   │   ├── layouts/        # Sidebar, Header, PageWrapper
│   │   │   ├── features/       # Feature-specific components
│   │   │   │   ├── discovery/  # FreelancerCard, SearchFilters, OpportunityCard
│   │   │   │   ├── pitches/    # StatusBadge, PitchWindowForm, SubmitPitchForm
│   │   │   │   ├── assignments/# AssignmentStatusBadge
│   │   │   │   └── payments/   # PaymentStatusBadge
│   │   │   └── shared/         # ErrorBoundary, EmptyState, LoadingSkeleton
│   │   ├── lib/
│   │   │   ├── api/            # API client & auth functions
│   │   │   ├── hooks/          # Zustand auth store
│   │   │   └── validations/    # Zod schemas
│   │   └── types/              # TypeScript type definitions
│   └── package.json
├── services/
│   ├── identity/               # User auth & profiles (port 8001)
│   ├── discovery/              # Talent search & squads (port 8002)
│   ├── pitch/                  # Pitch windows & assignments (port 8003)
│   ├── payment/                # Payments & compliance (port 8004)
│   └── ml/                     # ML scoring & matching (port 8005)
├── shared/
│   ├── db/                     # Database utilities
│   ├── auth/                   # JWT utilities
│   ├── logging/                # Logging configuration
│   └── errors/                 # Error handling
├── migrations/                 # Global Alembic migrations
└── scripts/                    # Utility scripts
```

## Frontend Routes

| Route | Description | Role |
|-------|-------------|------|
| `/login` | User login | Public |
| `/register` | Account registration (freelancer or editor) | Public |
| `/forgot-password` | Password reset request | Public |
| `/` | Dashboard with KPI stats | Authenticated |
| `/discovery` | Search and filter freelancers | Editor |
| `/pitches` | Pitch windows inbox with tabs | Editor |
| `/pitches/[id]` | Pitch window detail with submissions | Editor |
| `/assignments` | Assignment list with status tracking | Both |
| `/assignments/[id]` | Assignment detail with timeline | Both |
| `/payments` | Payment history with escrow tracking | Both |
| `/squads` | Team management and member organization | Editor |
| `/portfolio` | Freelancer portfolio and scores | Freelancer |
| `/settings` | Profile, notifications, and security | Authenticated |

## API Reference

### Identity Service (Port 8001)

User authentication, profiles, and newsroom management.

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/auth/register` | Create user account |
| POST | `/api/v1/auth/login` | Get JWT tokens |
| POST | `/api/v1/auth/refresh` | Refresh access token |
| GET | `/api/v1/users/me` | Get current user profile |
| PATCH | `/api/v1/users/me` | Update current user profile |
| GET | `/api/v1/freelancers/{id}` | Get freelancer public profile |
| PATCH | `/api/v1/freelancers/me` | Update freelancer profile |
| POST | `/api/v1/freelancers/me/availability` | Set availability status |
| POST | `/api/v1/newsrooms` | Create a newsroom |
| GET | `/api/v1/newsrooms/{id}` | Get newsroom details |
| PATCH | `/api/v1/newsrooms/{id}` | Update a newsroom |
| POST | `/api/v1/newsrooms/{id}/members` | Add newsroom member |

### Discovery Service (Port 8002)

Freelancer search, filtering, and squad management.

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/discovery/search` | Search freelancers with filters |
| GET | `/api/v1/discovery/freelancers/{id}` | Get full freelancer profile |
| POST | `/api/v1/squads/templates` | Create squad template |
| GET | `/api/v1/squads/templates` | List squad templates |
| GET | `/api/v1/squads/templates/{id}` | Get squad template |
| PATCH | `/api/v1/squads/templates/{id}` | Update squad template |
| DELETE | `/api/v1/squads/templates/{id}` | Delete squad template |
| POST | `/api/v1/squads/instances` | Create squad from template |
| GET | `/api/v1/squads/instances` | List squad instances |
| GET | `/api/v1/squads/instances/{id}` | Get squad with members |
| POST | `/api/v1/squads/instances/{id}/activate` | Activate a squad |
| POST | `/api/v1/squads/instances/{id}/complete` | Complete a squad |
| POST | `/api/v1/squads/instances/{id}/disband` | Disband a squad |
| POST | `/api/v1/squads/instances/{id}/members` | Invite freelancer to squad |
| GET | `/api/v1/squads/invitations/my` | List my squad invitations |
| POST | `/api/v1/squads/members/{id}/respond` | Accept/decline invitation |
| DELETE | `/api/v1/squads/instances/{id}/members/{mid}` | Remove squad member |

### Pitch Service (Port 8003)

Pitch windows, submissions, and assignment lifecycle.

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/pitch-windows` | Create pitch window |
| GET | `/api/v1/pitch-windows` | List pitch windows |
| GET | `/api/v1/pitch-windows/{id}` | Get pitch window |
| PATCH | `/api/v1/pitch-windows/{id}` | Update pitch window |
| POST | `/api/v1/pitch-windows/{id}/open` | Open window for submissions |
| POST | `/api/v1/pitch-windows/{id}/close` | Close pitch window |
| POST | `/api/v1/pitches` | Create a pitch |
| GET | `/api/v1/pitches/my` | List my pitches |
| GET | `/api/v1/pitches/window/{id}` | List pitches for a window |
| GET | `/api/v1/pitches/{id}` | Get pitch details |
| PATCH | `/api/v1/pitches/{id}` | Update draft pitch |
| POST | `/api/v1/pitches/{id}/submit` | Submit pitch for review |
| POST | `/api/v1/pitches/{id}/review` | Accept or reject pitch |
| POST | `/api/v1/pitches/{id}/withdraw` | Withdraw a pitch |
| GET | `/api/v1/assignments/my` | List my assignments |
| GET | `/api/v1/assignments/newsroom` | List newsroom assignments |
| GET | `/api/v1/assignments/{id}` | Get assignment details |
| PATCH | `/api/v1/assignments/{id}` | Update assignment |
| POST | `/api/v1/assignments/{id}/status` | Update assignment status |
| POST | `/api/v1/webhooks/cms/webhook` | Handle CMS webhook events |

### Payment Service (Port 8004)

Payments, escrow, compliance, and ledger.

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/payments` | Create a payment |
| GET | `/api/v1/payments/my` | List my payments |
| GET | `/api/v1/payments/newsroom` | List newsroom payments |
| GET | `/api/v1/payments/{id}` | Get payment details |
| POST | `/api/v1/payments/{id}/escrow` | Hold funds in escrow |
| POST | `/api/v1/payments/{id}/release` | Release from escrow |
| POST | `/api/v1/payments/{id}/complete` | Complete payment |
| POST | `/api/v1/payments/{id}/refund` | Refund a payment |
| POST | `/api/v1/webhooks/stripe` | Handle Stripe webhooks |
| GET | `/api/v1/compliance/my` | Get my compliance record |
| GET | `/api/v1/compliance/summary` | Get tax year summary |
| GET | `/api/v1/compliance/{id}` | Get freelancer compliance |
| GET | `/api/v1/ledger/my` | List my ledger entries |
| GET | `/api/v1/ledger/balance` | Get current balance |

### ML Service (Port 8005)

Portfolio analysis, style matching, duplicate detection, and trust scoring.

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/portfolio/ingest` | Ingest portfolio URLs |
| GET | `/api/v1/portfolio/my` | List my portfolio items |
| GET | `/api/v1/portfolio/{id}` | Get portfolio item |
| GET | `/api/v1/portfolio/freelancer/{id}` | Get freelancer's portfolio |
| POST | `/api/v1/style/compute` | Compute style fingerprint |
| GET | `/api/v1/style/fingerprint/{type}/{id}` | Get style fingerprint |
| POST | `/api/v1/style/match` | Match freelancers to newsroom style |
| POST | `/api/v1/duplicate/check` | Check for duplicate content |
| POST | `/api/v1/trust-score/compute` | Compute trust score |
| GET | `/api/v1/trust-score/my` | Get my trust score |

All services expose `/health` and `/ready` endpoints for health and readiness checks.

## Authentication

All protected endpoints require JWT authentication via the `Authorization` header:

```
Authorization: Bearer <access_token>
```

Access tokens expire after 15 minutes. Use the refresh endpoint to obtain new tokens. Multi-tenant endpoints also accept `X-Newsroom-ID` header for newsroom context.

## Development

### Make Commands

| Command | Description |
|---------|-------------|
| `make build` | Build all Docker images |
| `make up` | Start all services |
| `make up-db` | Start only PostgreSQL and Redis |
| `make down` | Stop all services |
| `make logs` | Tail logs from all services |
| `make migrate` | Run Alembic migrations for all services |
| `make test` | Run tests with coverage for all services |
| `make test-identity` | Run tests for identity service only |
| `make test-discovery` | Run tests for discovery service only |
| `make test-pitch` | Run tests for pitch service only |
| `make test-payment` | Run tests for payment service only |
| `make test-ml` | Run tests for ML service only |
| `make lint` | Run flake8 and mypy |
| `make shell` | Open bash in identity container |
| `make db-shell` | Open psql shell |
| `make clean` | Remove all containers, volumes, and prune |
| `make init-db` | First-time database initialization |

### Running Services Locally

```bash
# Backend (any individual service)
make up-db                    # Start databases
make dev-identity             # Run identity service on :8001
make dev-discovery            # Run discovery service on :8002
make dev-pitch                # Run pitch service on :8003
make dev-payment              # Run payment service on :8004
make dev-ml                   # Run ML service on :8005

# Frontend
cd frontend
npm run dev                   # Start Next.js dev server on :3000
```

### Database Migrations

```bash
# Create a new migration
docker-compose exec identity alembic revision --autogenerate -m "description"

# Apply all migrations
make migrate

# Rollback last migration
docker-compose exec identity alembic downgrade -1
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `POSTGRES_DB` | Database name | `elastic_newsroom` |
| `POSTGRES_USER` | Database user | `newsroom_user` |
| `POSTGRES_PASSWORD` | Database password | `changeme_in_production` |
| `REDIS_HOST` | Redis hostname | `redis` |
| `REDIS_PORT` | Redis port | `6379` |
| `JWT_SECRET_KEY` | JWT signing key | (change in production) |
| `JWT_ALGORITHM` | JWT algorithm | `HS256` |
| `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` | Access token expiry | `15` |
| `JWT_REFRESH_TOKEN_EXPIRE_DAYS` | Refresh token expiry | `7` |
| `IDENTITY_SERVICE_PORT` | Identity service port | `8001` |
| `DISCOVERY_SERVICE_PORT` | Discovery service port | `8002` |
| `PITCH_SERVICE_PORT` | Pitch service port | `8003` |
| `PAYMENT_SERVICE_PORT` | Payment service port | `8004` |
| `ML_SERVICE_PORT` | ML service port | `8005` |
| `STRIPE_SECRET_KEY` | Stripe secret key | `sk_test_...` |
| `STRIPE_PUBLISHABLE_KEY` | Stripe publishable key | `pk_test_...` |
| `STRIPE_WEBHOOK_SECRET` | Stripe webhook secret | `whsec_...` |
| `PLATFORM_FEE_PERCENTAGE` | Platform fee percentage | `10.0` |
| `CMS_WEBHOOK_SECRET` | CMS webhook secret | `disabled` |
| `EMBEDDING_MODEL` | ML embedding model | `all-MiniLM-L6-v2` |
| `ENVIRONMENT` | Runtime environment | `development` |
| `DEBUG` | Enable debug mode | `true` |
| `LOG_LEVEL` | Logging level | `INFO` |
| `CORS_ORIGINS` | Allowed CORS origins | `http://localhost:3000,...` |

### Frontend Environment Variables

Create `frontend/.env.local` to override API URLs:

```bash
NEXT_PUBLIC_IDENTITY_API_URL=http://localhost:8001
NEXT_PUBLIC_DISCOVERY_API_URL=http://localhost:8002
NEXT_PUBLIC_PITCH_API_URL=http://localhost:8003
NEXT_PUBLIC_PAYMENT_API_URL=http://localhost:8004
NEXT_PUBLIC_ML_API_URL=http://localhost:8005
```

## License

Confidential - Internal Use Only
