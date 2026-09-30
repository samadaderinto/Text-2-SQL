const configuredApiBaseUrl = import.meta.env.VITE_API_BASE_URL || "http://localhost:8001";

export const API_BASE_URL = configuredApiBaseUrl.includes("://")
  ? configuredApiBaseUrl.replace(/\/$/, "")
  : `https://${configuredApiBaseUrl}`;
