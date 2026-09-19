export function CloudModeBanner() {

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
