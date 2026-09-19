import {
  useEffect,
  useRef,
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

const EMPTY_MESSAGES: ChatMessage[] = [];

interface Props {
  conversationId: string | null;
  initialMessages?: ChatMessage[];
  onSourceClick: (
    source: SourceCitation,
  ) => void;
}

export function ChatPanel({
  conversationId,
  initialMessages = EMPTY_MESSAGES,
  onSourceClick,
}: Props) {
  const cloudInfrastructureMode =
    import.meta.env
      .VITE_DEPLOYMENT_MODE
    === "cloud_infrastructure";
  const activeRequest = useRef<AbortController | null>(null);
  const [verifyGrounding, setVerifyGrounding] = useState(true);
  const [elapsedSeconds, setElapsedSeconds] = useState(0);
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
    activeRequest.current?.abort();
    activeRequest.current = null;
    setIsSending(false);
    setMessages(initialMessages);
    setInput("");
    setError(null);
    return () => {
      activeRequest.current?.abort();
      activeRequest.current = null;
    };
  }, [
    conversationId,
    initialMessages,
  ]);

  useEffect(() => {
    if (!isSending) return;
    const startedAt = Date.now();
    setElapsedSeconds(0);
    const timer = window.setInterval(() => {
      setElapsedSeconds(Math.floor((Date.now() - startedAt) / 1000));
    }, 1000);
    return () => window.clearInterval(timer);
  }, [isSending]);

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

    const controller = new AbortController();
    activeRequest.current = controller;
    const timeout = window.setTimeout(() => controller.abort(
      new DOMException("The answer took too long. The server may still be processing it.", "TimeoutError"),
    ), 360_000);
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
          controller.signal,
          verifyGrounding,
        );

      if (activeRequest.current !== controller) return;

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
      if (activeRequest.current !== controller) return;
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
        controller.signal.aborted
          ? controller.signal.reason?.name === "TimeoutError"
            ? "The answer took too long. The server may still be processing it."
            : "Stopped waiting. The server may still finish this answer."
          : err instanceof Error
          ? err.message
          : "Message failed.",
      );
    } finally {
      window.clearTimeout(timeout);
      if (activeRequest.current === controller) {
        activeRequest.current = null;
        setIsSending(false);
      }
    }
  }

  return (
    <main className="chat-panel">
      <header className="chat-header">
        <h2>Chat with your documents</h2>
        <p>Ask a question and explore the supporting sources.</p>
        <label className="grounding-option">
          <input type="checkbox" checked={verifyGrounding} disabled={isSending}
            onChange={(event) => setVerifyGrounding(event.target.checked)} />
          Verify answer grounding
        </label>
        <small>{verifyGrounding ? "Check the answer against retrieved evidence." : "Skip extra verification for faster answers. Citations are still checked."}</small>
      </header>
      <div className="messages">
        {messages.length === 0 && (
          <div className="chat-empty">
            <h2>What would you like to know?</h2>
            <p>Choose a knowledge base, upload your documents, and ask your first question.</p>
          </div>
        )}
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
          <div className="assistant-message thinking-status" role="status">
            Preparing your answer… {elapsedSeconds}s
            {elapsedSeconds >= 20 && <small>{verifyGrounding ? "Searching documents and verifying the answer..." : "Searching documents and preparing the answer..."}</small>}
          </div>
        )}
      </div>

      {error && (
        <div className="error-box" role="alert">
          {error}
        </div>
      )}

      <form
        className="chat-input"
        onSubmit={handleSubmit}
      >
        <textarea
          aria-label="Your question"
          value={input}
          onChange={(event) =>
            setInput(
              event.target.value,
            )
          }
          placeholder={
            cloudInfrastructureMode

              ? "Full AI chat is available in the local Ollama demo."

              : conversationId

                ? "Ask about your documents..."

                : "Select or create a conversation first."
          }
          disabled={
            !conversationId
            || isSending
          }
        />

        {isSending && (
          <button type="button" onClick={() => activeRequest.current?.abort()}>Stop</button>
        )}
        <button
          type="submit"
          disabled={
            cloudInfrastructureMode
            ||
            !conversationId
            ||
            isSending
            ||
            !input.trim()
          }
        >
          Send
        </button>
      </form>
    </main>
  );
}
