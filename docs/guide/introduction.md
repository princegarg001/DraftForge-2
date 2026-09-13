# Introduction

DraftForge is a platform for teaching and assessing Indian statutory legal
drafting. Students write affidavits, employment agreements, rent agreements and
legal notices; the platform scores them against a calibrated rubric, cites the
precedent behind each finding, and tutors the student toward fixing the gaps
without writing the draft for them.

## The problem

Legal drafting is taught through repetition and correction, but correction does
not scale. A cohort of eighty students submitting three drafts each is 240
documents to mark by hand, and the marking is:

- **Slow**, so feedback arrives after the student has moved on.
- **Inconsistent**, because two examiners weight the same omission differently.
- **Unevidenced**, because "this clause is weak" does not tell a student which
  statute they failed to satisfy.

The obvious fix — hand the draft to a language model — introduces worse
problems. Model scores drift between runs on identical input, so a student can
resubmit unchanged work and get a different mark. Models hallucinate statutory
citations, confidently attributing a provision to the wrong Act. And a model
asked for feedback will usually just rewrite the draft, removing exactly the
work the exercise exists to make the student do.

## The approach

Grading is deterministic and generative assistance is separate.

### Grading runs no inference

The scorer is a rule engine. It classifies the document type, checks structural
elements, matches mandatory clauses against an indexed reference corpus, applies
formatting rules and subtracts gap penalties. Identical input produces an
identical score, every time, and each point traces to a named criterion.

Vector search is used inside grading, but only to *locate evidence* — to find
which passage of the student's draft corresponds to a required clause. The
decision about whether that clause is adequate is rule-based.

### Generation is confined to teaching

The AI tutor, the drafting assistant and the evaluation explainer all use an
LLM, and none of them can write to a score. The tutor is prompted to respond to
"what should this clause say?" with a question about the governing statute
rather than with the clause.

### Evidence is citable

Every finding records where the reference came from: source document, section,
page. A student disputing a mark is shown the rule, their text and the
precedent, rather than an opaque number.

## Who uses it

**Students** draft in a versioned workspace, request evaluation, review findings
with citations, work through a generated roadmap targeting their weak skills,
and discuss their draft with the tutor.

**Instructors** create classes, invite students by email, publish assignments,
audit submissions side by side with diffs, override scores with a recorded
reason, and read cohort-wide skill analytics.

Instructors are also the only route to an account: students do not self-register.
See [Onboarding & invitations](/flows/onboarding).

## Technology

| Layer | Choice |
| :--- | :--- |
| API | FastAPI (Python 3.11+), Pydantic v2 |
| Frontend | React 18, TypeScript, Vite, Tailwind |
| Relational store & auth | Supabase PostgreSQL, Supabase Auth |
| Vector search | Qdrant Cloud |
| Knowledge graph | Neo4j Aura |
| Embeddings | FastEmbed ONNX (`BAAI/bge-small-en-v1.5`, 384-dim) |
| Inference | Groq Cloud, with local Ollama fallback |
| Rate limiting & budgets | Redis |
| Email | Resend |
| Telemetry | OpenTelemetry → Grafana Cloud |
| Infrastructure | Terraform → Render, Cloudflare, Grafana Cloud |

Embeddings run locally rather than through an API. A 384-dimension ONNX model
is small enough to run in-process, which removes a network hop from the
retrieval path and means no draft text is sent to a third party for embedding.

## Where to go next

- [Quickstart](/guide/quickstart) — get it running.
- [System overview](/architecture/overview) — how the pieces fit.
- [Flows](/flows/overview) — follow a request end to end.
- [Security model](/security/model) — trust boundaries and how they are enforced.
