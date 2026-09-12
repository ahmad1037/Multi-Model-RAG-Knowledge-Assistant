import {
  useEffect,
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

export function WorkspacePage() {

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
    useEffect(() => {

    async function load() {

      const response =
        await getKnowledgeBases();

      setKnowledgeBases(
        response.data,
      );


      if (
        response.data.length > 0
      ) {

        setKnowledgeBaseId(
          response.data[0].id,
        );
      }
    }


    load();

  }, []);
    async function newConversation() {

    if (!knowledgeBaseId) {
      return;
    }


    const response =
      await createConversation(
        knowledgeBaseId,
      );


    setConversationId(
      response.data.id,
    );


    setSelectedSource(
      null,
    );
  }
    return (
    <div className="workspace">

      <aside className="sidebar">

        <h1>
          Multimodal RAG
        </h1>


        <select
          value={
            knowledgeBaseId ?? ""
          }

          onChange={(event) => {

            setKnowledgeBaseId(
              event.target.value,
            );

            setConversationId(
              null,
            );

          }}
        >

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


        <button
          onClick={
            newConversation
          }

          disabled={
            !knowledgeBaseId
          }
        >

          + New conversation

        </button>

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