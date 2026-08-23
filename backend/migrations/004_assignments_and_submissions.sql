-- Phase 9 Schema: Assignments, Submissions, and Assignment Enrolments

CREATE TYPE assignment_status AS ENUM ('DRAFT', 'PUBLISHED', 'CLOSED', 'ARCHIVED');
CREATE TYPE submission_status AS ENUM ('SUBMITTED', 'EVALUATED', 'REVIEWED_BY_TEACHER', 'GRADED_OVERRIDDEN');

CREATE TABLE IF NOT EXISTS public.assignments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    teacher_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    document_type doc_type NOT NULL,
    instructions TEXT NOT NULL,
    deadline TIMESTAMPTZ,
    rubric_override JSONB,
    status assignment_status NOT NULL DEFAULT 'PUBLISHED',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.submissions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    assignment_id UUID NOT NULL REFERENCES public.assignments(id) ON DELETE CASCADE,
    student_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
    draft_id UUID NOT NULL REFERENCES public.drafts(id) ON DELETE CASCADE,
    draft_version_id UUID NOT NULL REFERENCES public.draft_versions(id) ON DELETE CASCADE,
    evaluation_id UUID REFERENCES public.evaluations(id) ON DELETE SET NULL,
    status submission_status NOT NULL DEFAULT 'SUBMITTED',
    final_score NUMERIC(5, 2),
    teacher_notes TEXT,
    submitted_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(assignment_id, student_id)
);

CREATE INDEX IF NOT EXISTS idx_assignments_teacher ON public.assignments(teacher_id);
CREATE INDEX IF NOT EXISTS idx_submissions_assignment ON public.submissions(assignment_id);
CREATE INDEX IF NOT EXISTS idx_submissions_student ON public.submissions(student_id);