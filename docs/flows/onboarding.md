# Onboarding & invitations

This is the flow that replaced open self-registration. It is worth reading in
full before changing anything in it, because several steps exist to close
specific holes rather than to add features.

## Why it changed

The original system let anyone register and **choose their own role** from a
dropdown. Selecting "Faculty" granted reference-corpus upload, cohort analytics
across every student on the platform, and the ability to override any grade.

The fix has two halves. Removing `role` from the request is the obvious one.
The less obvious one: if faculty sign-up had simply stayed open, the hole would
reopen through the front door — the role would no longer come from the request
body, but anyone could still obtain one. So faculty registration is gated by an
institution-issued code, and students do not register at all.

## The flow

```mermaid
sequenceDiagram
    autonumber
    actor T as Instructor
    participant API
    participant DB as Postgres
    participant Q as Background task
    participant R as Resend
    actor S as Student

    rect rgb(238, 242, 255)
        Note over T,DB: 1 · Faculty registration (gated)
        T->>API: POST /auth/register-faculty<br/>{email, password, full_name, registration_code}
        API->>DB: look up SHA-256 of the code
        alt code unknown, exhausted or expired
            API-->>T: 403 "That registration code is not valid."
            Note over API: One message for every rejection,<br/>so the endpoint cannot be used<br/>to probe which codes exist.
        else valid
            API->>DB: create auth user
            API->>DB: create profile with role TEACHER
            Note over API,DB: The role is assigned by the server<br/>because a valid code was presented.<br/>It is never read from the request.
            API->>DB: increment use count, deactivate if exhausted
            API->>DB: audit: role granted, via which code
            API-->>T: 201 + session
        end
    end

    rect rgb(240, 253, 244)
        Note over T,DB: 2 · Build the roster
        T->>API: POST /classes {name, institution, term}
        API->>DB: insert class + generated join code
        API-->>T: 201 class

        T->>API: POST /classes/{id}/invitations<br/>{students: [{email, full_name}, ...]}
        API->>API: confirm the caller owns this class
        loop each student
            API->>DB: upsert roster entry (status INVITED)
            API->>DB: revoke any live invitation for this address
            Note over API,DB: A resend replaces the previous token<br/>rather than adding a second valid one.
            API->>API: generate 256-bit token
            API->>DB: store only SHA-256(token)
            API->>Q: queue the email (holds the raw token in memory only)
        end
        API-->>T: 202 {invited, skipped, failed}
    end

    rect rgb(255, 251, 235)
        Note over Q,S: 3 · Delivery (out of band)
        Q->>R: send rendered message
        Q->>DB: record outcome — metadata only, never the token
        R->>S: invitation email
    end

    rect rgb(253, 242, 248)
        Note over S,DB: 4 · Acceptance
        S->>API: GET /invitations/preview?token=…
        API->>DB: look up by SHA-256(token)
        API-->>S: class name, instructor, the invited address

        S->>API: POST /invitations/accept {token, password, full_name}
        API->>DB: re-validate the token
        Note over API,DB: The email comes from the invitation record,<br/>never the request body — otherwise one<br/>leaked token creates an account against<br/>any address the caller names.
        API->>DB: create auth user (email pre-confirmed)
        API->>DB: create profile with role STUDENT
        API->>DB: enrollment → ACTIVE, invitation → ACCEPTED
        API-->>S: 201 + session
    end
```

## Design decisions

### Only the token hash is stored

An invitation token is a bearer credential: holding one lets you create an
account bound to the invited address. It is treated like a password — the
database stores `SHA-256(token)` and the raw value exists only in the email.

A plain SHA-256 is correct here, unlike for passwords. The token carries 256
bits of entropy from `secrets`, so there is no dictionary to attack and no
reason to pay a slow KDF's cost on every acceptance lookup.

### The outbox stores no template context

The natural design queues the template plus its variables and lets a worker
render later. That cannot be used here: the context would contain the raw
token, which would then sit in a database row, in backups, and in anything that
reads the table — defeating the point of hashing it.

So invitations are rendered in-process and dispatched as a background task, and
the outbox records only delivery metadata. A permanently failed invitation is
therefore **not replayable**, which is the correct behaviour: the instructor
resends, and that mints a fresh token with a fresh expiry.

### Every bad token gives the same error

Unknown, expired, revoked and already-accepted all return:

> This invitation link is no longer valid. Ask your instructor to resend it.

Distinguishing them would let a caller probe which tokens exist. The specific
reason is logged.

### Re-adding a student revives their row

A removed student added back gets their existing enrollment reinstated rather
than a new one. Their drafts, evaluations and submissions stay attached.

### Removal is soft

Removing a student sets the enrollment to `REMOVED` and revokes pending
invitations. Their coursework is course record and is not deleted.

## Invitation states

```mermaid
stateDiagram-v2
    [*] --> PENDING: instructor invites
    PENDING --> ACCEPTED: student sets a password
    PENDING --> REVOKED: instructor revokes,<br/>student removed,<br/>or a resend supersedes it
    PENDING --> EXPIRED: TTL elapses (default 7 days)
    ACCEPTED --> [*]
    REVOKED --> [*]
    EXPIRED --> [*]
```

A partial unique index enforces **at most one `PENDING` invitation per address
per class**, so resending cannot accumulate valid tokens.

## The join code

Each class carries a short human-readable code, for when an invitation email is
filtered or lost. It deliberately omits `0/O` and `1/I/L`, since codes get read
aloud and retyped.

It can be rotated (`POST /classes/{id}/rotate-join-code`), which is the remedy
when a code has been shared beyond the intended cohort.

## Related

- [Authentication](/flows/authentication) — what happens on every later request.
- [Security model](/security/model) — the trust boundaries this flow enforces.
- [Row-level security](/security/row-level-security) — database-layer backstop.
