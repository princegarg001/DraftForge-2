import axios from 'axios';
import {
  AuthResponse,
  ReferenceDocument,
  DocumentClassificationResult,
  Draft,
  DraftVersion,
  VersionCompareResponse,
  Evaluation,
  LoopholeReport,
  Conversation,
  ChatMessage,
  ChatTurnResponse,
  StudentSkill,
  Roadmap,
  RoadmapItem,
  Quiz,
  QuizAttemptResponse,
  StudentProgress,
  LeaderboardResponse,
  Assignment,
  Submission,
  CohortAnalytics,
  AssistDraftingResponse,
  ExplainEvaluationResponse,
  RAGQueryResponse,
  HealthCheckResponse,
  AuthenticatedUser,
  InvitationPreview,
  ClassRoom,
  Enrollment,
  PendingInvitation,
  BulkInviteResponse,
  InviteOutcome,
} from '../types';

const getBaseUrl = (): string => {
  let envUrl = import.meta.env.VITE_API_URL;
  if (!envUrl || typeof envUrl !== 'string' || !envUrl.trim()) {
    envUrl = import.meta.env.PROD
      ? 'https://draftforge-2-d9mc.onrender.com'
      : 'http://localhost:8000';
  }
  const cleanUrl = envUrl.trim().replace(/\/+$/, '');
  return cleanUrl.endsWith('/api/v1') ? cleanUrl : `${cleanUrl}/api/v1`;
};

export const API_BASE_URL = getBaseUrl();

export const TOKEN_KEY = 'draftforge_token';
export const REFRESH_TOKEN_KEY = 'draftforge_refresh';
export const USER_KEY = 'draftforge_user';

export const getStoredToken = (): string | null => {
  try {
    return localStorage.getItem(TOKEN_KEY);
  } catch {
    // Private browsing and blocked site-data both make storage throw.
    return null;
  }
};

export const storeSession = (accessToken: string, refreshToken: string | null): void => {
  try {
    localStorage.setItem(TOKEN_KEY, accessToken);
    if (refreshToken) localStorage.setItem(REFRESH_TOKEN_KEY, refreshToken);
  } catch {
    /* storage unavailable; the session lives for this page only */
  }
};

export const clearSession = (): void => {
  try {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(REFRESH_TOKEN_KEY);
    localStorage.removeItem(USER_KEY);
  } catch {
    /* nothing to clear */
  }
};

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 60000,
});

apiClient.interceptors.request.use((config) => {
  const token = getStoredToken();
  if (token && config.headers) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Paths where a 401 is an expected outcome rather than an expired session.
// Clearing state and reloading on these would discard the error the form needs
// to display, and bounce the user mid-signup.
const PUBLIC_AUTH_PATHS = ['/auth/login', '/auth/register', '/auth/register-faculty', '/invitations/'];

let isRefreshing = false;
let pendingRefresh: Promise<string | null> | null = null;

async function refreshAccessToken(): Promise<string | null> {
  const refreshToken = localStorage.getItem(REFRESH_TOKEN_KEY);
  if (!refreshToken) return null;
  try {
    // A bare axios call, not apiClient: routing this through the instance
    // would re-enter the interceptor and loop on a failing refresh.
    const response = await axios.post<AuthResponse>(`${API_BASE_URL}/auth/refresh`, {
      refresh_token: refreshToken,
    });
    storeSession(response.data.access_token, response.data.refresh_token ?? null);
    return response.data.access_token;
  } catch {
    return null;
  }
}

apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const original = error.config;
    const status = error.response?.status;
    const url: string = original?.url ?? '';

    const isPublicAuthCall = PUBLIC_AUTH_PATHS.some((path) => url.includes(path));

    if (status === 401 && !isPublicAuthCall && original && !original._retried) {
      original._retried = true;

      // Concurrent 401s share one refresh, so a burst of expired requests does
      // not fire a burst of refresh calls and trip reuse detection.
      if (!isRefreshing) {
        isRefreshing = true;
        pendingRefresh = refreshAccessToken().finally(() => {
          isRefreshing = false;
        });
      }

      const newToken = await pendingRefresh;
      if (newToken) {
        original.headers = { ...original.headers, Authorization: `Bearer ${newToken}` };
        return apiClient(original);
      }

      clearSession();
      window.location.reload();
    }

    return Promise.reject(error);
  }
);

export const api = {
  // Auth
  // No `role` field: the server assigns it. Sending one is rejected outright
  // rather than ignored, so a stale client fails loudly.
  register: (data: { email: string; password: string; full_name: string }) =>
    apiClient.post<AuthResponse>('/auth/register', data),
  registerFaculty: (data: {
    email: string;
    password: string;
    full_name: string;
    registration_code: string;
  }) => apiClient.post<AuthResponse>('/auth/register-faculty', data),
  login: (data: { email: string; password: string }) =>
    apiClient.post<AuthResponse>('/auth/login', data),
  logout: (refresh_token: string) => apiClient.post('/auth/logout', { refresh_token }),
  // Authoritative identity. The frontend must not trust a role cached at
  // login - a role changed or revoked server-side takes effect here.
  getMe: () => apiClient.get<AuthenticatedUser>('/auth/me'),

  // Invitations (unauthenticated)
  previewInvitation: (token: string) =>
    apiClient.get<InvitationPreview>(`/invitations/preview?token=${encodeURIComponent(token)}`),
  acceptInvitation: (data: { token: string; password: string; full_name?: string }) =>
    apiClient.post<AuthResponse>('/invitations/accept', data),

  // Classes & roster (teacher)
  createClass: (data: {
    name: string;
    description?: string;
    institution?: string;
    academic_term?: string;
  }) => apiClient.post<ClassRoom>('/classes', data),
  getMyClasses: (includeArchived = false) =>
    apiClient.get<ClassRoom[]>(`/classes?include_archived=${includeArchived}`),
  getEnrolledClasses: () => apiClient.get<ClassRoom[]>('/classes/enrolled'),
  getClass: (classId: string) => apiClient.get<ClassRoom>(`/classes/${classId}`),
  updateClass: (classId: string, data: Partial<ClassRoom>) =>
    apiClient.patch<ClassRoom>(`/classes/${classId}`, data),
  rotateJoinCode: (classId: string) =>
    apiClient.post<ClassRoom>(`/classes/${classId}/rotate-join-code`),
  getRoster: (classId: string) =>
    apiClient.get<Enrollment[]>(`/classes/${classId}/roster`),
  inviteStudents: (classId: string, students: { email: string; full_name?: string }[]) =>
    apiClient.post<BulkInviteResponse>(`/classes/${classId}/invitations`, { students }),
  getPendingInvitations: (classId: string) =>
    apiClient.get<PendingInvitation[]>(`/classes/${classId}/invitations`),
  resendInvitation: (classId: string, email: string) =>
    apiClient.post<InviteOutcome>(
      `/classes/${classId}/invitations/resend?email=${encodeURIComponent(email)}`
    ),
  revokeInvitation: (classId: string, invitationId: string) =>
    apiClient.delete(`/classes/${classId}/invitations/${invitationId}`),
  removeStudent: (classId: string, enrollmentId: string) =>
    apiClient.delete(`/classes/${classId}/roster/${enrollmentId}`),

  // Reference Documents
  uploadReference: (formData: FormData) =>
    apiClient.post<ReferenceDocument>('/documents/reference/upload', formData),
  getReferences: (docType?: string) =>
    apiClient.get<ReferenceDocument[]>(`/documents/reference${docType ? `?document_type=${docType}` : ''}`),
  classifyText: (text: string) =>
    apiClient.post<DocumentClassificationResult>('/documents/classify', new URLSearchParams({ text })),

  // Drafts
  createDraft: (data: { title: string; raw_content: string; document_type?: string }) =>
    apiClient.post<Draft>('/drafts', data),
  uploadDraftFile: (formData: FormData) =>
    apiClient.post<Draft>('/drafts/upload', formData),
  getDrafts: () =>
    apiClient.get<Draft[]>('/drafts'),
  getDraft: (id: string) =>
    apiClient.get<Draft>(`/drafts/${id}`),
  addDraftVersion: (id: string, content: string) =>
    apiClient.post<DraftVersion>(`/drafts/${id}/versions`, new URLSearchParams({ content })),
  compareVersions: (id: string, v1: number, v2: number) =>
    apiClient.get<VersionCompareResponse>(`/drafts/${id}/compare?v1=${v1}&v2=${v2}`),

  // Evaluations
  evaluateDraft: (draft_id: string, version_number?: number) =>
    apiClient.post<Evaluation>('/evaluations', { draft_id, version_number }),
  getEvaluation: (evaluation_id: string) =>
    apiClient.get<Evaluation>(`/evaluations/${evaluation_id}`),

  // Loopholes (GraphRAG)
  getLoopholes: (evaluation_id: string) =>
    apiClient.get<LoopholeReport>(`/loopholes/${evaluation_id}`),

  // AI Assistance & Tutor
  explainEvaluation: (evaluation_id: string, clause_category?: string, student_query?: string) =>
    apiClient.post<ExplainEvaluationResponse>('/ai/explain-evaluation', { evaluation_id, clause_category, student_query }),
  assistDrafting: (data: { document_type: string; target_clause: string; user_instructions?: string; context_draft_id?: string }) =>
    apiClient.post<AssistDraftingResponse>('/ai/assist-drafting', data),

  // RAG & Evidence Retrieval
  queryEvidence: (data: { query: string; document_type: string; section_hint?: string; top_k?: number }) =>
    apiClient.post<RAGQueryResponse>('/rag/retrieve', data),

  // Chat & Memory
  createConversation: (title?: string) =>
    apiClient.post<Conversation>('/conversations', { title }),
  getConversations: () =>
    apiClient.get<Conversation[]>('/conversations'),
  getMessages: (conversationId: string) =>
    apiClient.get<ChatMessage[]>(`/conversations/${conversationId}/messages`),
  sendChatMessage: (data: { conversation_id: string; message: string; document_type?: string; draft_id?: string; section_hint?: string }) =>
    apiClient.post<ChatTurnResponse>('/chat/send', data),

  // Skills & Roadmaps
  getSkills: () =>
    apiClient.get<StudentSkill[]>('/skills/my-skills'),
  getActiveRoadmap: () =>
    apiClient.get<Roadmap | null>('/roadmap'),
  generateRoadmap: () =>
    apiClient.post<Roadmap>('/roadmap/generate'),
  completeRoadmapItem: (itemId: string) =>
    apiClient.patch<RoadmapItem>(`/roadmap/items/${itemId}/complete`),

  // Quizzes & Practice
  getQuizzes: (docType?: string) =>
    apiClient.get<Quiz[]>(`/quizzes${docType ? `?document_type=${docType}` : ''}`),
  getQuiz: (id: string) =>
    apiClient.get<Quiz>(`/quizzes/${id}`),
  submitQuiz: (data: { quiz_id: string; answers: Record<string, string> }) =>
    apiClient.post<QuizAttemptResponse>('/quizzes/submit', data),

  // Progress & Leaderboard
  getProgress: () =>
    apiClient.get<StudentProgress>('/progress'),
  getLeaderboard: () =>
    apiClient.get<LeaderboardResponse>('/leaderboard'),

  // Teacher Portal & Assignments
  createAssignment: (data: { title: string; description?: string; document_type: string; instructions: string; deadline?: string; rubric_override?: any }) =>
    apiClient.post<Assignment>('/assignments', data),
  getAssignments: (docType?: string) =>
    apiClient.get<Assignment[]>(`/assignments${docType ? `?document_type=${docType}` : ''}`),
  getAssignment: (id: string) =>
    apiClient.get<Assignment>(`/assignments/${id}`),
  getTeacherAssignments: () =>
    apiClient.get<Assignment[]>('/teachers/assignments'),
  getAssignmentSubmissions: (assignmentId: string) =>
    apiClient.get<Submission[]>(`/submissions/assignment/${assignmentId}`),
  submitAssignment: (data: { assignment_id: string; draft_id: string; draft_version_id: string }) =>
    apiClient.post<Submission>('/submissions', data),
  overrideScore: (submissionId: string, data: { overridden_score: number; override_reason: string; teacher_notes?: string }) =>
    apiClient.post<Submission>(`/submissions/${submissionId}/override`, data),
  getCohortAnalytics: (classId?: string) =>
    apiClient.get<CohortAnalytics>(
      `/analytics/cohort${classId ? `?class_id=${encodeURIComponent(classId)}` : ''}`
    ),

  // Health
  checkHealth: () =>
    apiClient.get<HealthCheckResponse>('/health'),
};