export interface HealthStatusResponse {
  status: 'healthy' | 'degraded' | string;
  api: 'available' | string;
  database: 'connected' | 'disconnected' | string;
  environment: string;
  version: string;
  timestamp: string;
  database_error?: string | null;
}

export interface ApiClientError {
  message: string;
  status?: number;
}
