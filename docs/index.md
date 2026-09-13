---
layout: home

hero:
  name: DraftForge
  text: Evidence-grounded legal drafting education
  tagline: Deterministic rubric assessment, separated from generative tutoring — so a score is always traceable to a rule, never to a model's mood.
  actions:
    - theme: brand
      text: Get started
      link: /guide/introduction
    - theme: alt
      text: How it works
      link: /architecture/overview
    - theme: alt
      text: Security model
      link: /security/model

features:
  - title: Deterministic scoring
    details: Grading runs no model inference. The same draft scores identically on every run, and every point is attributable to a named rubric criterion with cited evidence.
  - title: Evidence you can follow
    details: Findings carry the source document, section and page they came from — hybrid vector plus lexical retrieval over an indexed corpus of Indian statutory precedent.
  - title: Prerequisite-aware analysis
    details: A knowledge graph traverses clause dependencies, so an arbitration clause with no governing-law clause is flagged as an enforceability gap rather than passing in isolation.
  - title: Socratic, not substitutive
    details: The AI tutor asks statutory questions instead of rewriting the draft. Students keep the cognitive work that the learning depends on.
  - title: Roster-based onboarding
    details: Instructors build a class and invite students by email. Nobody self-selects a role, and coursework, analytics and leaderboards are scoped to the class.
  - title: Traced end to end
    details: OpenTelemetry spans cover embedding, retrieval, graph traversal, inference and scoring — with token-level cost attribution on every LLM call.
---

## What this documentation covers

| Section | Read it when |
| :--- | :--- |
| [Guide](/guide/introduction) | Running DraftForge locally, or configuring a deployment. |
| [Architecture](/architecture/overview) | Understanding how a subsystem works before changing it. |
| [Flows](/flows/overview) | Tracing a request end to end — onboarding, evaluation, submission. |
| [Security](/security/model) | Reviewing the trust boundaries, or changing anything touching authorization. |
| [Operations](/operations/observability) | Diagnosing production, or shipping a deploy. |
| [Reference](/reference/api) | Looking up an endpoint, a setting, or why a decision was made. |

## The core claim

Most LegalTech tools ask a language model to grade a document. That produces a
score that changes between runs, cannot be justified to a student who disputes
it, and is capable of confidently citing a statute that does not exist.

DraftForge splits the problem in two:

```mermaid
flowchart LR
    Draft["Student draft"] --> Split{" "}

    Split --> Det["<b>Deterministic layer</b><br/>rubric matching · structure checks<br/>clause coverage · gap penalties"]
    Split --> Gen["<b>Generative layer</b><br/>Socratic tutoring · explanation<br/>drafting assistance"]

    Det --> Score["Score<br/><i>reproducible, attributable</i>"]
    Gen --> Teach["Guidance<br/><i>never touches the score</i>"]

    style Det fill:#eef2ff,stroke:#6366f1,stroke-width:2px
    style Gen fill:#f1f5f9,stroke:#94a3b8,stroke-width:2px
    style Score fill:#ecfdf5,stroke:#10b981,stroke-width:2px
    style Teach fill:#fff7ed,stroke:#f59e0b,stroke-width:2px
```

The generative layer never writes to a score. That separation is what makes the
mark defensible: a student disputing a result is shown the criterion, the
evidence and the rule that produced it.
