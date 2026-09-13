-- =============================================================================
-- Migration 006 - Classes, rosters, invitations and the email outbox
--
-- Replaces open self-registration with a teacher-driven roster:
--
--   teacher registers -> creates a class -> adds students by email
--     -> each student is emailed an invitation
--     -> student sets a password and joins
--
-- This is a security change as much as a feature one. Cohort analytics and the
-- leaderboard previously aggregated across *every* student in the database
-- because there was no concept of a class to scope them to.
-- =============================================================================

CREATE TYPE invitation_status AS ENUM ('PENDING', 'ACCEPTED', 'REVOKED', 'EXPIRED');
CREATE TYPE enrollment_status AS ENUM ('INVITED', 'ACTIVE', 'REMOVED');
CREATE TYPE email_status AS ENUM ('QUEUED', 'SENDING', 'SENT', 'FAILED', 'BOUNCED');

-- -----------------------------------------------------------------------------
-- 1. Classes
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.classes (
    id             UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    teacher_id     UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
    name           VARCHAR(160) NOT NULL,
    description    TEXT,
    institution    VARCHAR(160),
    academic_term  VARCHAR(64),
    -- Human-shareable fallback join code, for students whose invite email is
    -- lost or filtered. Rotatable without disturbing the roster.
    join_code      VARCHAR(12) UNIQUE,
    is_archived    BOOLEAN NOT NULL DEFAULT FALSE,
    created_at     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT classes_name_not_blank CHECK (length(trim(name)) > 0)
);

CREATE INDEX IF NOT EXISTS idx_classes_teacher ON public.classes(teacher_id) WHERE NOT is_archived;

-- -----------------------------------------------------------------------------
-- 2. Enrollments
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.class_enrollments (
    id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    class_id    UUID NOT NULL REFERENCES public.classes(id) ON DELETE CASCADE,
    -- Null until the invited student accepts and a profile exists.
    student_id  UUID REFERENCES public.profiles(id) ON DELETE CASCADE,
    -- Retained so an invitation can be tracked before any account exists.
    email       VARCHAR(255) NOT NULL,
    full_name   VARCHAR(255),
    status      enrollment_status NOT NULL DEFAULT 'INVITED',
    invited_by  UUID REFERENCES public.profiles(id) ON DELETE SET NULL,
    invited_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    joined_at   TIMESTAMPTZ,
    CONSTRAINT enrollments_email_lowercase CHECK (email = lower(email))
);

-- One roster entry per email per class, so re-adding a student is an update
-- rather than a silent duplicate.
CREATE UNIQUE INDEX IF NOT EXISTS idx_enrollments_class_email
    ON public.class_enrollments(class_id, email);
CREATE INDEX IF NOT EXISTS idx_enrollments_student ON public.class_enrollments(student_id);

-- -----------------------------------------------------------------------------
-- 3. Invitations
--
-- Only a SHA-256 hash of the token is stored. A database read - a backup, a
-- log, a compromised admin view - must not yield a working invitation link,
-- for the same reason passwords are never stored in the clear.
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.invitations (
    id            UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    class_id      UUID NOT NULL REFERENCES public.classes(id) ON DELETE CASCADE,
    enrollment_id UUID REFERENCES public.class_enrollments(id) ON DELETE CASCADE,
    email         VARCHAR(255) NOT NULL,
    token_hash    CHAR(64) NOT NULL UNIQUE,
    intended_role user_role NOT NULL DEFAULT 'STUDENT',
    status        invitation_status NOT NULL DEFAULT 'PENDING',
    issued_by     UUID REFERENCES public.profiles(id) ON DELETE SET NULL,
    expires_at    TIMESTAMPTZ NOT NULL,
    accepted_at   TIMESTAMPTZ,
    accepted_by   UUID REFERENCES public.profiles(id) ON DELETE SET NULL,
    revoked_at    TIMESTAMPTZ,
    send_count    INTEGER NOT NULL DEFAULT 0,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT invitations_email_lowercase CHECK (email = lower(email)),
    -- An invitation must never confer ADMIN; that is granted deliberately.
    CONSTRAINT invitations_role_not_admin CHECK (intended_role <> 'ADMIN')
);

CREATE INDEX IF NOT EXISTS idx_invitations_token  ON public.invitations(token_hash);
CREATE INDEX IF NOT EXISTS idx_invitations_email  ON public.invitations(lower(email));
-- At most one live invitation per email per class.
CREATE UNIQUE INDEX IF NOT EXISTS idx_invitations_one_pending
    ON public.invitations(class_id, email) WHERE status = 'PENDING';

-- -----------------------------------------------------------------------------
-- 4. Faculty registration codes
--
-- Teacher accounts cannot be self-service, or the role-escalation hole closed
-- in Phase 1 simply reopens through the front door.
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.faculty_registration_codes (
    id           UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    code_hash    CHAR(64) NOT NULL UNIQUE,
    label        VARCHAR(160) NOT NULL,
    institution  VARCHAR(160),
    max_uses     INTEGER NOT NULL DEFAULT 1,
    use_count    INTEGER NOT NULL DEFAULT 0,
    expires_at   TIMESTAMPTZ,
    created_by   UUID REFERENCES public.profiles(id) ON DELETE SET NULL,
    is_active    BOOLEAN NOT NULL DEFAULT TRUE,
    created_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT faculty_codes_uses_within_limit CHECK (use_count <= max_uses)
);

-- -----------------------------------------------------------------------------
-- 5. Email outbox
--
-- Mail is queued here and delivered by a worker rather than sent inline. A
-- provider timeout mid-request would otherwise either stall the teacher's
-- request or lose the invitation entirely, and a partially-failed bulk invite
-- would have no record of which messages actually went out.
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.email_outbox (
    id             UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    recipient      VARCHAR(255) NOT NULL,
    subject        VARCHAR(255) NOT NULL,
    template       VARCHAR(64) NOT NULL,
    -- Template variables. Must never contain the raw invitation token; the
    -- token exists only in the rendered message.
    context        JSONB NOT NULL DEFAULT '{}'::jsonb,
    status         email_status NOT NULL DEFAULT 'QUEUED',
    attempts       INTEGER NOT NULL DEFAULT 0,
    max_attempts   INTEGER NOT NULL DEFAULT 5,
    next_attempt_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    provider_id    VARCHAR(128),
    last_error     TEXT,
    related_type   VARCHAR(64),
    related_id     UUID,
    created_at     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    sent_at        TIMESTAMPTZ
);

-- Drives the worker's claim query: due, not exhausted, oldest first.
CREATE INDEX IF NOT EXISTS idx_outbox_due
    ON public.email_outbox(next_attempt_at)
    WHERE status IN ('QUEUED', 'FAILED');
CREATE INDEX IF NOT EXISTS idx_outbox_related ON public.email_outbox(related_type, related_id);

-- -----------------------------------------------------------------------------
-- 6. Scope existing coursework to a class
-- -----------------------------------------------------------------------------
ALTER TABLE public.assignments
    ADD COLUMN IF NOT EXISTS class_id UUID REFERENCES public.classes(id) ON DELETE CASCADE;

CREATE INDEX IF NOT EXISTS idx_assignments_class ON public.assignments(class_id);

-- -----------------------------------------------------------------------------
-- 7. Membership helpers
-- -----------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION public.teaches_class(target_class_id UUID)
RETURNS BOOLEAN
LANGUAGE sql
STABLE
SECURITY DEFINER
SET search_path = public, pg_temp
AS $$
    SELECT EXISTS (
        SELECT 1 FROM public.classes c
        WHERE c.id = target_class_id AND c.teacher_id = auth.uid()
    );
$$;

CREATE OR REPLACE FUNCTION public.is_enrolled_in(target_class_id UUID)
RETURNS BOOLEAN
LANGUAGE sql
STABLE
SECURITY DEFINER
SET search_path = public, pg_temp
AS $$
    SELECT EXISTS (
        SELECT 1 FROM public.class_enrollments e
        WHERE e.class_id = target_class_id
          AND e.student_id = auth.uid()
          AND e.status = 'ACTIVE'
    );
$$;

-- Classmates, for correctly-scoped leaderboards.
CREATE OR REPLACE FUNCTION public.shares_class_with(other_user_id UUID)
RETURNS BOOLEAN
LANGUAGE sql
STABLE
SECURITY DEFINER
SET search_path = public, pg_temp
AS $$
    SELECT EXISTS (
        SELECT 1
        FROM public.class_enrollments mine
        JOIN public.class_enrollments theirs ON theirs.class_id = mine.class_id
        WHERE mine.student_id = auth.uid()
          AND theirs.student_id = other_user_id
          AND mine.status = 'ACTIVE'
          AND theirs.status = 'ACTIVE'
    );
$$;

-- -----------------------------------------------------------------------------
-- 8. Row level security
-- -----------------------------------------------------------------------------
DO $$
DECLARE
    tbl TEXT;
BEGIN
    FOREACH tbl IN ARRAY ARRAY[
        'classes', 'class_enrollments', 'invitations',
        'faculty_registration_codes', 'email_outbox'
    ]
    LOOP
        EXECUTE format('ALTER TABLE public.%I ENABLE ROW LEVEL SECURITY', tbl);
        EXECUTE format('ALTER TABLE public.%I FORCE ROW LEVEL SECURITY', tbl);
    END LOOP;
END $$;

DROP POLICY IF EXISTS classes_teacher_manage ON public.classes;
CREATE POLICY classes_teacher_manage ON public.classes
    FOR ALL USING (teacher_id = auth.uid()) WITH CHECK (teacher_id = auth.uid());

DROP POLICY IF EXISTS classes_student_read ON public.classes;
CREATE POLICY classes_student_read ON public.classes
    FOR SELECT USING (public.is_enrolled_in(id));

DROP POLICY IF EXISTS enrollments_teacher_manage ON public.class_enrollments;
CREATE POLICY enrollments_teacher_manage ON public.class_enrollments
    FOR ALL USING (public.teaches_class(class_id)) WITH CHECK (public.teaches_class(class_id));

-- A student sees their own roster row, not their classmates' contact details.
DROP POLICY IF EXISTS enrollments_student_read_own ON public.class_enrollments;
CREATE POLICY enrollments_student_read_own ON public.class_enrollments
    FOR SELECT USING (student_id = auth.uid());

-- Invitations are never readable through the API. Acceptance is a token
-- lookup performed by the service role; exposing rows would let a signed-in
-- user enumerate pending invitations and harvest addresses.
DROP POLICY IF EXISTS invitations_teacher_read ON public.invitations;
CREATE POLICY invitations_teacher_read ON public.invitations
    FOR SELECT USING (public.teaches_class(class_id));

-- faculty_registration_codes and email_outbox intentionally carry no policies:
-- with RLS enabled and nothing granted, they are reachable only by the service
-- role. Both hold credential-equivalent or personal data.

-- -----------------------------------------------------------------------------
-- 9. Replace global assignment visibility with class-scoped visibility
-- -----------------------------------------------------------------------------
DROP POLICY IF EXISTS assignments_student_read_published ON public.assignments;
CREATE POLICY assignments_student_read_classmates ON public.assignments
    FOR SELECT USING (
        status = 'PUBLISHED'
        AND (class_id IS NULL OR public.is_enrolled_in(class_id))
    );

COMMENT ON COLUMN public.assignments.class_id IS
    'Null means legacy pre-class coursework, visible to any authenticated student. New assignments must set it.';
