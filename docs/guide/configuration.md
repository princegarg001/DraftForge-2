# Configuration

All settings live in `backend/app/config.py`, loaded from the environment and
validated by Pydantic at startup. The full list is in
[Environment variables](/reference/environment).

## Fail fast, loudly

Configuration is validated **at import**, not on first use. An invalid setting
stops the process from starting rather than surfacing as a strange error hours
later under load.

Production additionally enforces invariants that development does not:

```python
if not self.RATE_LIMIT_ENABLED:
    raise ValueError("RATE_LIMIT_ENABLED must be True in production.")
if not self.REDIS_REQUIRED:
    raise ValueError("REDIS_REQUIRED must be True in production, …")
```

A deployment silently running with rate limiting off or wildcard CORS is worse
than one that refuses to boot and explains why.

## Environments

| | development | staging | production |
| :--- | :--- | :--- | :--- |
| `DEBUG` | allowed | allowed | **forbidden** |
| Localhost CORS origins | auto-added | auto-added | **never** |
| Origin scheme | any | any | **https only** |
| `TRUSTED_HOSTS` | `*` allowed | `*` allowed | **must be explicit** |
| `/docs` | optional | optional | **forced off** |
| Rate limiting | may fail open | may fail open | **must fail closed** |
| Email | `console` allowed | real | **real required** |

## CORS

```bash
ALLOWED_ORIGINS="https://app.example.edu,https://staging.example.edu"
```

Exact origins only. `*` is rejected at startup.

::: danger Never widen this with a pattern
The original configuration used
`allow_origin_regex=r"^https://.*\.onrender\.com$"` with credentials enabled —
so any hostname obtainable by deploying to Render could make credentialed
requests and read the responses.

If a new origin needs access, add the exact origin.
:::

## Rate limits

Defaults suit a classroom. Adjust if legitimate use trips them:

```bash
RATE_LIMIT_LLM_PER_MINUTE=10
RATE_LIMIT_LLM_PER_DAY=300
LLM_TOKEN_BUDGET_PER_DAY=150000
```

Check the rate-limit panel on the API Health dashboard before loosening
anything — saturation is as often an abusive client as it is a limit set too
tight, and the two have opposite fixes.

## Secrets

**In development:** a `.env` file, which `.gitignore` excludes.

**In deployment:** environment variables set by Terraform from repository
secrets. Never a `.tfvars` file — `.gitignore` excludes those too, and
Terraform state stores every value in plaintext.

Rotation: change it in the provider, update the repository secret, re-apply
Terraform, redeploy. Rotate the Supabase service-role key first if several are
affected; it bypasses RLS.

## Adding a setting

1. Add the field to `Settings` with a type and default.
2. Add a `field_validator` if it has constraints.
3. Add it to the production invariants if it can be unsafe.
4. Document it in `.env.example` with a comment explaining *why*, not just what.
5. Add it to the Terraform module.
6. Add it to [Environment variables](/reference/environment).
7. Add a test if it is security-relevant — see
   `tests/security/test_config_invariants.py`.

Step 7 has already paid for itself once: writing those tests surfaced that
`RATE_LIMIT_ENABLED=False` passed production validation and disabled rate
limiting entirely.
