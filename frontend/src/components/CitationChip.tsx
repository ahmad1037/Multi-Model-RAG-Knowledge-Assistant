import type {
  SourceCitation,
} from "../api/types";


interface Props {

  source: SourceCitation;

  onClick: (
    source: SourceCitation,
  ) => void;
}


export function CitationChip({
  source,
  onClick,
}: Props) {

  return (
    <button
      className="citation-chip"

      onClick={() =>
        onClick(source)
      }
    >
      [{source.source_id}]

      {source.page_start
        ? ` p.${source.page_start}`
        : ""}
    </button>
  );
}