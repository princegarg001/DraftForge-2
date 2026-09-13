# Runbooks

Procedures for the alerts that fire. Each starts from the alert and ends at a
decision.

## HighErrorRate

> Over 5% of requests failing for 5 minutes.

1. Open **API Health** → *Errors by endpoint*. One endpoint or all of them?
2. One endpoint → filter Loki by that path, read the exception, click through to
   the trace.
3. All endpoints → check dependencies at `GET /api/v1/health` (authenticated).
   A single unreachable service usually explains it.
4. If it began at a deploy, roll back by redeploying the previous commit from
   the Render dashboard.

**Escalate** if error rate exceeds 20% or persists beyond 15 minutes.

## LLMTokenBurnRateHigh

> Projected burn above 500k tokens/hour.

This is a cost alert. Act on it before the bill lands.

1. **LLM Cost & Performance** → *Token share by operation*. Which feature?
2. Prompt tokens climbing while calls stay flat → context bloat, likely
   unbounded conversation memory. Check document-memory summarisation.
3. Calls climbing → identify the user via traces. Is a legitimate class session
   running, or is one account looping?
4. Immediate lever: lower `RATE_LIMIT_LLM_PER_DAY` or
   `LLM_TOKEN_BUDGET_PER_DAY` and redeploy.
5. Abusive account: set `profiles.is_active = false`. Takes effect on their next
   request, because the role and status are read from the database each time.

## RetrievalScoreDegraded

> Median top similarity below 0.45 for 30 minutes.

Retrieval degrades silently — nothing errors, answers just get worse.

1. **Retrieval & Evaluation Quality** → is it all document types or one?
   One type points at that corpus; all types point at the embedding model or
   Qdrant.
2. Confirm the collection is populated:
   ```bash
   curl -H "api-key: $QDRANT_API_KEY" \
     "$QDRANT_URL/collections/legal_reference_corpus"
   ```
3. Check `EMBEDDING_MODEL` has not changed. **A different model makes existing
   vectors meaningless** — they were written in a different space. Changing it
   requires re-indexing the whole corpus, not just a redeploy.
4. If the collection is empty or wrong, re-upload reference documents through
   the instructor portal.

## RetrievalReturningNothing

> p90 result count below 1.

More urgent than the above: evaluations will produce findings with no citations.

1. Check Qdrant reachability and the collection's point count.
2. If the collection is missing, the backend recreates it empty on start — it
   does **not** re-index. Reference documents must be re-uploaded.
3. Check the `document_type` filter is not excluding everything.

## InvitationEmailsFailing

> Over 10% of invitations undelivered.

Critical, because a student with no invitation cannot join at all.

1. Query recent failures:
   ```sql
   select status, last_error, count(*)
   from email_outbox
   where created_at > now() - interval '1 hour'
   group by 1, 2 order by 3 desc;
   ```
2. `BOUNCED` → permanent. Usually an unverified sending domain or a bad address.
   Check the domain's DKIM/SPF in the Resend dashboard.
3. `FAILED` → transient, retries exhausted. Check Resend status and the API key.
4. After fixing: instructors must **resend**. Failed invitations are not
   replayable by design — the outbox never stored the token — and resending
   mints a fresh one.

## AuthFailureSpike

> More than 5 auth failures/sec for 5 minutes.

1. **API Health** → *Authentication outcomes*. Single source or distributed?
2. Find source addresses in Loki:
   ```
   {app="draftforge"} |= "Failed login" | json
   ```
3. Single IP → add a Cloudflare block rule.
4. Distributed → credential stuffing. Tighten `RATE_LIMIT_AUTH_PER_MINUTE` and
   consider requiring a password reset for any account that was accessed.
5. Confirm the auth limits are actually engaging — check `RateLimitSaturation`
   on the same dashboard. If they are not, verify Redis is reachable and
   `REDIS_REQUIRED` is set.

## Suspected credential compromise

1. **Rotate first, investigate second.** Rotate the affected key in its
   provider's console.
2. Update the value in Render (or via Terraform) and redeploy.
3. For the Supabase service-role key, rotate immediately — it bypasses RLS and
   grants full database access.
4. Read `audit_log` for the exposure window:
   ```sql
   select * from audit_log
   where created_at between $start and $end
   order by created_at;
   ```
5. Check gitleaks history results — if the key was ever committed, it is in the
   history regardless of later removal.

## Rolling back a deploy

Render keeps previous deploys. Redeploy the last good one from the dashboard, or
revert the commit and let the pipeline run.

::: warning Migrations do not roll back
Reverting application code does not undo a migration. If the bad deploy included
one, write a forward migration that reverses it. Restoring a Supabase backup
loses every write since the snapshot.
:::

## Useful queries

::: details Recent grade overrides
```sql
select a.created_at, p.email as instructor, a.subject_id as student,
       a.details->>'previous_score' as was,
       a.details->>'new_score' as now,
       a.details->>'reason' as reason
from audit_log a
join profiles p on p.id = a.actor_id
where a.action = 'grade.overridden'
order by a.created_at desc limit 50;
```
:::

::: details Invitations pending longer than three days
```sql
select c.name as class, i.email, i.created_at, i.send_count
from invitations i
join classes c on c.id = i.class_id
where i.status = 'PENDING'
  and i.created_at < now() - interval '3 days'
order by i.created_at;
```
:::

::: details Tables missing row-level security
```sql
select tablename from pg_tables
where schemaname = 'public' and not rowsecurity;
```
Should always return zero rows. CI asserts this on every migration change.
:::
