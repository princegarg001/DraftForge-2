# Audit log

Privileged actions are recorded to `audit_log`, added in migration 005.

## What is recorded

| Action | Recorded when |
| :--- | :--- |
| `grade.overridden` | An instructor changes a mark |
| `role.changed` | A role is granted or altered, including faculty registration |
| `reference.uploaded` | A precedent enters the corpus |
| `invite.issued` / `invite.revoked` / `invite.accepted` | Roster lifecycle |
| `account.deactivated` / `account.reactivated` | Access revoked or restored |

## Shape

```json
{
  "actor_id":    "…",
  "actor_role":  "TEACHER",
  "action":      "grade.overridden",
  "resource":    "submission",
  "resource_id": "…",
  "subject_id":  "… the affected student …",
  "details": {
    "previous_score": 62.0,
    "new_score": 71.0,
    "reason": "Clause present but matcher missed the archaic phrasing."
  },
  "ip_address": "…",
  "request_id": "a1b2c3…",
  "created_at": "…"
}
```

`subject_id` is separate from `actor_id` so "what was done to this student" is
answerable without scanning every entry's details.

`request_id` ties the entry to the logs and trace for the same request.

## Append-only

Migration 005 grants no `UPDATE` or `DELETE`:

```sql
REVOKE UPDATE, DELETE ON public.audit_log FROM authenticated, anon;
```

A compromised instructor session can therefore change a grade, but cannot erase
the record of having done so. That property is the entire point — an audit log
that the actor can edit is decoration.

Reads are admin-only.

## Writes never fail the action

Audit writes are best-effort. A failure is logged loudly but does not propagate:

```python
except Exception as exc:
    logger.error(f"AUDIT WRITE FAILED action={action.value} …")
```

Blocking an instructor's grade override on an audit-table hiccup trades a real
feature for a bookkeeping one. The loud log line is what surfaces the problem.

## What is deliberately absent

`details` is chosen by the caller and must stay free of credentials and
document text. The logging sink redacts secrets; the database does not.

Ordinary reads are not audited. Auditing every `SELECT` produces volume nobody
reads, which is indistinguishable from auditing nothing.
