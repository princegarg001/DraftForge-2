# Decision records

Decisions that are non-obvious, or that a future reader would otherwise be
likely to reverse without knowing what it cost.

---

## ADR-001 · Grading runs no model inference

**Accepted**

**Context.** Every comparable tool asks an LLM to grade. It is far less work.

**Decision.** The scorer is a rule engine. `app/ai/evaluation/` imports nothing
from `app/ai/llm/`.

**Why.** Model scores drift between runs on identical input, so a student can
resubmit unchanged work and receive a different mark — which is indefensible
when challenged. Models also hallucinate statutory citations, and a wrong
citation in a legal-education product teaches the wrong law.

**Cost.** Rubrics must be authored by hand for each document type, and the
scorer cannot reward good drafting that the rubric did not anticipate.

**Accepting that cost buys** a mark that is reproducible and attributable to a
named rule with cited evidence. That is the product.

---

## ADR-002 · Retrieval locates evidence; rules judge it

**Accepted**

**Context.** Grading uses vector search, which is not deterministic in the way a
rule is.

**Decision.** Retrieval answers *which passage corresponds to this requirement*.
Whether it satisfies the requirement is decided by rules.

**Why.** This keeps determinism intact. A retrieval drift changes which evidence
is cited — visible and debuggable — rather than whether a clause passes, which
would be a silent score change.

---

## ADR-003 · Roles are server-assigned, never client-supplied

**Accepted** · supersedes the original design

**Context.** The sign-up form offered a role dropdown, and the chosen value was
sent to the server and honoured.

**Decision.** `role` is absent from every request schema. Schemas use
`extra="forbid"`, so a client still sending one fails loudly. The role is read
from `profiles` on every request. Faculty registration is gated by a hashed,
use-limited institution code.

**Why.** Anyone could obtain instructor privileges: reference-corpus upload,
platform-wide analytics, and grade override on any submission.

**Note.** Removing the field alone would have been insufficient. Had faculty
sign-up stayed open, the same privileges would remain obtainable — just through
the front door.

---

## ADR-004 · Tokens are verified locally, not against Supabase

**Accepted** · supersedes the original design

**Context.** `supabase.auth.get_user(token)` ran on every authenticated request.

**Decision.** Verify the JWS locally against a cached JWKS, or the shared secret
for legacy HS256.

**Why.** The round trip added 100–300 ms to every endpoint and made Supabase
Auth a hard availability dependency. `SUPABASE_JWT_SECRET` was already
configured and simply unused.

**Consequence.** Revocation is no longer instant — a token remains valid until
it expires. Accepted because the access-token lifetime is short, and because
account deactivation *is* checked on every request via the profile lookup.

---

## ADR-005 · Unauthorized resources return 404, not 403

**Accepted**

**Decision.** Accessing a resource you do not own returns 404.

**Why.** A 403 confirms the record exists, which turns any id-taking endpoint
into an enumeration oracle. 404 is indistinguishable from a non-existent id.

**Cost.** Marginally worse debugging — a genuine 404 and a permission failure
look alike. The server log distinguishes them.

---

## ADR-006 · The outbox stores no template context

**Accepted**

**Context.** A transactional outbox normally queues the template plus its
variables for a worker to render later.

**Decision.** Invitations are rendered in-process and dispatched as a background
task. The outbox records only delivery metadata.

**Why.** The context would contain the raw invitation token, which would then
sit in a database row and in backups — defeating the point of storing only its
hash.

**Consequence.** A permanently failed invitation is not replayable. This is
correct: the instructor resends, minting a fresh token with a fresh expiry,
rather than resurrecting an old one.

---

## ADR-007 · Embeddings run in-process

**Accepted**

**Decision.** FastEmbed ONNX (`BAAI/bge-small-en-v1.5`, 384-dim) in-process,
rather than an embedding API.

**Why.** It removes a network hop from a path that runs several times per
evaluation, and no student draft text is sent to a third party for embedding —
a meaningful property for an education platform.

**Cost.** The model loads on first use, so a cold start is slow. Production
therefore runs two instances.

---

## ADR-008 · Terraform does not model Supabase, Qdrant or Neo4j

**Accepted**

**Decision.** Those three are provisioned by hand; their credentials are
variables.

**Why.** No provider can create a project or cluster for any of them. A module
that only pretends to manage a resource is worse than an honest gap: it implies
a destroy would clean up state it would leave behind, and a plan would detect
drift it cannot see.

The part that actually changes — the schema — is versioned in
`backend/migrations/`.

---

## ADR-009 · Rate limiting fails closed in production

**Accepted**

**Decision.** With `REDIS_REQUIRED`, an unavailable limiter rejects requests
rather than allowing them. Production requires both `REDIS_REQUIRED` and
`RATE_LIMIT_ENABLED`, validated at startup.

**Why.** Failing open means a Redis blip silently removes every limit —
including the ones bounding inference spend. A brief 429 is preferable to an
unbounded bill and unthrottled credential stuffing.

**Note.** The startup check originally required `REDIS_REQUIRED` only *while*
rate limiting was enabled, so `RATE_LIMIT_ENABLED=False` passed validation and
removed limits entirely. Writing the test for it surfaced that gap.

---

## ADR-010 · Class membership scopes analytics and leaderboards

**Accepted** · supersedes the original design

**Context.** Both aggregated every student in the database.

**Decision.** Scoped through `class_enrollments` — classmates for a student, the
classes they run for an instructor.

**Why.** Every student saw the names and mean scores of every other student on
the platform, across institutions. This is why the class model is a security fix
and not only a feature.
