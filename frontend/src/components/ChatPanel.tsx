import {
  useEffect,
  useState,
} from "react";
import type {
  FormEvent,
} from "react";

import {
  sendMessage,
} from "../api/client";
import type {
  SourceCitation,
} from "../api/types";
import {
  MessageBubble,
} from "./MessageBubble";

interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  sources?: SourceCitation[];
}

interface Props {
  conversationId: string | null;
  initialMessages?: ChatMessage[];
  onSourceClick: (
    source: SourceCitation,
  ) => void;
}

export function ChatPanel({
  conversationId,
  initialMessages = [],
  onSourceClick,
}: Props) {
  const [
    messages,
    setMessages,
  ] = useState<ChatMessage[]>(
    initialMessages,
  );

  const [
    input,
    setInput,
  ] = useState("");

  const [
    isSending,
    setIsSending,
  ] = useState(false);

  const [
    error,
    setError,
  ] = useState<string | null>(
    null,
  );

  useEffect(() => {
    setMessages(initialMessages);
    setInput("");
    setError(null);
  }, [
    conversationId,
    initialMessages,
  ]);

  async function handleSubmit(
    event: FormEvent<HTMLFormElement>,
  ) {
    event.preventDefault();

    const question = input.trim();

    if (
      !conversationId
      || !question
      || isSending
    ) {
      return;
    }

    const temporaryMessageId =
      crypto.randomUUID();

    const temporaryUserMessage:
      ChatMessage = {
        id: temporaryMessageId,
        role: "user",
        content: question,
      };

    setInput("");
    setError(null);
    setIsSending(true);

    setMessages(
      (current) => [
        ...current,
        temporaryUserMessage,
      ],
    );

    try {
      const response =
        await sendMessage(
          conversationId,
          question,
        );

      const result = response.data;

      setMessages(
        (current) => [
          ...current,
          {
            id:
              result.assistant_message_id
              ?? crypto.randomUUID(),
            role: "assistant",
            content: result.answer,
            sources: result.sources,
          },
        ],
      );
    } catch (err) {
      setMessages(
        (current) =>
          current.filter(
            (message) =>
              message.id
              !== temporaryMessageId,
          ),
      );

      setInput(question);

      setError(
        err instanceof Error
          ? err.message
          : "Message failed.",
      );
    } finally {
      setIsSending(false);
    }
  }

  return (
    <main className="chat-panel">
      <div className="messages">
        {messages.map(
          (message) => (
            <MessageBubble
              key={message.id}
              role={message.role}
              content={message.content}
              sources={message.sources}
              onSourceClick={
                onSourceClick
              }
            />
          ),
        )}

        {isSending && (
          <div className="assistant-message">
            Thinking...
          </div>
        )}
      </div>

      {error && (
        <div className="error-box">
          {error}
        </div>
      )}

      <form
        className="chat-input"
        onSubmit={handleSubmit}
      >
        <textarea
          value={input}
          onChange={(event) =>
            setInput(
              event.target.value,
            )
          }
          placeholder={
            conversationId
              ? "Ask about your documents..."
              : "Select or create a conversation first."
          }
          disabled={
            !conversationId
            || isSending
          }
        />

        <button
          type="submit"
          disabled={
            !conversationId
            || isSending
            || !input.trim()
          }
        >
          Send
        </button>
      </form>
    </main>
  );
}