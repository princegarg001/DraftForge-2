# Threat model

## Assets

| Asset | Why it matters |
| :--- | :--- |
| Student coursework | Academic work; unpublished and personal |
| Marks and evaluations | Academic record; tampering is academic misconduct |
| Student PII | Names, email addresses, institutional affiliation |
| Service credentials | Supabase service-role key, Groq, Resend, Qdrant, Neo4j |
| Inference budget | Directly convertible to money by an attacker |
| Reference corpus | Curated precedent, the platform's substantive value |

## Adversaries

| Adversary | Capability | Wants |
| :--- | :--- | :--- |
| Curious student | Valid account | Other students' marks, the answer keys |
| Malicious student | Valid account | A higher mark, or to damage a peer's |
| Compromised instructor | Valid elevated account | Alter marks, exfiltrate a cohort |
| External attacker | No account | Any of the above; or free inference |
| Automated scanner | No account | Known vulnerabilities, exposed secrets |

The curious student is the most likely and the easiest to underestimate. They
have a legitimate account, the software is used daily, and the boundaries are
guessable — incrementing an id in a URL is not an advanced technique.

## Threats and mitigations

### Privilege escalation

**Was exploitable.** The sign-up form offered a role dropdown.

| Vector | Mitigation |
| :--- | :--- |
| `role` in the registration body | Removed; `extra="forbid"` rejects it loudly |
| `user_metadata.role` at provisioning | Only `app_metadata` is trusted; `ADMIN` never implicit |
| Open faculty sign-up | Gated by a hashed, use-limited institution code |
| Role edited in `localStorage` | Role read from the database on every request |

### Horizontal access (peer data)

**Was exploitable, five ways.** See the [security model](/security/model).

| Vector | Mitigation |
| :--- | :--- |
| Guessing an evaluation id | Ownership resolved server-side; 404 on failure |
| Submitting another student's draft | Draft and version ownership both verified |
| Completing another student's roadmap item | Join through `roadmaps` enforced |
| Cross-instructor grade override | Assignment ownership verified |
| Enumerating ids via 403 vs 404 | Uniform 404 |

### Credential attacks

| Vector | Mitigation |
| :--- | :--- |
| Password guessing | 5/min, 30/hr per IP; uniform failure message |
| Account enumeration | Identical response for unknown account and wrong password |
| Invitation token guessing | 256-bit tokens; only hashes stored; rate limited |
| Token replay after logout | Refresh revoked server-side; rotation with reuse detection |
| Algorithm confusion | Permitted algorithm derived from the key, not the header |

### Resource abuse

| Vector | Mitigation |
| :--- | :--- |
| Unbounded inference spend | Per-user request limits **and** a daily token budget |
| Upload flooding | 40/hr, 15 MB cap enforced while streaming |
| Decompression bombs | Ratio and uncompressed-size ceilings on DOCX; page cap on PDF |
| Mail-reputation damage | 200 invitations/hr; 200 per batch |
| Unauthenticated compute | `/documents/classify` now requires auth |

### Data exfiltration

| Vector | Mitigation |
| :--- | :--- |
| Cross-origin credentialed reads | Exact-origin allowlist; the `*.onrender.com` regex is gone |
| Secret in the frontend bundle | CI greps build output; only `VITE_API_URL` is exposed |
| Secrets in logs or traces | Sink-level redaction; collector strips auth headers |
| Secrets in the repository | gitleaks over full history, with project-specific detectors |
| Answer keys via the API | Column-level grants withhold them |

### Tampering

| Vector | Mitigation |
| :--- | :--- |
| Editing a mark | Overrides restricted to the owning instructor, and audited |
| Erasing the evidence | `audit_log` has no `UPDATE`/`DELETE` grant |
| Rewriting a marked draft | `draft_versions` is append-only |
| Altering history | Marks reference an immutable version |

## Accepted risks

Stated rather than omitted:

**Service-role key in the application.** Compromising the backend compromises
all data. Mitigated by the key existing only in the deployment environment, and
by RLS covering every other access path. Migrating repositories to request-
scoped clients would reduce this.

**Tokens in `localStorage`.** An XSS exposes them. Mitigated by a strict CSP and
React's escaping; httpOnly cookies are the real fix.

**Prompt injection via draft content.** A student can put instructions in a
draft the tutor reads. The realistic impact is coaxing the tutor into writing
their clause — a pedagogical failure, not a breach, since the tutor has no
privileged access and cannot alter a mark.

**A compromised instructor account.** Nothing prevents an instructor with valid
credentials from exfiltrating their own cohort. The audit log makes it
attributable after the fact; MFA would reduce the likelihood.

**No MFA.** Supabase supports it; it is not yet enforced. For instructor
accounts, which can alter academic records, this is the most valuable single
addition remaining.

## Not in scope

- Physical security of managed providers
- Denial of service beyond edge and application rate limiting
- Nation-state adversaries
- Supply-chain compromise of pinned dependencies (monitored, not prevented)
