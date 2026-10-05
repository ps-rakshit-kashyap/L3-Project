import { HealthStatusResponse } from '@/types/health';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export class ApiService {
  private static baseUrl = API_BASE_URL.replace(/\/$/, '');

  /**
   * Fetches the backend health status from /api/v1/health.
   */
  static async getHealth(): Promise<HealthStatusResponse> {
    const url = `${this.baseUrl}/api/v1/health`;
    
    try {
      const response = await fetch(url, {
        method: 'GET',
        headers: {
          'Accept': 'application/json',
        },
        cache: 'no-store',
      });

      if (!response.ok) {
        throw new Error(`HTTP error ${response.status}: ${response.statusText}`);
      }

      const data: HealthStatusResponse = await response.json();
      return data;
    } catch (err: unknown) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown network error';
      // Return a structured degraded response if network or server is unreachable
      return {
        status: 'unreachable',
        api: 'unavailable',
        database: 'unknown',
        environment: 'unknown',
        version: 'unknown',
        timestamp: new Date().toISOString(),
        database_error: `Failed to connect to ${url}: ${errorMessage}`,
      };
    }
  }

  static getBaseUrl(): string {
    return this.baseUrl;
  }
}
