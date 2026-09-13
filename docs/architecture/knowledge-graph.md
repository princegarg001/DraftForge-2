# Knowledge graph

Clause dependency analysis in Neo4j. This is what catches defects that per-clause
checking cannot see.

## The problem it solves

A rubric checks clauses individually. Each may pass in isolation while the
document is still unenforceable, because legal provisions have prerequisites.

An arbitration clause with no governing-law clause is the canonical case: both
statements are individually well-drafted, and the arbitration agreement is
nonetheless difficult to enforce because nothing establishes which law governs
it. No per-clause check can see that — the defect is in the *relationship*.

## Model

```mermaid
flowchart TB
    DT["DocumentType"] -->|REQUIRES| C1["Clause<br/>Governing Law"]
    DT -->|REQUIRES| C2["Clause<br/>Arbitration"]
    DT -->|REQUIRES| C3["Clause<br/>Termination"]

    C2 -->|DEPENDS_ON| C1
    C3 -->|DEPENDS_ON| C4["Clause<br/>Notice Period"]

    C1 -->|GOVERNED_BY| S1["Statute<br/>Indian Contract Act"]
    C2 -->|GOVERNED_BY| S2["Statute<br/>Arbitration & Conciliation Act"]

    C2 -.->|MITIGATES| R1["Risk<br/>Unenforceable dispute resolution"]
    C1 -.->|MITIGATES| R1

    style C1 fill:#eef2ff,stroke:#6366f1
    style C2 fill:#eef2ff,stroke:#6366f1
    style R1 fill:#fef2f2,stroke:#ef4444
```

| Node | Represents |
| :--- | :--- |
| `DocumentType` | One of the four supported types |
| `Clause` | A statutory provision |
| `Statute` | The Act or section governing it |
| `Risk` | A failure mode a clause guards against |
| `Skill` | A drafting competency, linked to progression |

| Relationship | Meaning |
| :--- | :--- |
| `REQUIRES` | This type must contain this clause |
| `DEPENDS_ON` | This clause is ineffective without that one |
| `GOVERNED_BY` | Statutory authority |
| `MITIGATES` | This clause reduces this risk |

## Detection

```mermaid
sequenceDiagram
    autonumber
    participant S as Loophole service
    participant DB as Postgres
    participant N as Neo4j

    S->>DB: load evaluation findings
    S->>S: derive which clauses are present
    S->>N: MATCH (c:Clause)-[:DEPENDS_ON]->(p:Clause)<br/>WHERE c.id IN $present AND NOT p.id IN $present
    N-->>S: unsatisfied prerequisites
    S->>N: MATCH (r:Risk)<-[:MITIGATES]-(c:Clause)<br/>WHERE NOT c.id IN $present
    N-->>S: unmitigated risks
    S->>S: rank by severity
    S-->>DB: report
```

## Severity

| Level | Means | Example |
| :--- | :--- | :--- |
| `CRITICAL` | The document likely fails its purpose | Affidavit with no verification jurat |
| `MAJOR` | A provision is unenforceable or ambiguous | Arbitration without governing law |
| `MINOR` | Below best practice | No severability clause |

Each finding carries remediation guidance naming the statute, so the output is
instructional rather than merely a list of complaints.

## Why a graph

The queries above are two- and three-hop traversals over a sparse,
heterogeneous set of relationships. In SQL each becomes a recursive CTE, and
they stop being readable at the third hop — which is where the interesting
defects live.

The graph is small (hundreds of nodes) and read-mostly. It is not there for
scale; it is there because the query shape fits.

## Seeding

Schema constraints and seed topology are applied at startup by
`initialize_graph_constraints()` and `seed_knowledge_graph()`. Both are
idempotent. Seed content lives in `app/ai/graph/seed_knowledge.py`.
