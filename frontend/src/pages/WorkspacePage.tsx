import { KnowledgeBaseControls } from "../components/KnowledgeBaseControls";
import {
  useEffect,
  useRef,
  useState,
} from "react";

import {
  createConversation,
  getKnowledgeBases,
} from "../api/client";

import type {
  KnowledgeBase,
  SourceCitation,
} from "../api/types";

import {
  ChatPanel,
} from "../components/ChatPanel";

import {
  SourcePanel,
} from "../components/SourcePanel";

import { CloudModeBanner } from "../components/CloudModeBanner";

import {
  DocumentPanel,
} from "../components/DocumentPanel";

export function WorkspacePage() {

  const initialized = useRef(false);
  const [isManagingKnowledgeBase, setIsManagingKnowledgeBase] = useState(false);

  const [
    knowledgeBases,
    setKnowledgeBases,
  ] = useState<KnowledgeBase[]>([]);


  const [
    knowledgeBaseId,
    setKnowledgeBaseId,
  ] = useState<string | null>(
    null,
  );


  const [
    conversationId,
    setConversationId,
  ] = useState<string | null>(
    null,
  );


  const [
    selectedSource,
    setSelectedSource,
  ] = useState<
    SourceCitation | null
  >(
    null,
  );

  const [
    isCreatingConversation,
    setIsCreatingConversation,
  ] = useState(false);

  const [error, setError] =
    useState<string | null>(null);

    useEffect(() => {

    if (initialized.current) {
      return;
    }

    initialized.current = true;

    async function load() {

      try {
        const response =
          await getKnowledgeBases();

        setKnowledgeBases(response.data);

        const firstKnowledgeBase =
          response.data[0];

        if (firstKnowledgeBase) {
          setKnowledgeBaseId(
            firstKnowledgeBase.id,
          );
          setIsCreatingConversation(true);

          const conversation =
            await createConversation(
              firstKnowledgeBase.id,
            );

          setConversationId(
            conversation.data.id,
          );
        }
      } catch (err) {
        setError(
          err instanceof Error
            ? err.message
            : "Could not initialize the workspace.",
        );
      } finally {
        setIsCreatingConversation(false);
      }
    }


    load();

  }, []);

    async function selectKnowledgeBase(
    nextKnowledgeBaseId: string,
  ) {
    setKnowledgeBaseId(nextKnowledgeBaseId);
    setConversationId(null);
    setSelectedSource(null);
    setError(null);

    if (!nextKnowledgeBaseId) {
      return;
    }

    setIsCreatingConversation(true);

    try {
      const response =
        await createConversation(
          nextKnowledgeBaseId,
        );

      setConversationId(response.data.id);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Conversation creation failed.",
      );
    } finally {
      setIsCreatingConversation(false);
    }
  }

    async function newConversation() {

    if (!knowledgeBaseId) {
      return;
    }


    setIsCreatingConversation(true);
    setError(null);

    try {
      const response =
        await createConversation(
          knowledgeBaseId,
        );

      setConversationId(response.data.id);
      setSelectedSource(null);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Conversation creation failed.",
      );
    } finally {
      setIsCreatingConversation(false);
    }
  }
    return (
    <div className="workspace">


      <aside className="sidebar">

        <div className="brand-mark">MR</div>

        <div className="brand-copy">
          <h1>Multimodal RAG</h1>
          <p>Knowledge workspace</p>
        </div>

        <CloudModeBanner />

        {error && (
          <div className="workspace-error" role="alert">
            {error}
          </div>
        )}

        <label htmlFor="knowledge-base">
          Knowledge base
        </label>


        <select
          id="knowledge-base"
          disabled={isCreatingConversation || isManagingKnowledgeBase}
          value={
            knowledgeBaseId ?? ""
          }

          onChange={(event) => {
            void selectKnowledgeBase(
              event.target.value,
            );
          }}
        >

          {knowledgeBases.length === 0 && <option value="">Create a knowledge base to begin</option>}
          {knowledgeBases.map(
            (kb) => (

              <option
                key={kb.id}
                value={kb.id}
              >

                {kb.name}

              </option>
            ),
          )}

        </select>


        <KnowledgeBaseControls
          key={knowledgeBaseId ?? "empty"}
          selected={knowledgeBases.find(kb => kb.id === knowledgeBaseId)}
          disabled={isCreatingConversation}
          onBusyChange={setIsManagingKnowledgeBase}
          onCreated={async kb => {
            setKnowledgeBases(current => [kb, ...current]);
            await selectKnowledgeBase(kb.id);
          }}
          onDeleted={async id => {
            const remaining = knowledgeBases.filter(kb => kb.id !== id);
            setKnowledgeBases(remaining);
            await selectKnowledgeBase(remaining[0]?.id ?? "");
          }}
        />

        <button
          onClick={
            newConversation
          }

          disabled={
            !knowledgeBaseId
            || isCreatingConversation
            || isManagingKnowledgeBase
          }
        >

          {isCreatingConversation
            ? "Starting..."
            : "+ New conversation"}

        </button>

        <DocumentPanel
          knowledgeBaseId={knowledgeBaseId || null}
        />

      </aside>



      <ChatPanel

        conversationId={
          conversationId
        }

        onSourceClick={
          setSelectedSource
        }

      />


      <SourcePanel

        source={
          selectedSource
        }

      />

    </div>
  );
}
