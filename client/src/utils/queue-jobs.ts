import api from "./api";

export type QueueJobStatus<T = unknown> = {
  job_id: string;
  kind: string;
  status: "queued" | "running" | "succeeded" | "failed";
  result?: T;
  error?: string;
};

const delay = (milliseconds: number) =>
  new Promise((resolve) => window.setTimeout(resolve, milliseconds));

export const waitForQueueJob = async <T = unknown>(
  jobId: string,
  timeoutMs = 5 * 60 * 1000,
): Promise<QueueJobStatus<T>> => {
  const deadline = Date.now() + timeoutMs;

  while (Date.now() < deadline) {
    const response = await api.get<QueueJobStatus<T>>(`/jobs/${jobId}/`);
    const job = response.data;

    if (job.status === "succeeded") return job;
    if (job.status === "failed") {
      throw new Error(job.error ?? "The background task failed.");
    }

    await delay(1000);
  }

  throw new Error("The background task is taking longer than expected.");
};
