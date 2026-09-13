# Row-level security

Migration 005 enables RLS on all 23 tables and defines policies for each.

## Why it was needed

Migrations 001–004 created twenty-three tables and enabled RLS on **none** of
them. Authorization existed only in application code, so any path reaching the
database with a user-scoped key — a leaked anon key, a direct PostgREST call, a
future endpoint that forgets its check — had unrestricted access to every row.

## Current honest status

::: warning Read this before relying on RLS
The backend still connects with the **service-role key**, which is `BYPASSRLS`
by design. Today these policies defend against:

- a leaked or misused anon key,
- direct PostgREST access,
- anything using `get_user_scoped_client()`.

They are **not yet** the enforcement boundary for the API's own queries.
Migrating the repositories onto request-scoped clients is the remaining work;
`get_user_scoped_client()` exists for it. Until then, the application-layer
ownership checks are the primary control and RLS is the backstop for everything
else.
:::

## Helper functions

`SECURITY DEFINER`, because reading a role from `profiles` must not itself pass
through the `profiles` policies — without that, every policy calling these would
recurse.

| Function | Returns |
| :--- | :--- |
| `current_user_role()` | The caller's role, or null if inactive |
| `is_teacher()` / `is_admin()` | Role predicates |
| `owns_draft_version(uuid)` | Walks `draft_versions → drafts.user_id` |
| `teaches_evaluation(uuid)` | Whether the caller's assignment received it |
| `teaches_class(uuid)` | Class ownership |
| `is_enrolled_in(uuid)` | Active enrollment |
| `shares_class_with(uuid)` | Classmate test, for scoped leaderboards |

## Policy summary

| Table | Student | Teacher |
| :--- | :--- | :--- |
| `profiles` | Own row | Read all |
| `drafts` | Full on own | Read once submitted to their assignment |
| `draft_versions` | Full via parent draft | Read once submitted to theirs |
| `evaluations` | Read own | Read + override on their coursework only |
| `evaluation_evidence` | Read own | Read on their coursework |
| `conversations` / `messages` | Full on own | None |
| `roadmaps` / `roadmap_items` | Full on own | None |
| `student_skills` | Read own | Read all |
| `classes` | Read if enrolled | Full on own |
| `class_enrollments` | Read own row only | Full on own classes |
| `invitations` | None | Read on own classes |
| `assignments` | Read published in their classes | Full on own |
| `submissions` | Read own, insert own | Full via own assignments |
| `audit_log` | None | Admin read only |

`faculty_registration_codes` and `email_outbox` carry **no policies at all**.
With RLS enabled and nothing granted, they are reachable only by the service
role. Both hold credential-equivalent or personal data.

## `FORCE ROW LEVEL SECURITY`

Applied to every table alongside `ENABLE`. `ENABLE` alone exempts the table
owner, so a connection that happened to be owner-privileged would silently
bypass every policy.

## Column-level grants

RLS gates rows, not columns. A student permitted to read a quiz question would
also read its `correct_option`, and likewise `exercises.model_solution`.

```sql
REVOKE SELECT ON public.quiz_questions FROM authenticated, anon;
GRANT SELECT (id, quiz_id, question_text, options, order_index)
    ON public.quiz_questions TO authenticated;
```

`correct_option` and `explanation` are both omitted — each discloses the answer
before the attempt is graded. The service role, which grades the attempt, still
reads them.

## 404, not 403

Policies that deny a read make the row simply not exist for that caller, which
naturally produces a 404. The application deliberately matches this: returning
403 would confirm the row exists and turn the endpoint into an id oracle.

## Testing policies

Policies are not exercised by the current test suite, because doing so requires
a real Supabase project with `auth.uid()`. CI verifies structure instead:

- every migration applies cleanly in order,
- no public table lacks RLS.

Behavioural policy tests against a disposable Supabase project are the gap.
