import { apiBaseUrl, apiHeaders } from "../api/connection";


export type HealthResponse = {
  status: string;
  service: string;
};


export async function getBackendHealth(): Promise<HealthResponse> {
  const response = await fetch(
    `${apiBaseUrl()}/health/live`, { headers: apiHeaders() }
  );

  if (!response.ok) {
    throw new Error(
      "Backend health check failed"
    );
  }

  return response.json();
}
