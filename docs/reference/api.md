# API endpoints

60 endpoints under `/api/v1`. The interactive schema is at `/docs` in
non-production environments.

## Conventions

**Authentication** — `Authorization: Bearer <jwt>` on everything except the
public endpoints marked below.

**Errors** — uniform envelope:

```json
{ "code": "permission_denied", "detail": "…", "request_id": "a1b2c3…" }
```

Branch on `code`; the prose is free to change. Quote `request_id` when
reporting a problem — it is in the response header too.

**404 for unauthorized resources** — accessing something you do not own returns
404, not 403. A 403 would confirm it exists.

## System

| Method | Path | Access |
| :--- | :--- | :--- |
| `GET` | `/` | Public |
| `GET` | `/health` | Public — shallow liveness |
| `GET` | `/api/v1/health` | **Authenticated** — dependency status |

`/api/v1/health` probes four services per call, so it is authenticated: open
access is both an amplification vector and a readout of which dependencies are
down.

## Authentication

| Method | Path | Access | Notes |
| :--- | :--- | :--- | :--- |
| `POST` | `/auth/register` | Public | Always creates a **STUDENT**. No `role` field. |
| `POST` | `/auth/register-faculty` | Public | Requires a valid registration code |
| `POST` | `/auth/login` | Public | Rate limited 5/min, 30/hr |
| `POST` | `/auth/refresh` | Public | Rotates the refresh token |
| `POST` | `/auth/logout` | Public | Revokes server-side; always 204 |
| `GET` | `/auth/me` | Authenticated | **Authoritative** role and status |

## Invitations

| Method | Path | Access |
| :--- | :--- | :--- |
| `GET` | `/invitations/preview?token=` | Public |
| `POST` | `/invitations/accept` | Public |

The only unauthenticated write endpoints, rate limited under the auth scope.
The email comes from the invitation record, never the request body.

## Classes & roster

| Method | Path | Access |
| :--- | :--- | :--- |
| `POST` | `/classes` | Teacher |
| `GET` | `/classes` | Teacher — own classes |
| `GET` | `/classes/enrolled` | Student |
| `GET` `PATCH` | `/classes/{id}` | Teacher — owner |
| `POST` | `/classes/{id}/rotate-join-code` | Teacher — owner |
| `GET` | `/classes/{id}/roster` | Teacher — owner |
| `POST` | `/classes/{id}/invitations` | Teacher — owner |
| `GET` | `/classes/{id}/invitations` | Teacher — owner |
| `POST` | `/classes/{id}/invitations/resend` | Teacher — owner |
| `DELETE` | `/classes/{id}/invitations/{iid}` | Teacher — owner |
| `DELETE` | `/classes/{id}/roster/{eid}` | Teacher — owner |

Bulk invite returns **202**: the roster updates synchronously, delivery happens
out of band.

## Drafts

| Method | Path | Access |
| :--- | :--- | :--- |
| `POST` | `/drafts` | Student |
| `POST` | `/drafts/upload` | Student — 40/hr, 15 MB |
| `GET` | `/drafts` | Student — own |
| `GET` | `/drafts/{id}` | Student — owner |
| `POST` | `/drafts/{id}/versions` | Student — owner |
| `GET` | `/drafts/{id}/compare?v1=&v2=` | Student — owner |

## Evaluation

| Method | Path | Access |
| :--- | :--- | :--- |
| `POST` | `/evaluations` | Student — owner of the draft |
| `GET` | `/evaluations/{id}` | Owner, their instructor, or admin |
| `GET` | `/loopholes/{id}` | Owner, their instructor, or admin |

## AI (rate limited, token budgeted)

| Method | Path | Access |
| :--- | :--- | :--- |
| `POST` | `/ai/explain-evaluation` | Authenticated |
| `POST` | `/ai/assist-drafting` | Authenticated |
| `POST` | `/rag/retrieve` | Authenticated |
| `POST` | `/chat/send` | Authenticated |
| `POST` `GET` | `/conversations` | Student — own |
| `GET` | `/conversations/{id}/messages` | Student — owner |

## Learning

| Method | Path | Access |
| :--- | :--- | :--- |
| `GET` | `/skills/my-skills` | Student |
| `GET` `POST` | `/roadmap`, `/roadmap/generate` | Student |
| `PATCH` | `/roadmap/items/{id}/complete` | Student — owner |
| `GET` | `/quizzes`, `/quizzes/{id}` | Authenticated |
| `POST` | `/quizzes/submit` | Student |
| `GET` | `/exercises`, `/exercises/{id}`, `/exercises/my-attempts` | Student |
| `POST` | `/exercises/attempt` | Student |
| `GET` | `/progress` | Student |
| `GET` | `/leaderboard` | **Class-scoped** |

Quiz and exercise responses never include `correct_option` or `model_solution` —
withheld by column-level grants.

## Coursework

| Method | Path | Access |
| :--- | :--- | :--- |
| `POST` | `/assignments` | Teacher |
| `GET` | `/assignments`, `/assignments/{id}` | Student — their classes |
| `GET` | `/teachers/assignments` | Teacher — own |
| `POST` | `/submissions` | Student — owner of the draft |
| `GET` | `/submissions/assignment/{id}` | Teacher — owner of the assignment |
| `POST` | `/submissions/{id}/override` | Teacher — owner; **audited** |

## Documents

| Method | Path | Access |
| :--- | :--- | :--- |
| `POST` | `/documents/reference/upload` | Teacher — audited |
| `GET` | `/documents/reference` | Authenticated |
| `POST` | `/documents/classify` | **Authenticated** (was public) |

## Analytics

| Method | Path | Access |
| :--- | :--- | :--- |
| `GET` | `/analytics/cohort?class_id=` | Teacher — own classes only |
| `GET` | `/teachers/cohort-analytics` | Teacher — own classes only |

::: warning Both were global
These aggregated every profile, evaluation and skill record in the database, so
an instructor's "cohort" dashboard described the entire platform. Now scoped
through class membership.
:::

## Rate limits

| Scope | Limit | Applies to |
| :--- | :--- | :--- |
| `AUTH` | 5/min, 30/hr | Login, register, refresh, invitations |
| `LLM` | 10/min, 300/day | Chat, AI assist, RAG, roadmap generation |
| `UPLOAD` | 40/hr | Draft and reference uploads |
| `INVITE` | 200/hr | Bulk invite and resend |
| `DEFAULT` | 120/min | Everything else |

Responses carry `X-RateLimit-Limit` and `X-RateLimit-Remaining`; a 429 carries
`Retry-After`.

LLM endpoints additionally charge a **daily token budget**
(`LLM_TOKEN_BUDGET_PER_DAY`), because request counts cannot bound spend.
