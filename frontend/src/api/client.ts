import type {
  Conversation,
  ConversationTurnResponse,
  DocumentItem,
  DocumentUploadResponse,
  KnowledgeBase,
  Message,
  ProcessingJob,
} from "./types";

const API_BASE_URL = (
  import.meta.env.VITE_API_BASE_URL ??
  "http://localhost:8000/api/v1"
).replace(/\/$/, "");

export interface ApiResponse<T> {
  data: T;
  requestId: string | null;
}

async function apiRequest<T>(
  path: string,
  options?: RequestInit,
): Promise<ApiResponse<T>> {
  
  const response = await fetch(
    `${API_BASE_URL}${path}`,
    options,
  );

  const requestId = response.headers.get(
    "X-Request-ID",
  );

  if (!response.ok) {
    let message =
      `Request failed: ${response.status}`;

    try {
      const body: {
        detail?: unknown;
      } = await response.json();

      if (body.detail) {
        message =
          typeof body.detail === "string"
            ? body.detail
            : JSON.stringify(body.detail);
      }
    } catch {
      // Keep the default error message.
    }

    throw new Error(
      requestId
        ? `${message} | Request ID: ${requestId}`
        : message,
    );
  }

  const data = (await response.json()) as T;

  return {
    data,
    requestId,
  };
}

export async function getKnowledgeBases() {
  return apiRequest<KnowledgeBase[]>(
    "/knowledge-bases",
  );
}

export async function getDocuments(
  knowledgeBaseId: string,
) {
  return apiRequest<DocumentItem[]>(
    `/knowledge-bases/${knowledgeBaseId}/documents`,
  );
}

export async function createConversation(
  knowledgeBaseId: string,
) {
  return apiRequest<Conversation>(
    `/knowledge-bases/${knowledgeBaseId}/conversations`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        title: null,
      }),
    },
  );
}

export async function getMessages(
  conversationId: string,
) {
  return apiRequest<Message[]>(
    `/conversations/${conversationId}/messages`,
  );
}

export async function sendMessage(
  conversationId: string,
  message: string,
) {
  return apiRequest<ConversationTurnResponse>(
    `/conversations/${conversationId}/messages`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        message,
        verify_grounding: true,
      }),
    },
  );
}

export async function uploadDocument(
  knowledgeBaseId: string,
  file: File,
) {
  const formData = new FormData();

  formData.append(
    "file",
    file,
  );

  return apiRequest<DocumentUploadResponse>(
    `/knowledge-bases/${knowledgeBaseId}/documents`,
    {
      method: "POST",
      body: formData,
    },
  );
}

export async function getProcessingJob(
  jobId: string,
) {
  return apiRequest<ProcessingJob>(
    `/processing-jobs/${jobId}`,
  );
}
