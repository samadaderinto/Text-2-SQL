import axios from "axios";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";
const REPORTING_ENABLED = import.meta.env.VITE_ERROR_REPORTING_ENABLED !== "false";
const MAX_QUEUE_SIZE = 20;

type ClientErrorEvent = {
  level: "error" | "warning";
  event_type: "window_error" | "unhandled_rejection" | "api_error";
  message: string;
  stack?: string;
  route?: string;
  method?: string;
  status_code?: number;
  timestamp: string;
};

const pendingEvents: ClientErrorEvent[] = [];
let flushTimer: number | undefined;

const currentRoute = (): string =>
  window.location.pathname;

const sanitizeText = (value: string): string =>
  value
    .replace(/\b[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}\b/g, "[redacted-email]")
    .replace(
      /\b(password|token|authorization|secret)\b\s*[:=]\s*\S+/gi,
      "$1=[redacted]",
    )
    .slice(0, 4000);

const sanitizeRoute = (value: string): string =>
  value.split(/[?#]/, 1)[0].slice(0, 300);

const flush = async (): Promise<void> => {
  if (flushTimer !== undefined) {
    window.clearTimeout(flushTimer);
    flushTimer = undefined;
  }

  const batch = pendingEvents.splice(0);
  await Promise.all(
    batch.map(async (event) => {
      try {
        await axios.post(`${API_BASE_URL}/logs/client/`, event, {
          timeout: 2500,
          headers: { "Content-Type": "application/json" },
        });
      } catch {
        // Error reporting must not cause further application errors.
      }
    }),
  );
};

export const reportClientError = (
  event: Omit<ClientErrorEvent, "timestamp">,
): void => {
  if (!REPORTING_ENABLED || typeof window === "undefined") return;

  if (pendingEvents.length >= MAX_QUEUE_SIZE) pendingEvents.shift();
  pendingEvents.push({
    ...event,
    message: sanitizeText(event.message),
    stack: event.stack ? sanitizeText(event.stack) : undefined,
    route: sanitizeRoute(event.route ?? currentRoute()),
    timestamp: new Date().toISOString(),
  });

  if (flushTimer === undefined) {
    flushTimer = window.setTimeout(() => void flush(), 500);
  }
};

export const installErrorReporting = (): (() => void) => {
  const onError = (event: ErrorEvent): void => {
    reportClientError({
      level: "error",
      event_type: "window_error",
      message: event.message || "Uncaught browser error",
      stack: event.error instanceof Error ? event.error.stack : undefined,
    });
  };

  const onUnhandledRejection = (event: PromiseRejectionEvent): void => {
    const reason = event.reason;
    reportClientError({
      level: "error",
      event_type: "unhandled_rejection",
      message: reason instanceof Error ? reason.message : String(reason),
      stack: reason instanceof Error ? reason.stack : undefined,
    });
  };

  const flushOnPageHide = (): void => {
    void flush();
  };

  window.addEventListener("error", onError);
  window.addEventListener("unhandledrejection", onUnhandledRejection);
  window.addEventListener("pagehide", flushOnPageHide);

  return () => {
    window.removeEventListener("error", onError);
    window.removeEventListener("unhandledrejection", onUnhandledRejection);
    window.removeEventListener("pagehide", flushOnPageHide);
  };
};
