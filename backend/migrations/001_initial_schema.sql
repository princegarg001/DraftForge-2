-- PostgreSQL / Supabase Initial Schema

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Role Enumeration
CREATE TYPE user_role AS ENUM ('STUDENT', 'TEACHER', 'ADMIN');
CREATE TYPE doc_type AS ENUM ('AFFIDAVIT_OF_CHARACTER', 'EMPLOYMENT_AGREEMENT', 'RENT_AGREEMENT', 'LEGAL_NOTICE');
CREATE TYPE draft_status AS ENUM ('DRAFT', 'SUBMITTED', 'EVALUATED', 'ARCHIVED');
CREATE TYPE finding_category AS ENUM ('STRUCTURE', 'CLAUSE_COVERAGE', 'FORMATTING', 'GAP', 'CONTRADICTION', 'DEPENDENCY');
CREATE TYPE finding_status AS ENUM ('PASS', 'PARTIAL', 'FAIL', 'WARNING');

-- User Profiles Table (Mirrors Supabase Auth UID)
CREATE TABLE IF NOT EXISTS public.profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    email VARCHAR(255) NOT NULL UNIQUE,
    role user_role NOT NULL DEFAULT 'STUDENT',
    full_name VARCHAR(255),
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Master Reference Documents (Uploaded by teachers/admins)
CREATE TABLE IF NOT EXISTS public.reference_documents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title VARCHAR(255) NOT NULL,
    document_type doc_type NOT NULL,
    jurisdiction VARCHAR(64) NOT NULL DEFAULT 'India',
    storage_path TEXT NOT NULL,
    file_size_bytes BIGINT NOT NULL,
    file_hash VARCHAR(64) NOT NULL,
    mime_type VARCHAR(128) NOT NULL,
    uploaded_by UUID REFERENCES public.profiles(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Student Drafts
CREATE TABLE IF NOT EXISTS public.drafts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
    document_type doc_type NOT NULL,
    title VARCHAR(255) NOT NULL,
    status draft_status NOT NULL DEFAULT 'DRAFT',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Draft Versions
CREATE TABLE IF NOT EXISTS public.draft_versions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    draft_id UUID NOT NULL REFERENCES public.drafts(id) ON DELETE CASCADE,
    version_number INTEGER NOT NULL,
    raw_content TEXT NOT NULL,
    storage_path TEXT,
    file_hash VARCHAR(64),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(draft_id, version_number)
);

-- Evaluations
CREATE TABLE IF NOT EXISTS public.evaluations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    draft_version_id UUID NOT NULL REFERENCES public.draft_versions(id) ON DELETE CASCADE,
    overall_score NUMERIC(5, 2) NOT NULL,
    max_score NUMERIC(5, 2) NOT NULL DEFAULT 100.00,
    structure_score NUMERIC(5, 2) NOT NULL,
    clause_score NUMERIC(5, 2) NOT NULL,
    formatting_score NUMERIC(5, 2) NOT NULL,
    gap_penalty NUMERIC(5, 2) NOT NULL DEFAULT 0.00,
    rubric_version VARCHAR(64) NOT NULL,
    llm_explanation TEXT,
    is_overridden BOOLEAN NOT NULL DEFAULT FALSE,
    overridden_score NUMERIC(5, 2),
    overridden_by UUID REFERENCES public.profiles(id),
    override_reason TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Granular Evaluation Evidence Findings
CREATE TABLE IF NOT EXISTS public.evaluation_evidence (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    evaluation_id UUID NOT NULL REFERENCES public.evaluations(id) ON DELETE CASCADE,
    category finding_category NOT NULL,
    criterion VARCHAR(128) NOT NULL,
    status finding_status NOT NULL,
    score NUMERIC(5, 2) NOT NULL,
    max_score NUMERIC(5, 2) NOT NULL,
    student_evidence TEXT,
    reference_evidence TEXT,
    source_document TEXT,
    source_page INTEGER,
    source_section TEXT,
    explanation TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Chat System
CREATE TABLE IF NOT EXISTS public.conversations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL DEFAULT 'Legal Drafting Tutoring',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    conversation_id UUID NOT NULL REFERENCES public.conversations(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
    role VARCHAR(32) NOT NULL,
    content TEXT NOT NULL,
    model VARCHAR(64),
    retrieved_sources JSONB DEFAULT '[]'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Skill Tracking
CREATE TABLE IF NOT EXISTS public.skills (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(128) NOT NULL UNIQUE,
    category VARCHAR(64) NOT NULL,
    description TEXT
);

CREATE TABLE IF NOT EXISTS public.student_skills (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
    skill_id UUID NOT NULL REFERENCES public.skills(id) ON DELETE CASCADE,
    proficiency_score NUMERIC(5, 2) NOT NULL DEFAULT 0.00,
    confidence_level NUMERIC(3, 2) NOT NULL DEFAULT 0.00,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(user_id, skill_id)
);

CREATE TABLE IF NOT EXISTS public.skill_history (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    student_skill_id UUID NOT NULL REFERENCES public.student_skills(id) ON DELETE CASCADE,
    score_delta NUMERIC(5, 2) NOT NULL,
    evaluation_id UUID REFERENCES public.evaluations(id),
    reason TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Learning Roadmaps
CREATE TABLE IF NOT EXISTS public.roadmaps (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.roadmap_items (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    roadmap_id UUID NOT NULL REFERENCES public.roadmaps(id) ON DELETE CASCADE,
    phase_number INTEGER NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    skill_id UUID REFERENCES public.skills(id),
    is_completed BOOLEAN NOT NULL DEFAULT FALSE,
    completed_at TIMESTAMPTZ,
    UNIQUE(roadmap_id, phase_number, title)
);

-- Indexes for performance & relational queries
CREATE INDEX IF NOT EXISTS idx_drafts_user_id ON public.drafts(user_id);
CREATE INDEX IF NOT EXISTS idx_draft_versions_draft_id ON public.draft_versions(draft_id);
CREATE INDEX IF NOT EXISTS idx_evaluations_draft_version_id ON public.evaluations(draft_version_id);
CREATE INDEX IF NOT EXISTS idx_evaluation_evidence_evaluation_id ON public.evaluation_evidence(evaluation_id);
CREATE INDEX IF NOT EXISTS idx_messages_conversation_id ON public.messages(conversation_id);
CREATE INDEX IF NOT EXISTS idx_student_skills_user_id ON public.student_skills(user_id);
CREATE INDEX IF NOT EXISTS idx_roadmap_items_roadmap_id ON public.roadmap_items(roadmap_id);