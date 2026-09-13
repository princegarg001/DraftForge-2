# Quickstart

Getting DraftForge running locally.

## Prerequisites

- **Python** 3.11 or 3.12
- **Node.js** 18+
- **Docker** (optional, for Redis and the observability stack)
- Accounts on [Supabase](https://supabase.com), [Qdrant Cloud](https://cloud.qdrant.io), [Neo4j Aura](https://neo4j.com/cloud/aura/) and [Groq](https://console.groq.com)

The four managed services all have free tiers sufficient for development.

## 1 · Provision the managed services

::: details Supabase
1. Create a project.
2. In the SQL Editor, run the migrations **in order**: `001` → `006` from `backend/migrations/`.
3. Create three storage buckets: `reference-documents`, `student-drafts`, `assignment-submissions`.
4. From Settings → API, copy the project URL, the `anon` key, the `service_role` key and the JWT secret.

The `service_role` key bypasses row-level security. It belongs only in the
backend environment — never in the frontend, and never in a `VITE_`-prefixed
variable.
:::

::: details Qdrant
Create a cluster and copy its URL and API key. The backend creates the
`legal_reference_corpus` collection on first start (384 dimensions, cosine).
:::

::: details Neo4j Aura
Create a free AuraDB instance. Save the connection URI, username and generated
password — the password is shown once.
:::

::: details Groq
Create an API key at the Groq console. Only the generative features need it;
evaluation runs without any LLM.
:::

## 2 · Backend

```bash
cd backend

python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\Activate.ps1

pip install -r requirements.txt -r requirements-dev.txt

cp .env.example .env
```

Edit `.env` and fill in the credentials from step 1. For local work:

```bash
ENVIRONMENT="development"
DEBUG=True
EMAIL_PROVIDER="console"     # prints invitations to stdout, sends nothing
REDIS_REQUIRED=False         # rate limiting fails open without Redis
ENABLE_DOCS=True
```

Start it:

```bash
uvicorn app.main:app --reload --port 8000
```

- API — <http://localhost:8000>
- Swagger — <http://localhost:8000/docs>

## 3 · Redis (recommended)

Without Redis the rate limiter fails open, so limits are not exercised at all
in development and a regression in them would not show up until production.

```bash
docker run -d --name draftforge-redis -p 6379:6379 redis:7.4-alpine
```

Then set `REDIS_REQUIRED=True` and `RATE_LIMIT_ENABLED=True`.

## 4 · Frontend

```bash
cd frontend
npm install

cp .env.example .env    # VITE_API_URL=http://localhost:8000/api/v1
npm run dev
```

The app is at <http://localhost:5173>.

## 5 · Create your first account

Students cannot self-register — that is the whole point of the
[onboarding flow](/flows/onboarding). Bootstrap an instructor instead.

Insert a faculty registration code. The **hash** is stored, so generate a code
and hash it:

```bash
python -c "import hashlib; code='LOCAL-DEV-CODE-001'; print(hashlib.sha256(code.encode()).hexdigest())"
```

Then in the Supabase SQL Editor:

```sql
insert into public.faculty_registration_codes (code_hash, label, max_uses)
values ('<paste the hash>', 'Local development', 10);
```

Now register at <http://localhost:5173> under **Faculty Sign-Up**, using
`LOCAL-DEV-CODE-001`.

From there: create a class, add a student email, and — because
`EMAIL_PROVIDER=console` — the invitation link is printed to the backend
terminal. Paste it into a browser to complete the student side.

## 6 · Seed the reference corpus (optional)

Evaluation works without it, but clause-coverage findings will have no citations
to point at. Upload reference documents through the instructor portal
(**Ingest Reference Corpus**), or seed the knowledge graph:

```bash
cd backend
python scripts/seed_knowledge_graph.py
```

## 7 · Observability (optional)

```bash
docker compose -f observability/docker-compose.observability.yml up -d
```

Then in `backend/.env`:

```bash
OTEL_ENABLED=True
OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4318
LOG_FORMAT=json
```

Grafana is at <http://localhost:3001> with the three dashboards pre-provisioned.
See [Observability](/operations/observability).

## Verify

```bash
cd backend
pytest -q                    # full suite
pytest tests/security -q     # the Phase 1 regression tests

cd ../frontend
npm run build                # tsc + vite build
```

## Troubleshooting

::: details Startup fails with a long pydantic validation error
`ENVIRONMENT=production` enforces invariants that development does not: no
`DEBUG`, https-only origins, explicit trusted hosts, rate limiting on and
failing closed, a real email provider. Use `ENVIRONMENT=development` locally.
:::

::: details 401 on every request
Check `SUPABASE_URL` and `SUPABASE_JWT_SECRET`. Tokens are verified locally now,
so a wrong secret fails every request rather than only some.
:::

::: details Invitation emails never arrive
With `EMAIL_PROVIDER=console` they are never sent — the rendered message is
printed to the backend terminal, link included.
:::

::: details First evaluation is slow
FastEmbed downloads and caches its ONNX model on first use. Subsequent runs are
fast; production keeps a warm instance for this reason.
:::
