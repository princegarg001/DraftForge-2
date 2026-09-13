export type UserRole = 'STUDENT' | 'TEACHER' | 'ADMIN';

export type DocumentType = 
  | 'AFFIDAVIT_OF_CHARACTER'
  | 'EMPLOYMENT_AGREEMENT'
  | 'RENT_AGREEMENT'
  | 'LEGAL_NOTICE';

export interface UserProfile {
  id: string;
  email: string;
  role: UserRole;
  full_name: string | null;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  expires_in?: number | null;
  refresh_token?: string | null;
  user_id: string;
  email: string;
  role: UserRole;
  full_name: string | null;
}

/** Server-resolved identity from /auth/me. Never carries tokens. */
export interface AuthenticatedUser {
  user_id: string;
  email: string;
  role: UserRole;
  full_name: string | null;
  is_active: boolean;
}

// ---------------------------------------------------------------------------
// Classes, rosters and invitations
// ---------------------------------------------------------------------------

export interface ClassRoom {
  id: string;
  teacher_id: string;
  name: string;
  description: string | null;
  institution: string | null;
  academic_term: string | null;
  join_code: string | null;
  is_archived: boolean;
  student_count: number;
  created_at: string | null;
}

export type EnrollmentStatus = 'INVITED' | 'ACTIVE' | 'REMOVED';

export interface Enrollment {
  id: string;
  class_id: string;
  student_id: string | null;
  email: string;
  full_name: string | null;
  status: EnrollmentStatus;
  invited_at: string | null;
  joined_at: string | null;
}

export interface PendingInvitation {
  id: string;
  email: string;
  status: string;
  expires_at: string | null;
  send_count: number;
  created_at: string | null;
}

export interface InviteOutcome {
  email: string;
  status: 'invited' | 'already_enrolled' | 'resent' | 'failed';
  detail: string | null;
}

export interface BulkInviteResponse {
  class_id: string;
  total_submitted: number;
  invited: number;
  skipped: number;
  failed: number;
  results: InviteOutcome[];
}

/**
 * Shown on the acceptance page before a password is set. Deliberately minimal -
 * it does not reveal whether an account already exists for the address.
 */
export interface InvitationPreview {
  email: string;
  class_name: string;
  institution: string | null;
  teacher_name: string | null;
  full_name: string | null;
  expires_at: string | null;
}

export interface ReferenceDocument {
  id: string;
  title: string;
  document_type: DocumentType;
  jurisdiction: string;
  storage_path: string;
  file_size_bytes: number;
  file_hash: string;
  mime_type: string;
  uploaded_by?: string | null;
  created_at: string;
}

export interface DocumentClassificationResult {
  detected_type: DocumentType;
  confidence: number;
  summary: string;
}

export interface DraftVersion {
  id: string;
  draft_id: string;
  version_number: number;
  raw_content: string;
  storage_path?: string | null;
  file_hash?: string | null;
  created_at: string;
}

export interface Draft {
  id: string;
  user_id: string;
  document_type: DocumentType;
  title: string;
  status: string;
  created_at: string;
  updated_at: string;
  versions: DraftVersion[];
}

export interface VersionCompareResponse {
  draft_id: string;
  v1_number: number;
  v2_number: number;
  additions: number;
  deletions: number;
  diff_summary: string;
}

export interface EvaluationFinding {
  id?: string;
  category: string;
  criterion: string;
  status: 'PASS' | 'PARTIAL' | 'FAIL' | 'WARNING';
  score: number;
  max_score: number;
  student_evidence: string | null;
  reference_evidence: string | null;
  source_document: string | null;
  source_page: number | null;
  source_section: string | null;
  explanation: string;
}

export interface Evaluation {
  id: string;
  draft_version_id: string;
  overall_score: number;
  max_score: number;
  structure_score: number;
  clause_score: number;
  formatting_score: number;
  gap_penalty: number;
  rubric_version: string;
  llm_explanation: string | null;
  is_overridden: boolean;
  overridden_score: number | null;
  created_at: string;
  evidence_items: EvaluationFinding[];
}

export interface LoopholeFinding {
  finding_id: string;
  title: string;
  severity: 'HIGH' | 'MEDIUM' | 'LOW';
  gap_type: string;
  related_clause_id?: string | null;
  related_clause_name: string | null;
  prerequisite_clause_id?: string | null;
  prerequisite_clause_name: string | null;
  risk_name: string | null;
  skill_id?: string | null;
  skill_name: string | null;
  educational_observation: string;
  reference_recommendation: string;
}

export interface LoopholeReport {
  evaluation_id: string;
  document_type: string;
  total_loopholes: number;
  high_severity_count: number;
  loopholes: LoopholeFinding[];
}

export interface Conversation {
  id: string;
  user_id: string;
  title: string;
  created_at: string;
  updated_at: string;
  summary: string | null;
}

export interface ChatMessage {
  id: string;
  conversation_id: string;
  user_id?: string;
  role: 'user' | 'assistant';
  content: string;
  model?: string;
  retrieved_sources?: Array<{
    source_document: string;
    section: string;
    page_number?: number;
    content?: string;
  }>;
  created_at: string;
}

export interface ChatTurnResponse {
  user_message: ChatMessage;
  ai_message: ChatMessage;
}

export interface SkillDetail {
  id: string;
  name: string;
  category: string;
  description?: string | null;
}

export interface StudentSkill {
  id: string;
  user_id: string;
  skill_id: string;
  proficiency_score: number;
  confidence_level: number;
  updated_at: string;
  skill: SkillDetail;
}

export interface RoadmapItem {
  id: string;
  roadmap_id: string;
  phase_number: number;
  title: string;
  description: string | null;
  skill_id?: string | null;
  is_completed: boolean;
  completed_at?: string | null;
}

export interface Roadmap {
  id: string;
  user_id: string;
  title: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  roadmap_items: RoadmapItem[];
}

export interface QuizOption {
  key: string;
  text: string;
}

export interface QuizQuestion {
  id: string;
  quiz_id: string;
  question_text: string;
  options: QuizOption[];
  order_index: number;
}

export interface Quiz {
  id: string;
  skill_id?: string | null;
  document_type: DocumentType;
  title: string;
  description?: string | null;
  difficulty: string;
  created_at: string;
  questions?: QuizQuestion[];
}

export interface QuizAttemptResponse {
  id: string;
  quiz_id: string;
  user_id: string;
  score: number;
  total_questions: number;
  passed: boolean;
  breakdown: Array<{
    question_id: string;
    user_answer?: string;
    correct_answer: string;
    is_correct: boolean;
    explanation: string;
  }>;
  created_at: string;
}

export interface StudentProgress {
  user_id: string;
  total_evaluations: number;
  average_score: number;
  score_history: number[];
  document_type_averages: Record<string, number>;
  mastered_skills_count: number;
  weak_skills_count: number;
}

export interface LeaderboardEntry {
  user_id: string;
  full_name: string;
  evaluations_completed: number;
  average_score: number;
}

export interface LeaderboardResponse {
  entries: LeaderboardEntry[];
}

export interface Assignment {
  id: string;
  teacher_id: string;
  title: string;
  description?: string | null;
  document_type: DocumentType;
  instructions: string;
  deadline?: string | null;
  status: string;
  submissions_count?: number;
  created_at: string;
  updated_at: string;
  rubric_override?: Record<string, any> | null;
}

export interface Submission {
  id: string;
  assignment_id: string;
  student_id: string;
  draft_id: string;
  draft_version_id: string;
  evaluation_id?: string | null;
  status: string;
  final_score?: number | null;
  teacher_notes?: string | null;
  submitted_at: string;
  student_name?: string | null;
  student_email?: string | null;
  evaluation?: Evaluation;
}

export interface WeakSkillStat {
  skill_name: string;
  average_proficiency: number;
  struggling_students_count: number;
}

export interface CohortAnalytics {
  total_students: number;
  total_evaluations: number;
  cohort_average_score: number;
  weak_skills_distribution: WeakSkillStat[];
}

export interface AssistDraftingResponse {
  document_type: string;
  target_clause: string;
  generated_draft?: string | null;
  drafted_clause?: string | null;
  commentary?: string | null;
}

export interface ExplainEvaluationResponse {
  evaluation_id: string;
  explanation: string;
  remedial_suggestions: string[];
  statutory_context?: string | null;
}

export interface EvidenceChunk {
  chunk_id: string;
  document_id: string;
  document_type: string;
  jurisdiction: string;
  source_document: string;
  section: string;
  clause_id?: string | null;
  page_number: number;
  content: string;
  similarity_score?: number | null;
  rrf_score?: number | null;
}

export interface RAGQueryResponse {
  query: string;
  document_type: string;
  results_count: number;
  evidence: EvidenceChunk[];
  formatted_context: string;
}

export interface ServiceStatus {
  reachable: boolean;
  details: string;
}

export interface HealthCheckResponse {
  status: string;
  app_version: string;
  services: {
    supabase_postgresql?: ServiceStatus;
    qdrant_cloud?: ServiceStatus;
    neo4j_aura?: ServiceStatus;
    [key: string]: ServiceStatus | undefined;
  };
}