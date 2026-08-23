-- Phase 7 Schema Extensions: Conversation Summaries, User Memory, Document Memory

CREATE TABLE IF NOT EXISTS public.conversation_summaries (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    conversation_id UUID NOT NULL REFERENCES public.conversations(id) ON DELETE CASCADE,
    summary_text TEXT NOT NULL,
    last_summarized_message_id UUID REFERENCES public.messages(id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(conversation_id)
);

CREATE TABLE IF NOT EXISTS public.user_learning_memory (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
    learning_notes TEXT NOT NULL,
    frequent_mistakes TEXT[] DEFAULT '{}',
    mastered_concepts TEXT[] DEFAULT '{}',
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(user_id)
);

CREATE TABLE IF NOT EXISTS public.document_memory (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    draft_id UUID NOT NULL REFERENCES public.drafts(id) ON DELETE CASCADE,
    document_summary TEXT NOT NULL,
    key_clauses_present TEXT[] DEFAULT '{}',
    identified_gaps TEXT[] DEFAULT '{}',
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(draft_id)
);

CREATE INDEX IF NOT EXISTS idx_messages_user_created ON public.messages(user_id, created_at);
CREATE INDEX IF NOT EXISTS idx_conversations_user ON public.conversations(user_id);