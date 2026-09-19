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

      Cloud infrastructure demo.
      Full Ollama multimodal chat
      runs locally.

    </div>
  );
}