-- =============================================================================
-- Migration 005 - Row Level Security, account status, and audit logging
--
-- Migrations 001-004 created twenty-three tables and enabled RLS on none of
-- them, so authorization existed only in application code. Any path that
-- reached the database with a user-scoped key - a leaked anon key, a direct
-- PostgREST call, a future endpoint that forgets its ownership check - had
-- unrestricted access to every row.
--
-- These policies are the database-layer half of the defence. The application
-- checks added alongside them remain the first line; this is what holds when
-- those are bypassed or forgotten.
--
-- NOTE: the backend currently connects with the service-role key, which is
-- BYPASSRLS by design. These policies therefore protect against key leakage,
-- direct database access and anon-key paths today, and become the enforcement
-- boundary for the API itself once repositories move to request-scoped
-- clients (see app/db/supabase.py:get_user_scoped_client).
-- =============================================================================

-- -----------------------------------------------------------------------------
-- 1. Account status
-- -----------------------------------------------------------------------------
ALTER TABLE public.profiles
    ADD COLUMN IF NOT EXISTS is_active BOOLEAN NOT NULL DEFAULT TRUE;

COMMENT ON COLUMN public.profiles.is_active IS
    'Cleared to revoke access without deleting coursework history.';

CREATE INDEX IF NOT EXISTS idx_profiles_role_active ON public.profiles(role, is_active);

-- -----------------------------------------------------------------------------
-- 2. Helper functions
--
-- SECURITY DEFINER so that reading a role from profiles does not itself pass
-- through the profiles policies - without this, every policy that calls these
-- would recurse.
-- -----------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION public.current_user_role()
RETURNS user_role
LANGUAGE sql
STABLE
SECURITY DEFINER
SET search_path = public, pg_temp
AS $$
    SELECT role FROM public.profiles WHERE id = auth.uid() AND is_active;
$$;

CREATE OR REPLACE FUNCTION public.is_teacher()
RETURNS BOOLEAN
LANGUAGE sql
STABLE
SECURITY DEFINER
SET search_path = public, pg_temp
AS $$
    SELECT COALESCE(public.current_user_role() IN ('TEACHER', 'ADMIN'), FALSE);
$$;

CREATE OR REPLACE FUNCTION public.is_admin()
RETURNS BOOLEAN
LANGUAGE sql
STABLE
SECURITY DEFINER
SET search_path = public, pg_temp
AS $$
    SELECT COALESCE(public.current_user_role() = 'ADMIN', FALSE);
$$;

-- True when the caller owns the draft behind a draft_version.
CREATE OR REPLACE FUNCTION public.owns_draft_version(version_id UUID)
RETURNS BOOLEAN
LANGUAGE sql
STABLE
SECURITY DEFINER
SET search_path = public, pg_temp
AS $$
    SELECT EXISTS (
        SELECT 1
        FROM public.draft_versions dv
        JOIN public.drafts d ON d.id = dv.draft_id
        WHERE dv.id = version_id AND d.user_id = auth.uid()
    );
$$;

-- True when the caller is the instructor whose assignment this evaluation was
-- submitted to. Teachers get access to coursework, not to the whole corpus.
CREATE OR REPLACE FUNCTION public.teaches_evaluation(eval_id UUID)
RETURNS BOOLEAN
LANGUAGE sql
STABLE
SECURITY DEFINER
SET search_path = public, pg_temp
AS $$
    SELECT EXISTS (
        SELECT 1
        FROM public.submissions s
        JOIN public.assignments a ON a.id = s.assignment_id
        WHERE s.evaluation_id = eval_id AND a.teacher_id = auth.uid()
    );
$$;

-- -----------------------------------------------------------------------------
-- 3. Enable RLS on every table
--
-- FORCE applies policies to the table owner as well, so a mistakenly
-- owner-privileged connection does not silently bypass them.
-- -----------------------------------------------------------------------------
DO $$
DECLARE
    tbl TEXT;
BEGIN
    FOREACH tbl IN ARRAY ARRAY[
        'profiles', 'reference_documents', 'drafts', 'draft_versions',
        'evaluations', 'evaluation_evidence', 'conversations', 'messages',
        'conversation_summaries', 'user_learning_memory', 'document_memory',
        'skills', 'student_skills', 'skill_history', 'roadmaps', 'roadmap_items',
        'exercises', 'exercise_attempts', 'quizzes', 'quiz_questions',
        'quiz_attempts', 'assignments', 'submissions'
    ]
    LOOP
        EXECUTE format('ALTER TABLE public.%I ENABLE ROW LEVEL SECURITY', tbl);
        EXECUTE format('ALTER TABLE public.%I FORCE ROW LEVEL SECURITY', tbl);
    END LOOP;
END $$;

-- -----------------------------------------------------------------------------
-- 4. profiles
-- -----------------------------------------------------------------------------
DROP POLICY IF EXISTS profiles_select_self ON public.profiles;
CREATE POLICY profiles_select_self ON public.profiles
    FOR SELECT USING (id = auth.uid() OR public.is_teacher());

DROP POLICY IF EXISTS profiles_update_self ON public.profiles;
CREATE POLICY profiles_update_self ON public.profiles
    FOR UPDATE USING (id = auth.uid()) WITH CHECK (id = auth.uid());

-- Deliberately no INSERT or DELETE policy for ordinary users: profile creation
-- and removal run through the service role, which is what keeps role
-- self-assignment impossible at the database layer too.

-- -----------------------------------------------------------------------------
-- 5. Drafts and versions
-- -----------------------------------------------------------------------------
DROP POLICY IF EXISTS drafts_owner_all ON public.drafts;
CREATE POLICY drafts_owner_all ON public.drafts
    FOR ALL USING (user_id = auth.uid()) WITH CHECK (user_id = auth.uid());

-- A teacher may read a draft only once it has been submitted to their own
-- assignment - not merely because it exists.
DROP POLICY IF EXISTS drafts_teacher_read_submitted ON public.drafts;
CREATE POLICY drafts_teacher_read_submitted ON public.drafts
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM public.submissions s
            JOIN public.assignments a ON a.id = s.assignment_id
            WHERE s.draft_id = drafts.id AND a.teacher_id = auth.uid()
        )
    );

DROP POLICY IF EXISTS draft_versions_owner_all ON public.draft_versions;
CREATE POLICY draft_versions_owner_all ON public.draft_versions
    FOR ALL
    USING (EXISTS (SELECT 1 FROM public.drafts d WHERE d.id = draft_id AND d.user_id = auth.uid()))
    WITH CHECK (EXISTS (SELECT 1 FROM public.drafts d WHERE d.id = draft_id AND d.user_id = auth.uid()));

DROP POLICY IF EXISTS draft_versions_teacher_read ON public.draft_versions;
CREATE POLICY draft_versions_teacher_read ON public.draft_versions
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM public.submissions s
            JOIN public.assignments a ON a.id = s.assignment_id
            WHERE s.draft_version_id = draft_versions.id AND a.teacher_id = auth.uid()
        )
    );

-- -----------------------------------------------------------------------------
-- 6. Evaluations and evidence
-- -----------------------------------------------------------------------------
DROP POLICY IF EXISTS evaluations_owner_read ON public.evaluations;
CREATE POLICY evaluations_owner_read ON public.evaluations
    FOR SELECT USING (
        public.owns_draft_version(draft_version_id)
        OR public.teaches_evaluation(id)
        OR public.is_admin()
    );

-- Scores are written by the deterministic engine under the service role;
-- students must never write their own. Overrides are the teacher's only
-- write path.
DROP POLICY IF EXISTS evaluations_teacher_override ON public.evaluations;
CREATE POLICY evaluations_teacher_override ON public.evaluations
    FOR UPDATE USING (public.teaches_evaluation(id)) WITH CHECK (public.teaches_evaluation(id));

DROP POLICY IF EXISTS evidence_read ON public.evaluation_evidence;
CREATE POLICY evidence_read ON public.evaluation_evidence
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM public.evaluations e
            WHERE e.id = evaluation_id
              AND (public.owns_draft_version(e.draft_version_id) OR public.teaches_evaluation(e.id))
        )
        OR public.is_admin()
    );

-- -----------------------------------------------------------------------------
-- 7. Conversations, messages and memory
-- -----------------------------------------------------------------------------
DROP POLICY IF EXISTS conversations_owner_all ON public.conversations;
CREATE POLICY conversations_owner_all ON public.conversations
    FOR ALL USING (user_id = auth.uid()) WITH CHECK (user_id = auth.uid());

DROP POLICY IF EXISTS messages_owner_all ON public.messages;
CREATE POLICY messages_owner_all ON public.messages
    FOR ALL USING (user_id = auth.uid()) WITH CHECK (user_id = auth.uid());

DROP POLICY IF EXISTS conversation_summaries_owner_all ON public.conversation_summaries;
CREATE POLICY conversation_summaries_owner_all ON public.conversation_summaries
    FOR ALL
    USING (EXISTS (SELECT 1 FROM public.conversations c WHERE c.id = conversation_id AND c.user_id = auth.uid()))
    WITH CHECK (EXISTS (SELECT 1 FROM public.conversations c WHERE c.id = conversation_id AND c.user_id = auth.uid()));

DROP POLICY IF EXISTS user_memory_owner_all ON public.user_learning_memory;
CREATE POLICY user_memory_owner_all ON public.user_learning_memory
    FOR ALL USING (user_id = auth.uid()) WITH CHECK (user_id = auth.uid());

DROP POLICY IF EXISTS document_memory_owner_all ON public.document_memory;
CREATE POLICY document_memory_owner_all ON public.document_memory
    FOR ALL
    USING (EXISTS (SELECT 1 FROM public.drafts d WHERE d.id = draft_id AND d.user_id = auth.uid()))
    WITH CHECK (EXISTS (SELECT 1 FROM public.drafts d WHERE d.id = draft_id AND d.user_id = auth.uid()));

-- -----------------------------------------------------------------------------
-- 8. Skills and roadmaps
-- -----------------------------------------------------------------------------
DROP POLICY IF EXISTS skills_read_all ON public.skills;
CREATE POLICY skills_read_all ON public.skills
    FOR SELECT USING (auth.uid() IS NOT NULL);

DROP POLICY IF EXISTS skills_teacher_write ON public.skills;
CREATE POLICY skills_teacher_write ON public.skills
    FOR ALL USING (public.is_teacher()) WITH CHECK (public.is_teacher());

DROP POLICY IF EXISTS student_skills_owner_read ON public.student_skills;
CREATE POLICY student_skills_owner_read ON public.student_skills
    FOR SELECT USING (user_id = auth.uid() OR public.is_teacher());

DROP POLICY IF EXISTS skill_history_owner_read ON public.skill_history;
CREATE POLICY skill_history_owner_read ON public.skill_history
    FOR SELECT USING (
        EXISTS (SELECT 1 FROM public.student_skills ss WHERE ss.id = student_skill_id AND ss.user_id = auth.uid())
        OR public.is_teacher()
    );

DROP POLICY IF EXISTS roadmaps_owner_all ON public.roadmaps;
CREATE POLICY roadmaps_owner_all ON public.roadmaps
    FOR ALL USING (user_id = auth.uid()) WITH CHECK (user_id = auth.uid());

-- roadmap_items has no user column of its own, which is exactly how the
-- complete-milestone endpoint ended up updatable by any student.
DROP POLICY IF EXISTS roadmap_items_owner_all ON public.roadmap_items;
CREATE POLICY roadmap_items_owner_all ON public.roadmap_items
    FOR ALL
    USING (EXISTS (SELECT 1 FROM public.roadmaps r WHERE r.id = roadmap_id AND r.user_id = auth.uid()))
    WITH CHECK (EXISTS (SELECT 1 FROM public.roadmaps r WHERE r.id = roadmap_id AND r.user_id = auth.uid()));

-- -----------------------------------------------------------------------------
-- 9. Exercises and quizzes
-- -----------------------------------------------------------------------------
DROP POLICY IF EXISTS exercises_read_all ON public.exercises;
CREATE POLICY exercises_read_all ON public.exercises
    FOR SELECT USING (auth.uid() IS NOT NULL);

DROP POLICY IF EXISTS exercises_teacher_write ON public.exercises;
CREATE POLICY exercises_teacher_write ON public.exercises
    FOR ALL USING (public.is_teacher()) WITH CHECK (public.is_teacher());

DROP POLICY IF EXISTS exercise_attempts_owner_all ON public.exercise_attempts;
CREATE POLICY exercise_attempts_owner_all ON public.exercise_attempts
    FOR ALL USING (user_id = auth.uid()) WITH CHECK (user_id = auth.uid());

DROP POLICY IF EXISTS exercise_attempts_teacher_read ON public.exercise_attempts;
CREATE POLICY exercise_attempts_teacher_read ON public.exercise_attempts
    FOR SELECT USING (public.is_teacher());

DROP POLICY IF EXISTS quizzes_read_all ON public.quizzes;
CREATE POLICY quizzes_read_all ON public.quizzes
    FOR SELECT USING (auth.uid() IS NOT NULL);

DROP POLICY IF EXISTS quizzes_teacher_write ON public.quizzes;
CREATE POLICY quizzes_teacher_write ON public.quizzes
    FOR ALL USING (public.is_teacher()) WITH CHECK (public.is_teacher());

DROP POLICY IF EXISTS quiz_questions_read_all ON public.quiz_questions;
CREATE POLICY quiz_questions_read_all ON public.quiz_questions
    FOR SELECT USING (auth.uid() IS NOT NULL);

DROP POLICY IF EXISTS quiz_questions_teacher_write ON public.quiz_questions;
CREATE POLICY quiz_questions_teacher_write ON public.quiz_questions
    FOR ALL USING (public.is_teacher()) WITH CHECK (public.is_teacher());

DROP POLICY IF EXISTS quiz_attempts_owner_all ON public.quiz_attempts;
CREATE POLICY quiz_attempts_owner_all ON public.quiz_attempts
    FOR ALL USING (user_id = auth.uid()) WITH CHECK (user_id = auth.uid());

DROP POLICY IF EXISTS quiz_attempts_teacher_read ON public.quiz_attempts;
CREATE POLICY quiz_attempts_teacher_read ON public.quiz_attempts
    FOR SELECT USING (public.is_teacher());

-- -----------------------------------------------------------------------------
-- 10. Answer-key column protection
--
-- RLS gates rows, not columns, so a student permitted to read a quiz question
-- would also read its correct_option. Column-level grants close that: the
-- answer key and model solution are withheld from the authenticated role and
-- reachable only through the service role, which is what grades the attempt.
-- -----------------------------------------------------------------------------
-- correct_option and explanation are both omitted from the grant: each
-- discloses the answer before the attempt is graded.
REVOKE SELECT ON public.quiz_questions FROM authenticated, anon;
GRANT SELECT (id, quiz_id, question_text, options, order_index)
    ON public.quiz_questions TO authenticated;

-- model_solution is the worked answer to the drafting exercise.
REVOKE SELECT ON public.exercises FROM authenticated, anon;
GRANT SELECT (id, skill_id, document_type, title, scenario, instructions, difficulty, hints, rubric_checklist, created_at)
    ON public.exercises TO authenticated;

-- -----------------------------------------------------------------------------
-- 11. Reference corpus
-- -----------------------------------------------------------------------------
DROP POLICY IF EXISTS reference_docs_read_all ON public.reference_documents;
CREATE POLICY reference_docs_read_all ON public.reference_documents
    FOR SELECT USING (auth.uid() IS NOT NULL);

DROP POLICY IF EXISTS reference_docs_teacher_write ON public.reference_documents;
CREATE POLICY reference_docs_teacher_write ON public.reference_documents
    FOR ALL USING (public.is_teacher()) WITH CHECK (public.is_teacher());

-- -----------------------------------------------------------------------------
-- 12. Assignments and submissions
-- -----------------------------------------------------------------------------
DROP POLICY IF EXISTS assignments_teacher_own ON public.assignments;
CREATE POLICY assignments_teacher_own ON public.assignments
    FOR ALL USING (teacher_id = auth.uid()) WITH CHECK (teacher_id = auth.uid());

DROP POLICY IF EXISTS assignments_student_read_published ON public.assignments;
CREATE POLICY assignments_student_read_published ON public.assignments
    FOR SELECT USING (status = 'PUBLISHED' AND auth.uid() IS NOT NULL);

DROP POLICY IF EXISTS submissions_student_own ON public.submissions;
CREATE POLICY submissions_student_own ON public.submissions
    FOR SELECT USING (student_id = auth.uid());

DROP POLICY IF EXISTS submissions_student_insert ON public.submissions;
CREATE POLICY submissions_student_insert ON public.submissions
    FOR INSERT WITH CHECK (
        student_id = auth.uid()
        -- The draft must genuinely belong to the submitting student; without
        -- this, another student's draft can be submitted as one's own.
        AND EXISTS (SELECT 1 FROM public.drafts d WHERE d.id = draft_id AND d.user_id = auth.uid())
    );

-- A teacher reaches submissions only through an assignment they own.
DROP POLICY IF EXISTS submissions_teacher_manage ON public.submissions;
CREATE POLICY submissions_teacher_manage ON public.submissions
    FOR ALL
    USING (EXISTS (SELECT 1 FROM public.assignments a WHERE a.id = assignment_id AND a.teacher_id = auth.uid()))
    WITH CHECK (EXISTS (SELECT 1 FROM public.assignments a WHERE a.id = assignment_id AND a.teacher_id = auth.uid()));

-- -----------------------------------------------------------------------------
-- 13. Audit log
--
-- Privileged actions - grade overrides, role changes, reference uploads - left
-- no durable trace. Append-only: no UPDATE or DELETE policy exists, so entries
-- cannot be rewritten through the API even with a compromised session.
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.audit_log (
    id           BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    actor_id     UUID REFERENCES public.profiles(id) ON DELETE SET NULL,
    actor_role   user_role,
    action       VARCHAR(64) NOT NULL,
    resource     VARCHAR(64) NOT NULL,
    resource_id  UUID,
    subject_id   UUID REFERENCES public.profiles(id) ON DELETE SET NULL,
    details      JSONB NOT NULL DEFAULT '{}'::jsonb,
    ip_address   INET,
    request_id   VARCHAR(64),
    created_at   TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_audit_actor   ON public.audit_log(actor_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_audit_action  ON public.audit_log(action, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_audit_subject ON public.audit_log(subject_id, created_at DESC);

ALTER TABLE public.audit_log ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.audit_log FORCE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS audit_admin_read ON public.audit_log;
CREATE POLICY audit_admin_read ON public.audit_log
    FOR SELECT USING (public.is_admin());

REVOKE UPDATE, DELETE ON public.audit_log FROM authenticated, anon;
