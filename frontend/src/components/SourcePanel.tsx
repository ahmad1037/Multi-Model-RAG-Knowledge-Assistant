import { useEffect, useState } from "react";
import { apiBaseUrl, apiHeaders } from "../api/connection";
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
  const [imageUrl, setImageUrl] = useState<string | null>(null);
  useEffect(() => {
    setImageUrl(null);
    if (!source?.visual_asset_id) return;
    const controller = new AbortController();
    let objectUrl: string | undefined;
    void fetch(`${apiBaseUrl()}/visual-assets/${source.visual_asset_id}/content`, {
      headers: apiHeaders(), signal: controller.signal,
    }).then(response => {
      if (!response.ok) throw new Error("Source image unavailable");
      return response.blob();
    }).then(blob => {
      if (controller.signal.aborted) return;
      objectUrl = URL.createObjectURL(blob); setImageUrl(objectUrl);
    }).catch(() => { /* The citation text remains available. */ });
    return () => { controller.abort(); if (objectUrl) URL.revokeObjectURL(objectUrl); };
  }, [source?.visual_asset_id]);

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


      {imageUrl && (

        <img

          src={imageUrl}

          alt="Retrieved visual evidence"

          className="source-image"
        />
      )}

    </aside>
  );
}
