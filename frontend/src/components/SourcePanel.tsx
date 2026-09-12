import type {
  SourceCitation,
} from "../api/types";


interface Props {

  source:
    | SourceCitation
    | null;
}


export function SourcePanel({
  source,
}: Props) {

  if (!source) {

    return (
      <aside className="source-panel">

        <h2>Sources</h2>

        <p>
          Click a citation to inspect
          its evidence.
        </p>

      </aside>
    );
  }


  const apiBase =
    import.meta.env
      .VITE_API_BASE_URL ??
    "http://localhost:8000/api/v1";


  return (
    <aside className="source-panel">

      <h2>
        {source.source_id}
      </h2>


      <strong>
        {source.document_name}
      </strong>


      {source.page_start && (

        <p>
          Page:
          {" "}
          {source.page_start}
        </p>
      )}


      {source.heading && (

        <p>
          Section:
          {" "}
          {source.heading}
        </p>
      )}


      <p>
        Type:
        {" "}
        {source.evidence_type}
      </p>


      {source.visual_asset_id && (

        <img

          src={
            `${apiBase}/visual-assets/`
            + `${source.visual_asset_id}`
            + "/content"
          }

          alt="Retrieved visual evidence"

          className="source-image"
        />
      )}

    </aside>
  );
}