import type { ApiResponse, HealthCheck, Item } from "@types";

const API_BASE_URL = "/api";

class ApiService {
  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${API_BASE_URL}${endpoint}`;

    const config: RequestInit = {
      headers: {
        "Content-Type": "application/json",
        ...options.headers,
      },
      ...options,
    };

    try {
      const response = await fetch(url, config);

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error("API request failed:", error);
      throw error;
    }
  }

  // Health check endpoint
  async healthCheck(): Promise<HealthCheck> {
    return this.request<HealthCheck>("/health");
  }

  // Get root message
  async getRootMessage(): Promise<ApiResponse> {
    return this.request<ApiResponse>("/");
  }

  // Get item by ID
  async getItem(itemId: number, q?: string): Promise<Item> {
    const params = q ? `?q=${encodeURIComponent(q)}` : "";
    return this.request<Item>(`/items/${itemId}${params}`);
  }
}

export const apiService = new ApiService();
export default apiService;
