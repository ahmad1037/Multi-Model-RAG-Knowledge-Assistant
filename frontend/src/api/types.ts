export interface KnowledgeBase {
  id: string;
  name: string;
  slug: string;
  description: string | null;
}


export interface DocumentItem {
  id: string;
  knowledge_base_id: string;

  original_filename: string;

  media_type: string;

  file_size_bytes: number | null;

  page_count: number | null;

  status: string;

  error_message: string | null;

  created_at: string;
  updated_at: string;
}


export interface Conversation {
  id: string;

  knowledge_base_id: string;

  title: string | null;

  summary: string | null;

  created_at: string;
  updated_at: string;
}


export interface Message {
  id: string;

  role: "user" | "assistant";

  content: string;

  citations: string[];

  model_name: string | null;

  created_at: string;
}


export interface SourceCitation {
  source_id: string;

  evidence_type:
    | "text_chunk"
    | "visual_asset";

  document_id: string;

  document_name: string;

  page_start: number | null;

  page_end: number | null;

  heading: string | null;

  visual_asset_id: string | null;
}


export interface ConversationTurnResponse {
  conversation_id: string;

  user_message_id: string;

  assistant_message_id: string | null;

  standalone_question: string;

  depends_on_history: boolean;

  answerable: boolean;

  answer: string;

  citations: string[];

  sources: SourceCitation[];

  grounding_verified: boolean;

  clarification_needed: boolean;

  clarification_question: string;
}


export interface ProcessingJob {
  id: string;

  document_id: string;

  status: string;

  current_stage: string;

  progress_percent: number;

  error_message: string | null;
}


export interface DocumentUploadResponse {
  document: DocumentItem;

  processing_job: ProcessingJob;
}
