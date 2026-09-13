# Coursework & submissions

How an assignment goes from published to graded.

```mermaid
sequenceDiagram
    autonumber
    actor T as Instructor
    participant API
    participant DB as Postgres
    actor S as Student

    rect rgb(238, 242, 255)
        Note over T,DB: Publish
        T->>API: POST /assignments {title, document_type,<br/>instructions, deadline, class_id}
        API->>DB: insert assignment (status PUBLISHED)
        Note over API,DB: Scoped to a class. Students outside it<br/>never see the assignment.
    end

    rect rgb(240, 253, 244)
        Note over S,DB: Submit
        S->>API: GET /assignments
        API->>DB: published assignments for this student's classes
        S->>API: POST /submissions {assignment_id,<br/>draft_id, draft_version_id}
        API->>DB: does this draft belong to this student?
        API->>DB: does this version belong to that draft?
        Note over API,DB: Both checks were absent. A student could<br/>submit another student's draft — and their<br/>evaluation — as their own work.
        API->>DB: reuse or create the evaluation
        API->>DB: insert submission (status EVALUATED)
        API-->>S: 201
    end

    rect rgb(255, 251, 235)
        Note over T,DB: Audit
        T->>API: GET /submissions/assignment/{id}
        API->>DB: does this instructor own the assignment?
        API-->>T: submissions + evaluations + student names
        T->>API: POST /submissions/{id}/override<br/>{overridden_score, reason, notes}
        API->>DB: does this instructor own the parent assignment?
        Note over API,DB: Role alone was the only gate here, so any<br/>teacher could rewrite any grade in the system.
        API->>DB: set override, status GRADED_OVERRIDDEN
        API->>DB: audit: who, what changed, why
        API-->>T: 200
    end
```

## Submission states

```mermaid
stateDiagram-v2
    [*] --> SUBMITTED
    SUBMITTED --> EVALUATED: deterministic score attached
    EVALUATED --> REVIEWED_BY_TEACHER: instructor opens it
    EVALUATED --> GRADED_OVERRIDDEN: instructor changes the mark
    REVIEWED_BY_TEACHER --> GRADED_OVERRIDDEN
    GRADED_OVERRIDDEN --> [*]
    EVALUATED --> [*]
```

## Overrides

An override never deletes the machine score. The evaluation keeps
`overall_score` and gains `overridden_score`, `overridden_by` and
`override_reason`. Both marks remain visible, which matters when a student asks
why their score changed.

Every override is written to the audit log with the previous score, the new
score, the stated reason and the subject student. The log is append-only —
migration 005 grants no `UPDATE` or `DELETE` — so a compromised instructor
session cannot rewrite its own history.

## Authorization

| Action | Permitted to |
| :--- | :--- |
| Create an assignment | Instructor, for their own class |
| List published assignments | Students enrolled in that class |
| Submit | The student who owns the draft |
| List submissions | The instructor who owns the assignment |
| Override a score | The instructor who owns the parent assignment |

::: warning Three fixes in this flow
- Submitting accepted `draft_id` on trust — a student could submit another student's work.
- The version was not checked against the draft — an arbitrary version id could be attached to a legitimately owned draft.
- Overriding checked only that the caller was *a* teacher, not that they owned the assignment.
:::

## One submission per student per assignment

Enforced by a unique constraint on `(assignment_id, student_id)`. Resubmitting
means creating a new draft version and submitting that, which keeps the history
of what was actually marked.
