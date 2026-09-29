import axios from "axios";
import { toast } from "react-toastify";

const firstErrorMessage = (value: unknown): string | undefined => {
  if (typeof value === "string" && value.trim()) {
    return value.trim();
  }

  if (Array.isArray(value)) {
    for (const item of value) {
      const message = firstErrorMessage(item);
      if (message) return message;
    }
    return undefined;
  }

  if (typeof value === "object" && value !== null) {
    const body = value as Record<string, unknown>;
    for (const key of ["detail", "message", "error", "non_field_errors"]) {
      const message = firstErrorMessage(body[key]);
      if (message) return message;
    }

    for (const [field, fieldErrors] of Object.entries(body)) {
      const message = firstErrorMessage(fieldErrors);
      if (message) {
        const label = field.replace(/_/g, " ");
        return `${label}: ${message}`;
      }
    }
  }

  return undefined;
};

export const getApiErrorMessage = (
  error: unknown,
  fallback = "Something went wrong. Please try again.",
): string => {
  if (!axios.isAxiosError(error)) {
    return firstErrorMessage(error) ?? fallback;
  }

  if (!error.response) {
    if (error.code === "ECONNABORTED" || error.code === "ETIMEDOUT") {
      return "The request timed out. Please try again.";
    }
    return "Unable to reach the server. Check your connection and try again.";
  }

  if (error.response.status >= 500) {
    return fallback;
  }

  return firstErrorMessage(error.response.data) ?? fallback;
};

export const notifyApiError = (
  error: unknown,
  fallback?: string,
): void => {
  toast.error(getApiErrorMessage(error, fallback));
};
