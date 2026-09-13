# Local development

Assumes [Quickstart](/guide/quickstart) is done.

## Layout

```
DraftForge-2/
├── backend/          FastAPI
├── frontend/         React + Vite
├── docs/             This site
├── observability/    Local LGTM stack
├── terraform/        Infrastructure
└── .github/          CI/CD
```

## Daily loop

```bash
# terminal 1
cd backend && uvicorn app.main:app --reload --port 8000

# terminal 2
cd frontend && npm run dev

# terminal 3 (optional)
cd docs && npm run dev
```

## Tests

```bash
cd backend

pytest -q                          # everything
pytest tests/security -q           # Phase 1 regression tests
pytest tests/unit -q               # fast, no services needed
pytest --cov=app --cov-report=html # coverage → htmlcov/
pytest -k "invitation" -v          # by name
```

`tests/conftest.py` installs test-safe configuration **before** any `app`
import, because `app.config` builds its Settings at import time. No real
credentials are needed, and a developer's `.env` cannot leak into a test run.

## Lint and format

```bash
cd backend
ruff check app tests --fix
ruff format app tests
mypy app
```

Or install the hooks so CI failures surface before push:

```bash
pip install pre-commit
pre-commit install
pre-commit run --all-files
```

## Frontend

```bash
cd frontend
npx tsc --noEmit    # type check only
npm run build       # tsc + vite build
npm run preview     # serve the build
```

## Migrations

Plain SQL in `backend/migrations/`, applied in filename order.

To add one:

1. Create `007_your_change.sql`.
2. Make it idempotent where practical — `IF NOT EXISTS`, and
   `DROP POLICY IF EXISTS` before `CREATE POLICY`.
3. **Enable RLS on any new table.** CI fails the build otherwise.
4. Run it in the Supabase SQL Editor.
5. Update [Data model](/architecture/data-model).

::: warning There is no down migration
Reverting application code does not undo a migration. Write a forward migration
that reverses it instead.
:::

## Adding an endpoint

1. Schema in `app/models/schemas/`.
2. Business logic in `app/services/` — not in the router.
3. Queries in `app/db/repositories/`.
4. Router in `app/api/v1/`, registered in `router.py`.
5. Apply the right dependencies:
   ```python
   dependencies=[Depends(require_student), Depends(RateLimit(LimitScope.LLM))]
   ```
6. **Verify ownership in the service.** The role gate says the caller is *a*
   student; it does not say the row is theirs. This is where the Phase 1 bugs
   came from.
7. Add an RLS policy if it touches a new table.
8. Test it — a security test if it touches authorization.

## Local checks that mirror CI

```bash
# backend
cd backend && ruff check app tests && pytest -q

# frontend
cd frontend && npx tsc --noEmit && npm run build

# secrets
gitleaks detect --config .gitleaks.toml

# docs
cd docs && npm run build
```

## Tips

::: details Testing the invitation flow without email
`EMAIL_PROVIDER=console` prints the rendered message, link included, to the
backend terminal.
:::

::: details Exercising rate limits locally
They fail open without Redis, so a regression would not show up. Run Redis and
set `REDIS_REQUIRED=True`.
:::

::: details Seeing traces locally
Start the observability stack, set `OTEL_ENABLED=True` and
`OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4318`, then open Grafana at
:3001.
:::

::: details Speeding up the test loop
`pytest tests/unit tests/security -q` needs no cloud SDKs and runs in seconds.
:::
