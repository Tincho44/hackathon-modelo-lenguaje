import { useApi } from "@hooks/useApi";
import { apiService } from "@services/api";
import type { BaseComponent } from "@types";
import React from "react";

interface ApiTestProps extends BaseComponent {}

const ApiTest: React.FC<ApiTestProps> = ({ className = "" }) => {
  const {
    data: rootData,
    loading: rootLoading,
    error: rootError,
  } = useApi(() => apiService.getRootMessage());

  const {
    data: healthData,
    loading: healthLoading,
    error: healthError,
  } = useApi(() => apiService.healthCheck());

  return (
    <div className={`api-test ${className}`}>
      <h2>API Connection Test</h2>

      <div className="api-section">
        <h3>Root Endpoint</h3>
        {rootLoading && <p>Loading...</p>}
        {rootError && <p className="error">Error: {rootError}</p>}
        {rootData && (
          <pre className="api-response">
            {JSON.stringify(rootData, null, 2)}
          </pre>
        )}
      </div>

      <div className="api-section">
        <h3>Health Check</h3>
        {healthLoading && <p>Loading...</p>}
        {healthError && <p className="error">Error: {healthError}</p>}
        {healthData && (
          <pre className="api-response">
            {JSON.stringify(healthData, null, 2)}
          </pre>
        )}
      </div>
    </div>
  );
};

export default ApiTest;
