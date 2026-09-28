import { localConnection } from "../api/connection";

export function CloudModeBanner() {
  if (localConnection()) return <div className="cloud-mode-banner"><strong>Local AI connected</strong><p>AI runs on your computer with Ollama. Keep your computer and tunnel running.</p></div>;

  const mode =
    import.meta.env
      .VITE_DEPLOYMENT_MODE;


  if (
    mode
    !== "cloud_infrastructure"
  ) {

    return null;
  }


  return (

    <div className="cloud-mode-banner">

      <strong>Cloud demo</strong>
      <p>Manage your documents here. Full AI chat runs locally with Ollama.</p>

    </div>
  );
}
