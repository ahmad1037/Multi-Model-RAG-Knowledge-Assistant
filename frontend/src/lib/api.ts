const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ??
  "http://localhost:8000/api/v1";


export type HealthResponse = {
  status: string;
  service: string;
};


export async function getBackendHealth(): Promise<HealthResponse> {
  const response = await fetch(
    `${API_BASE_URL}/health/live`
  );

  if (!response.ok) {
    throw new Error(
      "Backend health check failed"
    );
  }

  return response.json();
}