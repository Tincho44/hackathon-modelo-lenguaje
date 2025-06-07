// API Response types
export interface ApiResponse<T = any> {
  data: T;
  message: string;
  status: "success" | "error";
}

// Common component props
export interface BaseComponent {
  className?: string;
  children?: React.ReactNode;
}

// Example types for the FastAPI backend
export interface HealthCheck {
  status: string;
}

export interface Item {
  item_id: number;
  q?: string;
}

// User interface (example)
export interface User {
  id: number;
  name: string;
  email: string;
}
