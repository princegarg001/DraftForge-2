# System overview

## The whole picture

```mermaid
flowchart TB
    subgraph Client["Client · React 18 + Vite"]
        Student["Student workspace"]
        Teacher["Instructor portal"]
        Invite["Invitation acceptance"]
    end

    subgraph Edge["Edge"]
        CF["Cloudflare<br/>WAF · coarse rate limiting"]
    end

    subgraph API["API · FastAPI"]
        MW["Middleware chain<br/>TrustedHost → CORS → headers<br/>→ request context → body limit"]
        Authn["Local JWS verification<br/><i>JWKS cached, no round trip</i>"]
        Authz["Role from database<br/>+ per-resource ownership"]
        RL["Redis limiter<br/>requests · token budgets"]
        Routes["60 endpoints"]
    end

    subgraph Engines["Core engines"]
        Det["<b>Deterministic scorer</b><br/>structure · clauses<br/>formatting · gaps"]
        Rag["<b>Hybrid retrieval</b><br/>FastEmbed → Qdrant<br/>+ lexical, RRF fused"]
        Graph["<b>Graph reasoner</b><br/>clause dependencies<br/>loophole detection"]
        Gen["<b>Generative layer</b><br/>tutor · drafting · explainer"]
    end

    subgraph Data["Persistence"]
        PG[("Supabase Postgres<br/><i>RLS on every table</i>")]
        QD[("Qdrant<br/>reference corpus")]
        NEO[("Neo4j<br/>statutory graph")]
        RD[("Redis")]
        ST[("Supabase Storage")]
    end

    subgraph Obs["Telemetry"]
        OTEL["OTLP collector"]
        GRAF["Grafana Cloud<br/>Tempo · Loki · Prometheus"]
    end

    Client --> CF --> MW --> Authn --> Authz --> RL --> Routes

    Routes --> Det
    Routes --> Gen
    Routes --> Graph
    Det --> Rag
    Rag --> QD
    Graph --> NEO
    Gen -.->|"never writes a score"| Det

    Routes --> PG
    Routes --> ST
    RL --> RD

    API -.-> OTEL --> GRAF
    Engines -.-> OTEL

    style Det fill:#eef2ff,stroke:#6366f1,stroke-width:2px
    style Gen fill:#fff7ed,stroke:#f59e0b,stroke-width:2px
    style Authz fill:#fef2f2,stroke:#ef4444,stroke-width:2px
```

The dotted line from the generative layer to the scorer is the system's central
constraint: it is a prohibition, not a dependency. Nothing in the generative
path can influence a mark.

## Request lifecycle

Every authenticated request passes the same gates, in this order:

```mermaid
sequenceDiagram
    autonumber
    participant C as Client
    participant TH as TrustedHost
    participant CORS as CORS
    participant SH as Security headers
    participant RC as Request context
    participant BL as Body limit
    participant AU as Auth
    participant RL as Rate limiter
    participant H as Handler

    C->>TH: HTTP request
    TH->>TH: Host header in allowlist?
    TH->>CORS: pass
    CORS->>CORS: Origin exactly matches?
    CORS->>SH: pass
    SH->>RC: (headers added on the way out)
    RC->>RC: assign request_id, start timer
    RC->>BL: pass
    BL->>BL: reject oversized body while streaming
    BL->>AU: pass

    AU->>AU: verify JWS locally against cached JWKS
    Note over AU: No network call. The old code<br/>hit Supabase Auth on every request.
    AU->>AU: load profile → role from database
    Note over AU: The token says who. The database<br/>says what they may do.

    AU->>RL: pass
    RL->>RL: sliding window + token budget
    RL->>H: pass
    H->>H: resource-level ownership check
    H-->>C: response + request_id + security headers
```

Two of these gates exist because of specific defects found in the baseline
audit; see the [security model](/security/model).

## Backend layout

```
backend/app/
├── api/v1/           Routers — thin; no business logic
├── core/             Cross-cutting: auth, authz, rate limiting, audit,
│                     file validation, tokens, errors, logging
├── middleware/       Request context, security headers, body limits
├── observability/    Tracing, metrics, span helpers
├── db/
│   ├── repositories/ Data access, one per aggregate
│   ├── supabase.py   Admin and user-scoped clients
│   ├── qdrant.py     Vector store
│   └── neo4j.py      Graph store
├── services/         Business logic; orchestrates repositories and engines
│   ├── email/        Provider-agnostic delivery + outbox
│   └── parsing/      PDF, DOCX, TXT extraction
├── ai/
│   ├── evaluation/   Deterministic scorer, rubric loader, per-type evaluators
│   ├── rag/          Chunking, embedding, retrieval, reranking
│   ├── graph/        Cypher queries, schema, seeding
│   ├── llm/          Provider factory, prompts
│   ├── agents/       Tutor, drafting, roadmap, loophole
│   └── memory/       Conversation and document memory
├── pipelines/        Multi-step orchestration across engines
└── models/           Pydantic schemas (wire) and DB models
```

The rule that keeps this navigable: **routers do no work.** A router validates
input, calls one service method, and returns. Business logic lives in
`services/`, data access in `db/repositories/`, and anything cross-cutting in
`core/`.

## Layer responsibilities

| Layer | Owns | Must not |
| :--- | :--- | :--- |
| Router | HTTP shape, status codes, dependency wiring | Contain business rules or touch repositories |
| Service | Business rules, orchestration, authorization | Know about HTTP |
| Repository | Queries and persistence | Contain business rules |
| Engine (`ai/`) | Pure computation over inputs | Perform I/O beyond its own store |

## Why these data stores

Four stores sounds like a lot. Each answers a question the others cannot:

**Postgres** holds everything relational and is the authority on identity,
ownership and marks. Row-level security makes it the enforcement boundary, not
just the storage layer.

**Qdrant** answers "which passage of the reference corpus is semantically
closest to this clause?" — a question no `WHERE` clause can express.

**Neo4j** answers "does this clause depend on another clause that is missing?"
Clause dependencies form a graph, and traversing one in SQL means recursive CTEs
that become unreadable at the third hop.

**Redis** holds counters that must be atomic across workers and are worthless
after a day: rate-limit windows and daily token budgets. Putting them in
Postgres would mean write amplification on the hot path for data nobody keeps.

## Further reading

- [Evaluation engine](/architecture/evaluation-engine) — how a score is produced.
- [Retrieval](/architecture/retrieval) — chunking, embedding and fusion.
- [Knowledge graph](/architecture/knowledge-graph) — dependency traversal.
- [Data model](/architecture/data-model) — tables and their relationships.
