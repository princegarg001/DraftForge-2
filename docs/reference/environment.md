# Environment variables

Defined in `backend/app/config.py` and validated at startup. Full template:
`backend/.env.example`.

::: danger Never prefix a secret with `VITE_`
Vite inlines every `VITE_`-prefixed variable into the shipped browser bundle.
A key named that way is public the moment it deploys, and the failure is
silent. CI greps the build output for this.

`VITE_API_URL` is the only frontend variable, and it is meant to be public.
:::

## Application

| Variable | Default | Notes |
| :--- | :--- | :--- |
| `ENVIRONMENT` | `production` | `development` / `staging` / `production` |
| `DEBUG` | `False` | Must be `False` in production |
| `PORT` | `8000` | Platform-injected |
| `ALLOWED_ORIGINS` | — | Comma-separated **exact** origins. `*` rejected; https required in production |
| `TRUSTED_HOSTS` | `*` | Must be explicit in production |
| `ENABLE_DOCS` | `False` | Forced off in production |
| `APP_PUBLIC_URL` | localhost | Builds invitation links; https in production |

Localhost origins are injected automatically outside production and **never**
in production.

## Supabase — required

| Variable | Notes |
| :--- | :--- |
| `SUPABASE_URL` | Also derives the JWKS URL and expected issuer |
| `SUPABASE_ANON_KEY` | |
| `SUPABASE_SERVICE_ROLE_KEY` | **Bypasses RLS.** Backend only |
| `SUPABASE_JWT_SECRET` | Used for legacy HS256 verification |

## JWT

| Variable | Default | Notes |
| :--- | :--- | :--- |
| `JWT_AUDIENCE` | `authenticated` | |
| `JWT_LEEWAY_SECONDS` | `30` | Clock-skew tolerance |
| `JWKS_CACHE_TTL_SECONDS` | `600` | |
| `JWKS_REFRESH_COOLDOWN_SECONDS` | `30` | Stops unknown-`kid` tokens amplifying into one fetch per request |

## Data stores — required

`NEO4J_URI`, `NEO4J_USERNAME`, `NEO4J_PASSWORD`, `NEO4J_DATABASE`,
`QDRANT_URL`, `QDRANT_API_KEY`, `QDRANT_COLLECTION_NAME`.

## LLM & embeddings

| Variable | Default |
| :--- | :--- |
| `LLM_PROVIDER` | `groq` |
| `GROQ_API_KEY` | — |
| `GROQ_MODEL` | `llama-3.3-70b-versatile` |
| `EMBEDDING_MODEL` | `BAAI/bge-small-en-v1.5` |
| `LLM_REQUEST_TIMEOUT_SECONDS` | `45.0` |

::: warning Changing `EMBEDDING_MODEL` invalidates the index
Existing vectors were written in a different space and become meaningless.
Changing it requires re-indexing the entire corpus, not just a redeploy.
:::

## Rate limiting

| Variable | Default | Notes |
| :--- | :--- | :--- |
| `REDIS_URL` | localhost | |
| `REDIS_REQUIRED` | `False` | **Must be `True` in production** — otherwise limits fail open |
| `RATE_LIMIT_ENABLED` | `True` | **Must be `True` in production** |
| `RATE_LIMIT_AUTH_PER_MINUTE` | `5` | |
| `RATE_LIMIT_AUTH_PER_HOUR` | `30` | |
| `RATE_LIMIT_LLM_PER_MINUTE` | `10` | |
| `RATE_LIMIT_LLM_PER_DAY` | `300` | |
| `RATE_LIMIT_UPLOAD_PER_HOUR` | `40` | |
| `RATE_LIMIT_INVITE_PER_HOUR` | `200` | |
| `LLM_TOKEN_BUDGET_PER_DAY` | `150000` | `0` disables; request counts alone cannot bound spend |

## Request limits

| Variable | Default |
| :--- | :--- |
| `MAX_REQUEST_BYTES` | 20 MB |
| `MAX_UPLOAD_BYTES` | 15 MB |
| `HSTS_MAX_AGE_SECONDS` | 2 years |

## Email

| Variable | Default | Notes |
| :--- | :--- | :--- |
| `EMAIL_PROVIDER` | `console` | `console` prints instead of sending; rejected in production |
| `RESEND_API_KEY` | — | Required when provider is `resend` |
| `EMAIL_FROM_ADDRESS` | — | Domain must be verified with the provider |
| `INVITE_TOKEN_TTL_HOURS` | `168` | 7 days |

## Observability

| Variable | Default | Notes |
| :--- | :--- | :--- |
| `OTEL_ENABLED` | `False` | Everything is a no-op when false |
| `OTEL_EXPORTER_OTLP_ENDPOINT` | — | e.g. `http://localhost:4318` |
| `OTEL_EXPORTER_OTLP_HEADERS` | — | `key=value,key2=value2` |
| `OTEL_TRACES_SAMPLER_RATIO` | `1.0` | 0.25 in production |
| `LOG_FORMAT` | `console` | Use `json` in deployed environments |
| `LOG_LEVEL` | `INFO` | |

## Production invariants

Startup fails unless all hold:

```
DEBUG                = False
ALLOWED_ORIGINS      ⊇ one https origin, no "*"
TRUSTED_HOSTS        ≠ "*"
RATE_LIMIT_ENABLED   = True
REDIS_REQUIRED       = True
EMAIL_PROVIDER       ≠ "console"
RESEND_API_KEY       set when provider is resend
APP_PUBLIC_URL       starts with https://
```

Failing to start is deliberate. A production deployment silently running with
rate limiting disabled or wildcard CORS is worse than one that refuses to boot
and says why.
