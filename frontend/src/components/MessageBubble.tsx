import type {
  SourceCitation,
} from "../api/types";

import {
  CitationChip,
} from "./CitationChip";


interface Props {

  role:
    | "user"
    | "assistant";

  content: string;

  sources?: SourceCitation[];

  onSourceClick?: (
    source: SourceCitation,
  ) => void;
}


export function MessageBubble({
  role,
  content,
  sources = [],
  onSourceClick,
}: Props) {

  return (
    <div
      className={
        role === "user"
          ? "message user-message"
          : "message assistant-message"
      }
    >

      <div className="message-role">

        {role === "user"
          ? "You"
          : "Assistant"}

      </div>


      <div className="message-content">

        {content}

      </div>


      {sources.length > 0 && (

        <div className="citation-list">

          {sources.map(
            (source) => (

              <CitationChip

                key={
                  source.source_id
                }

                source={source}

                onClick={
                  onSourceClick ??
                  (() => {})
                }

              />
            ),
          )}

        </div>
      )}

    </div>
  );
}